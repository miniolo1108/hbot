import discord
from discord.ext import commands
import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = 1324139370038562818
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.dm_messages = True
intents.guilds = True
intents.members = True  # DM에 필요할 수 있음

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id == CHANNEL_ID and message.content.strip() == "dd!bot":
        try:
            await message.author.send("https://discord.com/oauth2/authorize?client_id=1259763046742757429")
        except discord.Forbidden:    
    await bot.process_commands(message)

bot.run(TOKEN)
