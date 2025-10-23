import discord
from discord.ext import commands
from discord import app_commands

from keep_alive import keep_alive

import random

TOKEN = 'your discord bot token' 

keep_alive()

# Define your bot's prefix
intents = discord.Intents.default()
intents.message_content = True # Enable message content intent
bot = commands.Bot(command_prefix='!', intents=intents)

GUILD_ID = discord.Object(id='your channel id') 

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')

    try:
        guild = GUILD_ID
        synced = await bot.tree.sync(guild= guild)
        print(f'Synced {len(synced)} commands to guild {guild.id}')
    except Exception as e:
        print(f'Error syncing commands: {e}')

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

bot.run(TOKEN) 


















