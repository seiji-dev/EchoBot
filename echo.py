import discord
from discord.ext import commands
import json
import os

DATA_FILE = "characters.json"

# ---------------------------
# JSON SAVE / LOAD FUNCTIONS
# ---------------------------

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f, indent=4)
        return {}

    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Load saved characters on startup
characters = load_data()

# ---------------------------
# DISCORD BOT SETUP
# ---------------------------

# ✅ Explicitly enable message content intent
intents = discord.Intents.default()
intents.message_content = True

# You can also enable other intents if needed (like members, reactions, etc.)
# intents.members = True
# intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------------------
# BOT COMMANDS
# ---------------------------

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def addchar(ctx, name: str, *, description: str):
    """Adds or updates a character."""
    characters[name] = {
        "description": description,
        "owner": ctx.author.id
    }
    save_data(characters)
    await ctx.send(f"✅ Character **{name}** saved!")

@bot.command()
async def showchar(ctx, name: str):
    """Shows a saved character."""
    if name not in characters:
        await ctx.send("❌ Character not found.")
        return
    char = characters[name]
    await ctx.send(f"**{name}**\n{char['description']}")

@bot.command()
async def delchar(ctx, name: str):
    """Deletes a character."""
    if name not in characters:
        await ctx.send("❌ Character not found.")
        return
    del characters[name]
    save_data(characters)
    await ctx.send(f"🗑 Character **{name}** deleted.")

@bot.command()
async def listchars(ctx):
    """Lists all characters saved."""
    if not characters:
        await ctx.send("No characters saved yet.")
        return
    names = "\n".join(characters.keys())
    await ctx.send(f"📜 **Characters:**\n{names}")

# ---------------------------
# RUN BOT
# ---------------------------

bot.run(os.environ["DISCORD_TOKEN"])
