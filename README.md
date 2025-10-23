# Simple Discord Bot

This is a small project that I made for my friends and myself to use. I made a excerpt of the bot (in Python) to here. The bot focuses on enabling small-scaled server to have fun.

# Setup

Everything starts with creating a bot in Discord, this can be done in [here](https://discord.com/developers/docs/intro). I am not going to include a complete guide on it, but you should gain a bot token for it, as well as invite your own bot to your server.

For a bot to be usable, we must host it to make it online. Depending how you host, local or cloud. I personally use [Render](https://render.com/). A free cloud service providing high uptime. Please be reminded that your bot token should set as an environment variable for best measure. Plus, you need to make a txt for host to know what packages are need by:
```
pip freeze > requirements.txt
```
also note that,
```
from keep_alive import keep_alive
```
this is an important line for someone who want to keep the bot online, this is not written by me. You also need to constantly ping it if you are using free hosting that will put your bot offline being idle for so long. It can be done by [UptimeRobot](https://uptimerobot.com/), but there is still a low chance that the bot will go offline.

# Commands

I learn most of them from [James S](https://www.youtube.com/@James_S), he provides videoes to teach the basics which are easy to follow. Alternatively, official [documentation](https://discordpy.readthedocs.io/en/stable/) is also a way to fully understand how the syntax works.

For a command to be *useful*, it really depends on the context, what kind of server are you staying. It can be studying, AI prompting or listening to music, anything you can imagine of.

Let's begin with my favourite doro command:

```
import random
@bot.command()
async def doro(ctx):
    s = "Do"
    ran = 0
    while ran <= 0.95:
        s += random.choice(["do","ro"])
        ran = random.random()
    s += "ro"
    await ctx.send(s)
```

`ctx` means context, which is generally used in prefix command. `async` and `await` are used to put them in sleep when not used. (Note: Warlus operator can be used to further compress the code.)

This command will yields a string of many `do` and `ro`.

```
@bot.command()
async def draw(ctx, *args):
    arguments = list(args)
    await ctx.send(f'You get {random.choice(arguments)}')
```

This is a more useful if someone want to draw one option from multiple options.

Next, this is a "fortune-telling" command.

```
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
```

The chinese simply mean how lucky, and paired with values of probability as a dictionary to be drawn by the random module. I think this is fun as it can connect to daily lifes. 

Now, we move on to slash commands. Suppose I want to make a drop-down menu to let people choose something, like which days are they free to go out.

We first need a function to get the date using datetime module,

```
from datetime import datetime, timedelta

def get_next_nday(n):
    today = datetime.now()
    days_until = (n - today.weekday() + 7) % 7
    next_nday = today + timedelta(days=days_until)
    return next_nday.date().strftime("%m月%d日")
```

and then we will create the menu object,

```
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
```

Now we are ready to go.

```
@bot.tree.command(name="Wanna hang out?", description="Choose which days you are free",guild=GUILD_ID)
async def myMenu(interaction: discord.Interaction):
    await interaction.response.send_message(view=MenuVIew())
```

This will call the menu out for my friends to choose while they can see the exact date, which is better than clicking emotes as reactions. However, this is only suitable for small amount of people. Note that for slash command, we use `interaction` instead of `ctx`, because the format showed up in discord is different. The bot will always reply to you, unlike prefix command which call the bot out to do something.

Last but not least, my friends sometimes do something funny, say like 10 losses in a row, and I want to add a role to them. Here comes a command that can help me.

```
@bot.tree.command(name="role", description="Assign new role", guild=GUILD_ID)
async def role(interaction: discord.Interaction, member: discord.Member, role_name: str, role_colour: str):
    """my command description
    Args:
        role_colour(str) : #FFFFFF
    """
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
```

It takes 3 input variables. Who, what is the role name, what is the colour of the role. We use hex colour code to process, which can be obtained easily by colour picker by Google.

There are still many functions that one can develop, such as chatbot. Here I will show another approach to make the bot run automatically via n8n.

<img width="1164" height="401" alt="image" src="https://github.com/user-attachments/assets/f195b613-a6c9-4ab0-9b97-b53638abaf48" />

Install discord trigger in n8n, and then set the trigger condition you want. This time for example every time I trigger it, it will connect to an AI and generate an interesting fact, a joke or a beautiful image. n8n will retrieve and bring back to the bot and send it through discord.

Please note that there are other objects available like buttons, embeds, modals , but currently I do not need to use them. They can be useful depend on your usage. 
