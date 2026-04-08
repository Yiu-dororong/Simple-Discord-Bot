import discord
from discord.ext import commands
from discord import app_commands

from keep_alive import keep_alive
import os
import libsql_client
from dotenv import load_dotenv
import random
## For real situations, please DO NOT hard-code your token and other private information, set it in environment variables instead
TOKEN = 'your discord bot token' 
load_dotenv()
keep_alive()

# Define your bot's prefix
intents = discord.Intents.default()
intents.message_content = True # Enable message content intent
bot = commands.Bot(command_prefix='!', intents=intents)

GUILD_ID = discord.Object(id='your channel id') 

url = os.getenv("TURSO_DATABASE_URL", "")
auth_token = os.getenv("TURSO_AUTH_TOKEN", "")
db = libsql_client.create_client(url=url, auth_token=auth_token)

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')

    try:
        guild = GUILD_ID
        synced = await bot.tree.sync(guild= guild)
        print(f'Synced {len(synced)} commands to guild {guild.id}')
    except Exception as e:
        print(f'Error syncing commands: {e}')
        
    try:
        await db.execute("CREATE TABLE IF NOT EXISTS discord_users (id TEXT PRIMARY KEY, username TEXT, balance INTEGER DEFAULT 0, level INTEGER DEFAULT 0, xp INTEGER DEFAULT 0, count INTEGER DEFAULT 0)")
        await db.execute("CREATE TABLE IF NOT EXISTS gambles (id TEXT PRIMARY KEY, win_rate REAL, deadline INTEGER)")
        await db.execute("CREATE TABLE IF NOT EXISTS bets (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, gamble_id TEXT, amount INTEGER, choice TEXT)")
        print("Database ready!")
    except Exception as e:
        print(f'Error initializing database: {e}')
        
@bot.command()
async def draw(ctx, *args):
    arguments = list(args)
    await ctx.send(f'You get {random.choice(arguments)}')

@bot.command()
async def doro(ctx):
    s = "Do"
    ran = 0
    while ran <= 0.95:
        s += random.choice(["do","ro"])
        ran = random.random()
    s += "ro"
    await ctx.send(s)

@bot.command()
async def lucky(ctx):
    luck= {"大凶 運氣很差":7,
          "凶 運氣差":13,
          "吉 運氣普普":20,
          "小吉 運氣偏好":20,
          "中吉 運氣不錯":13,
          "大吉 運氣很好":7,
          "...沒事發生 平平無奇的一天":20}
    
    msg = random.choices(list(luck.keys()), weights=list(luck.values()), k=1)[0]
    await ctx.send(msg)

from datetime import datetime, timedelta

from datetime import datetime, timedelta

def get_next_nday(n):
    today = datetime.now()
    days_until = (n - today.weekday() + 7) % 7
    next_nday = today + timedelta(days=days_until)
    return next_nday.date().strftime("%m月%d日")

class Menu(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="星期1",
                description=get_next_nday(1),
                emoji="1️⃣"
            ),
            discord.SelectOption(
                label="星期2",
                description=get_next_nday(2),
                emoji="2️⃣"
            ),
            discord.SelectOption(
                label="星期3",
                description=get_next_nday(3),
                emoji="3️⃣"
            ),
            discord.SelectOption(
                label="星期4",
                description=get_next_nday(3),
                emoji="4️⃣"
            ),
            discord.SelectOption(
                label="星期5",
                description=get_next_nday(4),
                emoji="5️⃣"
            )
        ]
        
        super().__init__(placeholder="Which days are you free(can choose more than 1)", min_values=1, max_values=5,options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'{interaction.user.mention} {("+".join(sorted(self.values)).replace("星期",""))} OK ')

class MenuVIew(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Menu())

###############
@bot.tree.command(name="Wanna hang out?", description="Choose which days you are free",guild=GUILD_ID)
async def myMenu(interaction: discord.Interaction):
    await interaction.response.send_message(view=MenuVIew())


@bot.tree.command(name="role", description="Assign new role", guild=GUILD_ID)
async def role(interaction: discord.Interaction, member: discord.Member, role_name: str, role_colour: str):
    """my command description
    Args:
        role_colour(str) : #FFFFFF
    """
    # Restrict to be used by admin only
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Admin only!",ephemeral=True)
    guild = interaction.guild  # Get the server where the command was issued

        # Convert hex color code (e.g., #ff5733) to a discord.Colour object
        if role_colour[0] == "#":
            color = discord.Colour(int(role_colour.lstrip("#"), 16))  # Strip '#' and convert hex to int
        else:
            await interaction.response.send_message("Wrong Format" ,ephemeral=True)

    # Create the new role with the specified color and make it mentionable
    new_role = await guild.create_role(
        #Allow spacing in the role by input _
        name=role_name.replace("_", " "),
        colour=color,
        mentionable=True
    )

    # Assign the new role to the mentioned user
    await member.add_roles(new_role)
    await interaction.response.send_message(f"{member.mention}, now you are{new_role.mention}!")

