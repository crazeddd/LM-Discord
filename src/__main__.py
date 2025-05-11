import discord, os, asyncio, sqlite3
from discord import app_commands
from dotenv import load_dotenv
from llama_cpp import Llama

llm = Llama(model_path="../models/deepseek-llm-7b-chat.Q5_K_M.gguf", n_ctx=2048)

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
bot = app_commands.CommandTree(client)

chat_history = []

connect = sqlite3.connect("memory.db")
cursor = connect.cursor()

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    role TEXT,
    content TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""
)

connect.commit()


def store_message(user_id, role, content):
    cursor.execute(
        "INSERT INTO memory (user_id, role, content) VALUES (?, ?, ?)",
        (user_id, role, content),
    )
    connect.commit()


def get_memory_chunk(user_id, limit):
    cursor.execute(
        """
           SELECT role, content FROM memory
           WHERE user_id = ?
           ORDER BY id DESC
           LIMIT ?   
    """,
        (user_id, limit),
    )
    rows = cursor.fetchall()[::-1]

    return "\n".join(f"{role}: {content}" for role, content in rows)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
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

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if "bob" in message.content.lower() or client.user in message.mentions:

        memory = get_memory_chunk(message.author.id, 10)

        prompt = f"""
            You are Bob, a Discord-based assistant with memory and a understated but prominent sense of humor.
            You remember key facts and recent conversation history that is provided to you. Use it to answer users as if you've been here the whole time.
            You give useful answers and respond informally, but without being exaggerated. 
            Avoid overly theatrical or cheesy responses.
            You use Discord's markdown in your messages.

            [Recent Conversation]
            {memory}

            {message.author.name}: {message.content}
            Bob:"""

        print(prompt)

        def generate_tokens():
            return llm(
                prompt,
                max_tokens=200,
                stop=[f"{message.author.name}:"],
                temperature=0.8,
                top_p=0.9,
                top_k=40,
                repeat_penalty=1.1,
            )

        async with message.channel.typing():
            output = await asyncio.to_thread(generate_tokens)
            reply = output["choices"][0]["text"].strip()

        await message.channel.send(reply)

        store_message(message.author.id, message.author.name, message.content)
        store_message(message.author.id, "Bob", reply)


client.run(os.getenv("BOT_TOKEN"))
