import discord
from discord.ext import commands
import os
import json
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ---------- BOT SETUP ----------
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="Echo/", intents=intents, help_command=None)  # Disable default help

# ---------- PERSISTENT STORAGE ----------
CHAR_FILE = "characters.json"
characters = {}

# Load characters, handle empty or invalid JSON
if os.path.exists(CHAR_FILE):
    try:
        with open(CHAR_FILE, "r") as f:
            characters = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        characters = {}
else:
    characters = {}

def save_characters():
    with open(CHAR_FILE, "w") as f:
        json.dump(characters, f, indent=4)

# ---------- HELP COMMAND ----------
@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(title="Echo Bot Commands", color=0x00ff00)
    embed.add_field(name='Echo/register "Name" Bracket:Text [Universe]', value='Register a new character', inline=False)
    embed.add_field(name='Echo/rename "Old Name" "New Name"', value='Rename a character', inline=False)
    embed.add_field(name='Echo/avatar "Name" + attach image', value='Update character avatar', inline=False)
    embed.add_field(name='Echo/list [search term]', value='List characters, optional search', inline=False)
    embed.add_field(name='Echo/delete "Name"', value='Delete a character', inline=False)
    embed.add_field(name='Echo/help', value='Show this help message', inline=False)
    await ctx.send(embed=embed)

# ---------- REGISTER ----------
@bot.command(name="register")
async def register(ctx, name, bracket_text, universe="Default"):
    user_id = str(ctx.author.id)

    if user_id not in characters:
        characters[user_id] = []

    # Check duplicates
    if any(c["name"] == name and c.get("universe") == universe for c in characters[user_id]):
        await ctx.send(f"A character named `{name}` in universe `{universe}` already exists.")
        return

    # Store user input in variable
    char_data = {
        "name": name,
        "bracket": bracket_text,
        "universe": universe,
        "avatar": None
    }

    # Add avatar if attached
    if ctx.message.attachments:
        char_data["avatar"] = ctx.message.attachments[0].url

    # Add character to user
    characters[user_id].append(char_data)
    save_characters()

    # Send confirmation embed
    embed = discord.Embed(title=f"Character Registered: {name}", color=0x00ff00)
    embed.add_field(name="Bracket", value=bracket_text, inline=False)
    embed.add_field(name="Universe", value=universe, inline=False)
    if char_data["avatar"]:
        embed.set_thumbnail(url=char_data["avatar"])
    await ctx.send(embed=embed)

# ---------- RENAME ----------
@bot.command(name="rename")
async def rename(ctx, old_name, new_name):
    user_id = str(ctx.author.id)
    if user_id not in characters:
        await ctx.send("You have no registered characters.")
        return

    for char in characters[user_id]:
        if char["name"] == old_name:
            char["name"] = new_name
            save_characters()
            await ctx.send(f"✅ Character `{old_name}` renamed to `{new_name}`")
            return
    await ctx.send(f"No character named `{old_name}` found.")

# ---------- AVATAR ----------
@bot.command(name="avatar")
async def avatar(ctx, name):
    user_id = str(ctx.author.id)
    if user_id not in characters:
        await ctx.send("You have no registered characters.")
        return

    char = next((c for c in characters[user_id] if c["name"] == name), None)
    if not char:
        await ctx.send(f"No character named `{name}` found.")
        return

    if not ctx.message.attachments:
        await ctx.send("Please attach an image for the avatar.")
        return

    avatar_url = ctx.message.attachments[0].url
    char["avatar"] = avatar_url
    save_characters()
    await ctx.send(f"✅ Avatar updated for `{name}`!")

# ---------- LIST ----------
@bot.command(name="list")
async def list_characters(ctx, *, search: str = None):
    user_id = str(ctx.author.id)
    if user_id not in characters or not characters[user_id]:
        await ctx.send("You have no registered characters.")
        return

    filtered = characters[user_id]
    if search:
        search_lower = search.lower()
        filtered = [
            c for c in filtered
            if search_lower in c["name"].lower()
            or search_lower in c["bracket"].lower()
            or search_lower in c.get("universe","").lower()
        ]

    if not filtered:
        await ctx.send(f"No characters found for search `{search}`.")
        return

    embed = discord.Embed(title=f"{ctx.author.name}'s Characters", color=0x00ff00)
    for char in filtered:
        value = f"Bracket: {char['bracket']}\nUniverse: {char.get('universe','Default')}"
        embed.add_field(name=char["name"], value=value, inline=False)
        if char["avatar"]:
            embed.set_thumbnail(url=char["avatar"])
    await ctx.send(embed=embed)

# ---------- DELETE ----------
@bot.command(name="delete")
async def delete(ctx, name):
    user_id = str(ctx.author.id)
    if user_id not in characters:
        await ctx.send("You have no registered characters.")
        return

    for i, char in enumerate(characters[user_id]):
        if char["name"] == name:
            del characters[user_id][i]
            save_characters()
            await ctx.send(f"✅ Character `{name}` deleted.")
            return
    await ctx.send(f"No character named `{name}` found.")

# ---------- ON READY ----------
@bot.event
async def on_ready():
    print(f"{bot.user} is online!")

# ---------- RUN BOT ----------
bot.run(TOKEN)
