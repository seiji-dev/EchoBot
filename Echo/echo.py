import discord
from discord.ext import commands
import os
import json
import threading
from flask import Flask
import requests
from dotenv import load_dotenv

# ---------------- LOAD TOKEN ----------------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ---------------- DISCORD INTENTS ----------------
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="Echo/", intents=intents)

# ---------------- DATA FILE ----------------
DATA_FILE = "characters.json"

def load_characters():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf8") as f:
        return json.load(f)

def save_characters():
    with open(DATA_FILE, "w", encoding="utf8") as f:
        json.dump(characters, f, indent=4)

characters = load_characters()

# ---------------- KEEP ALIVE (For Replit) ----------------
app = Flask("")

@app.route("/")
def home():
    return "Echo bot: alive!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    thread = threading.Thread(target=run_flask)
    thread.start()

def auto_ping():
    url = "https://REPLIT-PROJECT-URL"   # <-- CHANGE THIS to your Replit web URL
    def ping_loop():
        while True:
            try:
                requests.get(url)
            except:
                pass
            import time
            time.sleep(240)  # every 4 minutes
    thread = threading.Thread(target=ping_loop)
    thread.start()

keep_alive()
auto_ping()

# ---------------- READY ----------------
@bot.event
async def on_ready():
    print(f"Echo online as {bot.user}")

# ---------------- REGISTER ----------------
@bot.command(name="register")
async def register(ctx, name: str, trigger: str):
    if not trigger.endswith(":"):
        return await ctx.send("Trigger must end with a colon (e.g. Ekk:)")

    attachment = ctx.message.attachments[0] if ctx.message.attachments else None
    avatar_url = attachment.url if attachment else ctx.author.display_avatar.url

    user = str(ctx.author.id)
    characters.setdefault(user, {})
    characters[user][name] = {"trigger": trigger, "avatar": avatar_url}
    save_characters()

    embed = discord.Embed(title="Character Registered", color=0x88ccff)
    embed.add_field(name="Name", value=name, inline=False)
    embed.add_field(name="Trigger", value=trigger, inline=False)
    embed.set_thumbnail(url=avatar_url)

    await ctx.send(embed=embed)

# ---------------- RENAME ----------------
@bot.command(name="rename")
async def rename(ctx, old: str, new: str):
    user = str(ctx.author.id)
    if old not in characters.get(user, {}):
        return await ctx.send("Character not found.")

    characters[user][new] = characters[user].pop(old)
    save_characters()
    await ctx.send(f"Renamed **{old}** to **{new}**.")

# ---------------- AVATAR ----------------
@bot.command(name="avatar")
async def avatar(ctx, name: str):
    user = str(ctx.author.id)
    if name not in characters.get(user, {}):
        return await ctx.send("Character not found.")

    attachment = ctx.message.attachments[0] if ctx.message.attachments else None
    if not attachment:
        return await ctx.send("Please attach an image.")

    characters[user][name]["avatar"] = attachment.url
    save_characters()
    await ctx.send(f"Updated avatar for **{name}**.")

# ---------------- BRACKET ----------------
@bot.command(name="bracket")
async def bracket(ctx, name: str, new_trigger: str):
    if not new_trigger.endswith(":"):
        return await ctx.send("Trigger must end with a colon.")

    user = str(ctx.author.id)
    if name not in characters.get(user, {}):
        return await ctx.send("Character not found.")

    characters[user][name]["trigger"] = new_trigger
    save_characters()
    await ctx.send(f"Updated trigger for **{name}** to `{new_trigger}`.")

# ---------------- DELETE ----------------
@bot.command(name="delete")
async def delete(ctx, name: str):
    user = str(ctx.author.id)
    if name not in characters.get(user, {}):
        return await ctx.send("Character not found.")

    del characters[user][name]
    save_characters()
    await ctx.send(f"Deleted **{name}**.")

# ---------------- LIST ----------------
@bot.command(name="list")
async def list_characters(ctx):
    user = str(ctx.author.id)
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
    user = str(ctx.author.id)
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

# ---------------- COMMANDS HELP ----------------
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

    for user_id, user_chars in characters.items():
        for name, data in user_chars.items():
            trigger = data["trigger"]

            # if message starts with the user's trigger
            if content.startswith(trigger):
                proxied_text = content[len(trigger):].strip()

                # find/create webhook
                webhooks = await message.channel.webhooks()
                webhook = next((w for w in webhooks if w.name == "EchoProxy"), None)

                if webhook is None:
                    webhook = await message.channel.create_webhook(name="EchoProxy")

                # delete original message
                try:
                    await message.delete()
                except:
                    pass

                # send proxy message
                await webhook.send(
                    proxied_text,
                    username=name,
                    avatar_url=data["avatar"]
                )
                return  # stop after proxying

    await bot.process_commands(message)

# ---------------- RUN BOT ----------------
bot.run(TOKEN)
