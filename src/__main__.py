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


async def stream(prompt, system_prompt):
    url = "http://host.docker.internal:1234/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "mistral-nemo-instruct-2407",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
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


# WEB SEARCHES
async def web_search(prompt, max_results=2):
    system_prompt = f"""
            Rewrite the following question into a short, Google-style search query, if you believe a search is necessary.
            If you think the question can be answered without a search, respond with "No search needed".
            """
    query = ""
    async for token in stream(prompt, system_prompt):
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

    if "bob" in message.content.lower() or client.user in message.mentions:

        memory = get_memory_chunk(message.channel.id, 8)
        search_res = await web_search(message.content)

        system_prompt = f"""You are Bob, a Discord-based assistant with memory and a dry sense of humor.
Respond informally and helpfully, using provided memory to act like you've been part of the conversation.
Avoid exaggeration or cheesy replies.
Use Discord markdown for emphasis.

[Recent Conversation]
{memory}

[Search Results]
{search_res}

"""

        print(system_prompt)

        prompt = f"{message.author.name}: {message.content}\nBob:"

        async with message.channel.typing():
            is_first_chunk = True
            buffer_rate = 175
            reply = ""
            buffer = ""

            async for token in stream(prompt, system_prompt):
                reply += token
                buffer += token

                if is_first_chunk:
                    sent = await message.channel.send(content=reply.strip())
                    is_first_chunk = False

                if len(buffer) > buffer_rate:  # Reduce frequency of edits
                    await sent.edit(content=reply.strip())
                    buffer = ""

        await sent.edit(content=reply.strip())

        store_message(message.author.id, message.channel.id, message.author.name, message.content)
        store_message(message.author.id, message.channel.id, "Bob", reply.strip())


client.run(os.getenv("BOT_TOKEN"))