@bot.tree.command(name="money", description="查看目前的餘額", guild=GUILD_ID)
async def balance(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
        user_id = str(interaction.user.id)
        # Use '?' as a placeholder to prevent SQL injection
        result = await db.execute("SELECT balance, count FROM discord_users WHERE id = ?", [user_id])
        
        if not result.rows:
            await db.execute("INSERT INTO discord_users (id, username, balance) VALUES (?, ?, ?)", [user_id, interaction.user.name, 1000])
            await interaction.followup.send("歡迎！你獲得 1000 的起始餘額。", ephemeral=True)
        else:
            balance = result.rows[0][0]
            count = result.rows[0][1] or 0
            
            if balance <= 0:
                count += 1
                await db.execute("UPDATE discord_users SET balance = 1000, count = ? WHERE id = ?", [count, user_id])
                await interaction.followup.send(f"你的餘額歸零了！已為你復活並重新發放 1000 起始餘額。\n你目前的死亡(破產)次數為：{count}", ephemeral=True)
            else:
                msg = f"你目前的餘額為：{balance}"
                if count > 0:
                    msg += f"\n目前的死亡(破產)次數：{count}"
                await interaction.followup.send(msg, ephemeral=True)
    except Exception as e:
        traceback.print_exc()
        await interaction.followup.send(f"發生錯誤：{e}", ephemeral=True)

from typing import Literal
@bot.tree.command(name="create_gamble", description="建立新賭盤 (管理員限定)", guild=GUILD_ID)
async def create_gamble(interaction: discord.Interaction, 賭盤id: str, 描述: str, 是的機率: float, 時間限制: int = -1):
    """my command description
    Args:
        時間限制(int) : 選填 多少分鐘後截止下注
    """
    await interaction.response.defer()
    if not interaction.user.guild_permissions.administrator:
        return await interaction.followup.send("這不是你能用的", ephemeral=True)
    
    # 處理輸入為百分比的情況 (例如輸入 60 則轉換為 0.6)
    if 是的機率 >= 1:
        是的機率 = 是的機率 / 100.0
        
    if 是的機率 <= 0 or 是的機率 >= 1:
        return await interaction.followup.send("「是的機率」必須大於 0 且小於 1 (例如 0.6 或 60)！", ephemeral=True)

    try:
        # Check if gamble exists
        existing = await db.execute("SELECT id FROM gambles WHERE id = ?", [賭盤id])
        if existing.rows:
            return await interaction.followup.send(f"賭盤 ID `{賭盤id}` 已經存在！", ephemeral=True)
            
        if 時間限制 != -1:
            deadline_ts = int((datetime.now() + timedelta(minutes=時間限制)).timestamp())
        else:
            deadline_ts = None
            
        await db.execute("INSERT INTO gambles (id, win_rate, deadline) VALUES (?, ?, ?)", [賭盤id, 是的機率, deadline_ts])
        
        yes_odds = round(1 / 是的機率, 2)
        no_odds = round(1 / (1 - 是的機率), 2)

        embed = discord.Embed(title=f"🎲 新賭盤已建立: {賭盤id}", description=描述, color=discord.Color.gold())
        embed.add_field(name="賭盤 ID", value=f"`{賭盤id}`", inline=True)
        embed.add_field(name="選項: Yes", value=f"賠率: `{yes_odds}x`", inline=True)
        embed.add_field(name="選項: No", value=f"賠率: `{no_odds}x`", inline=True)
        embed.add_field(name="快速下注指令", value=f"```\n/bet 賭盤id:{賭盤id} 選項:\n```", inline=False)
        if deadline_ts:
            embed.add_field(name="截止時間", value=f"<t:{deadline_ts}:R> (<t:{deadline_ts}:F>)", inline=False)
        embed.set_footer(text="使用 /bet 指令來下注！")
        
        await interaction.followup.send(embed=embed)
    except Exception as e:
        traceback.print_exc()
        await interaction.followup.send(f"發生錯誤：{e}")

@bot.tree.command(name="bet", description="在指定的賭盤下注", guild=GUILD_ID)
async def place_bet(interaction: discord.Interaction, 賭盤id: str, 選項: Literal["Yes", "No"], 金額: int):
    await interaction.response.defer()
    if 金額 <= 0:
        return await interaction.followup.send("下注金額必須大於 0！", ephemeral=True)
        
    user_id = str(interaction.user.id)
    
    try:
        # Check if gamble exists
        gamble = await db.execute("SELECT win_rate, deadline FROM gambles WHERE id = ?", [賭盤id])
        if not gamble.rows:
            return await interaction.followup.send(f"找不到賭盤 `{賭盤id}`！", ephemeral=True)
            
        deadline = gamble.rows[0][1]
        if deadline is not None and int(datetime.now().timestamp()) > deadline:
            return await interaction.followup.send(f"這盤已經在 <t:{deadline}:F> 截止下注了！", ephemeral=True)
            
        # Check user balance
        user_data = await db.execute("SELECT balance FROM discord_users WHERE id = ?", [user_id])
        balance = user_data.rows[0][0] if user_data.rows else 0
        
        if balance < 金額:
            if balance == 0:
                return await interaction.followup.send(f"餘額不足！你目前只有 {balance}。請使用 `/money` 來復活！", ephemeral=True)
            return await interaction.followup.send(f"餘額不足！你目前只有 {balance}。", ephemeral=True)
            
        # Deduct balance and create bet entry
        await db.execute("UPDATE discord_users SET balance = balance - ? WHERE id = ?", [金額, user_id])
        await db.execute("INSERT INTO bets (user_id, gamble_id, amount, choice) VALUES (?, ?, ?, ?)", [user_id, 賭盤id, 金額, 選項])
        
        await interaction.followup.send(f"🎉 成功在 `{賭盤id}` 下注 **{金額}** 於選項 `{選項}`！ (剩餘餘額: {balance - 金額})")
    except Exception as e:
        traceback.print_exc()
        await interaction.followup.send(f"發生錯誤：{e}")

@bot.tree.command(name="gamble_result", description="結算賭盤 (管理員限定)", guild=GUILD_ID)
async def gamble_result(interaction: discord.Interaction, 賭盤id: str, 獲勝選項: Literal["Yes", "No"]):
    await interaction.response.defer()
    if not interaction.user.guild_permissions.administrator:
        return await interaction.followup.send("這不是你能用的", ephemeral=True)
        
    try:
        gamble = await db.execute("SELECT win_rate FROM gambles WHERE id = ?", [賭盤id])
        if not gamble.rows:
            return await interaction.followup.send(f"找不到賭盤 `{賭盤id}`！", ephemeral=True)
            
        prob_yes = float(gamble.rows[0][0])
            
        if 獲勝選項 == "Yes":
            win_rate = 1 / prob_yes
        else:
            win_rate = 1 / (1 - prob_yes)
        
        # Get all winning bets
        winners = await db.execute("SELECT user_id, amount FROM bets WHERE gamble_id = ? AND choice = ?", [賭盤id, 獲勝選項])
        
        payouts = []
        for row in winners.rows:
            uid, amt = row[0], row[1]
            payout = int(amt * win_rate)
            await db.execute("UPDATE discord_users SET balance = balance + ? WHERE id = ?", [payout, uid])
            payouts.append(f"<@{uid}>: 贏得 {payout} (下注 {amt})")
            
        # Clean up all bets for this gamble and the gamble itself
        await db.execute("DELETE FROM bets WHERE gamble_id = ?", [賭盤id])
        await db.execute("DELETE FROM gambles WHERE id = ?", [賭盤id])
        
        embed = discord.Embed(title=f"🎲 `{賭盤id}` 結算！", color=discord.Color.green())
        embed.add_field(name="獲勝選項", value=f"`{獲勝選項}`", inline=False)
        embed.add_field(name="結算賠率", value=f"`{round(win_rate, 2)}x`", inline=False)
        
        winners_text = "\n".join(payouts) if payouts else "沒有人猜中 QQ"
        # Safely truncate if it surpasses embed character limit
        if len(winners_text) > 1024:
            winners_text = winners_text[:1000] + "\n...等多名贏家！"
            
        embed.add_field(name="🎉 贏家列表", value=winners_text, inline=False)
            
        await interaction.followup.send(embed=embed)
    except Exception as e:
        traceback.print_exc()
        await interaction.followup.send(f"發生錯誤：{e}")

bot.run(TOKEN) 


















