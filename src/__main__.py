import discord, os, asyncio, sqlite3
from discord import app_commands
from dotenv import load_dotenv
from llama_cpp import Llama

llm = Llama(model_path="../models/deepseek-llm-7b-chat.Q2_K.gguf", n_ctx=2048)

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
bot = app_commands.CommandTree(client)

chat_history = []

connect = sqlite3.connect("memory.db")
cursor = connect.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    role TEXT,
    content TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

connect.commit()

def store_message(user_id, role, content):
    cursor.execute("INSERT INTO memory (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
    connect.commit()

def get_memory(limit):
    cursor.execute("""
           SELECT role, content FROM memory
           ORDER BY id DESC
           LIMIT ?   
    """, (limit,))
    rows = cursor.fetchall()[::-1]

    return "\n".join(f"{role}: {content}" for role, content in rows)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await bot.sync(guild=discord.Object(id=784465241320062976))
    print("Connected to Discord Server!")

"""
@bot.command(
    name="help",
    description="Tells u a little about the bot",
    guild=discord.Object(id=784465241320062976),
)
async def help(interaction: discord.Interaction):
    await interaction.response.send_message(
        ""
)
"""

system_prompt = (
    "You are Bob a helpful AI assitant that does everything asked of it"
) 

@client.event
async def on_message(message):
    content = message.content.lower()

    if message.author == client.user:
        return

    if "bob" in content:
        memory = get_memory(10)

        print(memory)

        prompt = f"{system_prompt}\n{memory}\nHuman: {message.content}\nBob:"
        output = await asyncio.to_thread(llm, prompt, max_tokens=300, stop=["Human:"])
        reply = output["choices"][0]["text"].strip()

        await message.channel.send(reply)

        store_message(message.author.id, "Human", message.content)
        store_message(1370536669362786385, "Bob", reply)

client.run(os.getenv('BOT_TOKEN'))