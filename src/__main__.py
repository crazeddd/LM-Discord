import discord, os, asyncio, aiohttp, json
from discord import app_commands
from discord.ui import View
from dotenv import load_dotenv

from memory import Memory

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
bot = app_commands.CommandTree(client)
guild = discord.Object(id=1372068994101547010)

# LM STUDIO REST API
current_model = "gemma-3-12b-it"

HOST = os.getenv("LM_STUDIO_HOST")
PORT = int(os.getenv("LM_STUDIO_PORT"))

async def get_models():
    url = f"{HOST}:{PORT}/v1/models"
    headers = {"Content-Type": "application/json"}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as res:
            if res.status == 200:
                data = await res.json()
                return data
            else:
                print("Error fetching models:", res.status)
                return None


async def stream(prompt, system_prompt):
    url = f"{HOST}:{PORT}/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": current_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "stream": True,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as res:
            async for line in res.content:
                line = line.decode("utf-8").strip()

                if not line.startswith("data:"):
                    continue

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


# COMMANDS
@bot.command(
    name="model",
    description=f"Change the current model",
    guild=guild,
)
async def model(interaction: discord.Interaction):
    models = await get_models()
    models_formatted = "```\n" + "\n".join(m["id"] for m in models["data"]) + "```"

    class Select(discord.ui.Select):
        def __init__(self):
            options = [
                discord.SelectOption(
                    label=m["id"], emoji="🤖", description=m["owned_by"]
                )
                for m in models["data"]
                if m["id"] != current_model
            ]
            super().__init__(
                placeholder="Choose a Model",
                max_values=1,
                min_values=1,
                options=options,
            )

        async def callback(self, interaction: discord.Interaction):
            self.selection = interaction.data["values"][0]
            global current_model
            current_model = self.selection
            await interaction.response.send_message(
                f"Updated Model to: {self.selection}"
            )

    view = View()
    view.add_item(Select())

    embed = discord.Embed(
        title=f"Current model: `{current_model}`",
        description="Change or update the running model",
        color=discord.Color.from_rgb(15, 213, 121),
        timestamp=discord.utils.utcnow(),
    )
    embed.add_field(name="Available Models", value=models_formatted)

    await interaction.response.send_message(embed=embed, view=view)


@bot.command(
    name="purge",
    description=f"Deletes a number of recent messages in a channel",
    guild=guild,
)
async def purge(
    interaction: discord.Interaction, channel: discord.TextChannel, amount: int
):
    i = 0

    if amount > 100:
        await interaction.response.send_message(
            content="Woops! You can't delete more than 100 messages at once"
        )
        return

    await interaction.response.send_message(
        content=f"Deleting **{amount}** messages in **{channel.mention}**..."
    )

    skipped = False
    async for msg in channel.history(limit=amount + 1):
        if not skipped:
            skipped = True
            continue

        i += 1
        await asyncio.sleep(0.30)
        await msg.delete()

    await interaction.edit_original_response(
        content=f"Finished deleting **{i}** messages\n-# (This message will be deleted in 5s)"
    )
    await asyncio.sleep(5)
    await interaction.delete_original_response()


@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if (
        client.user.name.lower() in message.content.lower()
        or client.user in message.mentions
    ):

        # local_memory = Memory.get_memory_chunk(message.channel.id, 8)
        # search_res = await web_search(message.content)
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


# DISCORD INIT
@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    await bot.sync(guild=guild)
    print("Synced commands")


client.run(os.getenv("BOT_TOKEN"))
