import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="Echo/", intents=intents)

# Data structure:
# characters = {
#     user_id: {
#         "Name": {"trigger": "Idh:", "avatar": url}
#     }
# }
characters = {}

@bot.event
async def on_ready():
    print(f"Echo online as {bot.user}")

# ---------------- REGISTER ----------------
@bot.command(name="register")
async def register(ctx, name: str, trigger: str):
    if not trigger.endswith(":"):
        return await ctx.send("Trigger must end with a colon, e.g. Idh:")

    attachment = ctx.message.attachments[0] if ctx.message.attachments else None
    avatar_url = attachment.url if attachment else ctx.author.display_avatar.url

    user = ctx.author.id
    characters.setdefault(user, {})
    characters[user][name] = {"trigger": trigger, "avatar": avatar_url}

    embed = discord.Embed(title="Character Registered", color=0x88ccff)
    embed.add_field(name="Name", value=name, inline=False)
    embed.add_field(name="Trigger", value=trigger, inline=False)
    embed.set_thumbnail(url=avatar_url)

    await ctx.send(embed=embed)

# ---------------- RENAME ----------------
@bot.command(name="rename")
async def rename(ctx, old: str, new: str):
    user = ctx.author.id
    if old not in characters.get(user, {}):
        return await ctx.send("Character not found.")

    characters[user][new] = characters[user].pop(old)
    await ctx.send(f"Renamed **{old}** to **{new}**.")

# ---------------- AVATAR ----------------
@bot.command(name="avatar")
async def avatar(ctx, name: str):
    user = ctx.author.id
    if name not in characters.get(user, {}):
        return await ctx.send("Character not found.")

    attachment = ctx.message.attachments[0] if ctx.message.attachments else None
    if not attachment:
        return await ctx.send("Please attach an image.")

    characters[user][name]["avatar"] = attachment.url
    await ctx.send(f"Updated avatar for **{name}**.")

# ---------------- BRACKET / TRIGGER CHANGE ----------------
@bot.command(name="bracket")
async def bracket(ctx, name: str, new_trigger: str):
    if not new_trigger.endswith(":"):
        return await ctx.send("Trigger must end with a colon.")

    user = ctx.author.id
    if name not in characters.get(user, {}):
        return await ctx.send("Character not found.")

    characters[user][name]["trigger"] = new_trigger
    await ctx.send(f"Updated trigger for **{name}** to `{new_trigger}`.")

# ---------------- DELETE ----------------
@bot.command(name="delete")
async def delete(ctx, name: str):
    user = ctx.author.id
    if name not in characters.get(user, {}):
        return await ctx.send("Character not found.")

    del characters[user][name]
    await ctx.send(f"Deleted **{name}**.")

# ---------------- LIST ----------------
@bot.command(name="list")
async def list_characters(ctx):
    user = ctx.author.id
    chars = characters.get(user, {})

    if not chars:
        return await ctx.send("You have no registered characters.")

    embed = discord.Embed(title="Your Characters", color=0x99ddff)
    for name, data in chars.items():
        embed.add_field(name=name, value=f"Trigger: `{data['trigger']}`", inline=False)
    await ctx.send(embed=embed)

# ---------------- SEARCH ----------------
@bot.command(name="search")
async def search(ctx, keyword: str):
    user = ctx.author.id
    matches = []

    for name, data in characters.get(user, {}).items():
        if keyword.lower() in name.lower() or keyword.lower() in data["trigger"].lower():
            matches.append((name, data["trigger"]))

    if not matches:
        return await ctx.send("No matches found.")

    embed = discord.Embed(title=f"Search results for '{keyword}'", color=0xaaddff)
    for name, trig in matches:
        embed.add_field(name=name, value=f"Trigger: `{trig}`", inline=False)
    await ctx.send(embed=embed)

# ---------------- HELP ----------------
@bot.command(name="commands")
async def commands_cmd(ctx):
    embed = discord.Embed(title="Echo Command List", color=0x77bbff)
    embed.add_field(name="Echo/register \"Name\" Trigger:", value="Register a new character (attach image for avatar)", inline=False)
    embed.add_field(name="Echo/rename Old New", value="Rename a character", inline=False)
    embed.add_field(name="Echo/avatar Name", value="Update avatar (attach image)", inline=False)
    embed.add_field(name="Echo/bracket Name NewTrigger:", value="Change trigger (must end with colon)", inline=False)
    embed.add_field(name="Echo/list", value="List your characters", inline=False)
    embed.add_field(name="Echo/search keyword", value="Search characters", inline=False)
    embed.add_field(name="Echo/delete Name", value="Delete a character", inline=False)
    embed.add_field(name="Echo/commands", value="Show this command list", inline=False)
    await ctx.send(embed=embed)

# ---------------- PROXYING ----------------
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content
    triggered = False

    for user_id, user_chars in characters.items():  # check all users
        for name, data in user_chars.items():
            trigger = data["trigger"]
            if content.lower().startswith(trigger.lower()):  # case-insensitive
                proxied = content[len(trigger):].strip()

                # find or create webhook
                webhook = None
                for wh in await message.channel.webhooks():
                    if wh.name == "EchoProxy":
                        webhook = wh
                        break
                if webhook is None:
                    webhook = await message.channel.create_webhook(name="EchoProxy")

                await message.delete()
                await webhook.send(
                    proxied,
                    username=name,
                    avatar_url=data["avatar"],
                )
                triggered = True
                break
        if triggered:
            break

    await bot.process_commands(message)

bot.run(TOKEN)
