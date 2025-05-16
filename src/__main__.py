import discord, os, asyncio, sqlite3, aiohttp, json
from discord import app_commands
from dotenv import load_dotenv
from duckduckgo_search import DDGS

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
bot = app_commands.CommandTree(client)

# LM STUDIO REST API

CURRENT_MODEL = "hermes-3-llama-3.1-8b"

async def stream(prompt, system_prompt):
    url = "http://host.docker.internal:1234/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": CURRENT_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "stream": True,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            async for line in resp.content:
                line = line.decode("utf-8").strip()

                if not line.startswith("data:"):
                    continue  # Skip if it's not a data line

                if line == "data: [DONE]":
                    break

                try:
                    data = json.loads(line.replace("data: ", ""))
                    delta = data["choices"][0]["delta"]
                    content = delta.get("content", "")
                    if content:
                        yield content
                except Exception:
                    continue


# MEMORY

connect = sqlite3.connect("memory.db")
cursor = connect.cursor()

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    channel_id TEXT,
    role TEXT,
    content TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""
)

connect.commit()


def store_message(user_id, channel_id, role, content):
    cursor.execute(
        "INSERT INTO memory (user_id, channel_id, role, content) VALUES (?, ?, ?, ?)",
        (user_id, channel_id, role, content),
    )
    connect.commit()


def get_memory_chunk(channel_id, limit):
    cursor.execute(
        """
           SELECT role, content FROM memory
           WHERE channel_id = ?
           ORDER BY timestamp DESC 
           LIMIT ?   
    """,
        (channel_id, limit),
    )
    rows = cursor.fetchall()[::-1]

    return "\n".join(f"{role}: {content}" for role, content in rows)


async def get_channel_history(history):
    history = [msg async for msg in history]
    messages = []

    for msg in history:
        messages.insert(
            0,
            f"[{msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {msg.author.name}: {msg.content}",
        )
    recent = "\n".join(messages)

    return recent


# WEB SEARCHES
async def web_search(prompt, max_results=2):
    system_prompt = """
You are helping decide whether a user's message requires a web search.

IMPORTANT:
- Your internal knowledge only goes up to 2023. It may be outdated.
- If the question mentions current events, public figures, politics, the economy, recent data, live events, or anything time-sensitive, assume a search *is needed*.
- Err on the side of doing a search if you're unsure.
- Only respond with "No search needed" if the question is timeless (e.g. basic math, historical facts before 2023, or fictional lore).
- If the question *definitely* needs a search, rewrite it as a short search query.

Examples:
User: Who is the current president of the US?
Output: current us president

User: What's 2 + 2?
Output: No search needed

User: Did Elon Musk step down?
Output: elon musk twitter ceo 2024

User: Tell me about photosynthesis.
Output: No search needed
"""

    query = ""

    async for token in stream(prompt + "/no_think", system_prompt):
        query += token

    print(query)
    if "no search needed" in query.lower():
        return ["No search needed"]
    else:
        try:
            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=max_results)
                return [f"{r['title']}: {r['body']}" for r in results]
        except Exception as e:
            print("Search error:", e)
            return ["[Search failed]"]


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    await bot.sync(guild=discord.Object(id=784465241320062976))
    print("Connected to guild")


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


@bot.command(
    name="model",
    description="Changes the model Bob runs on",
    guild=discord.Object(id=784465241320062976),
)
async def help(interaction: discord.Interaction):
    await interaction()


@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if (
        client.user.name.lower() in message.content.lower()
        or client.user in message.mentions
    ):

        #memory = get_memory_chunk(message.channel.id, 8)
        #search_res = await web_search(message.content)
        recent = await get_channel_history(message.channel.history(limit=15))

        system_prompt = f"""You are {client.user.name}, a Discord-based assistant with memory and a dry sense of humor.
Respond informally and helpfully, using provided memory to act like you've been part of the conversation.
Avoid exaggeration or cheesy replies and use modern humor.
Use Discord markdown for emphasis.

[Recent Messages]
{recent}
"""
        prompt = f"{message.author.name}: {message.content}\nBob:"

        print(system_prompt, prompt)

        async with message.channel.typing():
            is_first_chunk = True
            inside_think = False
            buffer_rate = 175
            reply = ""
            buffer = ""

            async for token in stream(prompt, system_prompt):
                buffer += token

                if "<think>" in buffer:
                    buffer = ""  # discard start tag
                    inside_think = True
                    continue

                if "</think>" in buffer:
                    buffer = ""  # discard end tag
                    inside_think = False
                    continue

                if inside_think:
                    continue

                reply += token

                if is_first_chunk and reply.strip():
                    sent = await message.channel.send(content=reply.strip())
                    is_first_chunk = False

                if len(buffer) > buffer_rate:  # Reduce frequency of edits
                    await sent.edit(content=reply.strip())
                    buffer = ""

        await sent.edit(content=reply.strip())

        store_message(
            message.author.id, message.channel.id, message.author.name, message.content
        )
        store_message(
            message.author.id, message.channel.id, client.user.name, reply.strip()
        )


client.run(os.getenv("BOT_TOKEN"))
