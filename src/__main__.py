import discord, os, sys, asyncio
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime

from utils.memory import Memory
from utils.lmstudio_client import LMStudioClient
from utils.tools import Tools

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

current_model = os.getenv("DEFAULT_MODEL", None)

bot.lm_client = LMStudioClient()
bot.memory = Memory()
bot.tools = Tools()


@bot.event
async def on_ready():
    global current_model
    await bot.lm_client.initialize_model(current_model)
    current_model = bot.lm_client.model
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    synced = await bot.tree.sync()

    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.listening, name=f"{current_model} 📦"
        ),
    )

    print(f"{time} Logged in as {bot.user}")
    print(f"{time} Discord.py version: {discord.__version__}")
    print(f"{time} Synced {str(len(synced))} commands")
    print(f"{time} Current model: {current_model}")


async def main():
    await bot.load_extension("cogs.model")
    await bot.load_extension("cogs.events")
    await bot.load_extension("cogs.ping")
    await bot.load_extension("cogs.prompt")
    # await bot.load_extension("cogs.purge")


asyncio.run(main())

bot.run(os.getenv("BOT_TOKEN"))
