import discord, os, sys, datetime
from discord.ext import commands
from dotenv import load_dotenv

from utils.memory import Memory
from utils.lmstudio_client import LMStudioClient

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

bot.guild = discord.Object(id=1372068994101547010)
bot.lm_client = LMStudioClient()
bot.memory = Memory()

current_model = None
local_memory = None
i = 0

# DISCORD INIT
@bot.event
async def on_ready():
    global current_model
    await bot.lm_client.initialize_model()
    current_model = bot.lm_client.model
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    synced = await bot.tree.sync()

    print(f"{time} Logged in as {bot.user}")
    print(f"{time} Synced {str(len(synced))} commands")
    print(f"{time} Current model: {current_model}")

async def main():
    await bot.load_extension("cogs.model")
    await bot.load_extension("cogs.purge")
    await bot.load_extension("cogs.events")

import asyncio
asyncio.run(main())

bot.run(os.getenv("BOT_TOKEN"))
