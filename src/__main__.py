import discord, os, sys, datetime, asyncio
from discord.ext import commands
from dotenv import load_dotenv

from utils.memory import Memory
from utils.lmstudio_client import LMStudioClient
from utils.tools import Tools

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

bot.lm_client = LMStudioClient()
bot.memory = Memory()
bot.tools = Tools()

current_model = None
local_memory = None
i = 0


@bot.event
async def on_ready():
    global current_model
    await bot.lm_client.initialize_model()
    current_model = bot.lm_client.model
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    synced = await bot.tree.sync()

    print(f"{time} Logged in as {bot.user}")
    print(f"{time} Discord.py version: {discord.__version__}")
    print(f"{time} Synced {str(len(synced))} commands")
    print(f"{time} Current model: {current_model}")


async def main():
    await bot.load_extension("cogs.model")
    await bot.load_extension("cogs.purge")
    await bot.load_extension("cogs.events")
    await bot.load_extension("cogs.test")
    await bot.load_extension("cogs.prompt")


asyncio.run(main())

bot.run(os.getenv("BOT_TOKEN"))
