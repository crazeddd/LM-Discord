import discord, os
from discord import app_commands
from dotenv import load_dotenv
from llama_cpp import Llama

llm = Llama(model_path="../model/deepseek-llm-7b-chat.Q2_K.gguf", n_ctx=2048)

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
bot = app_commands.CommandTree(client)


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
        "got rejected from art school, never turned back from there :saluting_face:"
)

@client.event
async def on_voice_state_update(member, before, after):
    voice_channel = 785276812762677269
    role = discord.utils.find(lambda r: r.name == "Jencum Huffer", member.roles)

    if after.channel != None:
        print(f"{member} joined {after.channel}")

        audio_path = "./audio"
        audio_list = os.listdir(audio_path)
        print(len(audio_list))
        audio = audio_list[random.randint(0, len((audio_list)) - 1)]

        if role in member.roles and after.channel.id == voice_channel:
            global vc
            vc = await after.channel.connect()
            vc.play(discord.FFmpegPCMAudio(source=f"audio/{audio}"))
            channel = client.get_channel(784465241320062980)
            await channel.send(responses[random.randint(0, len(responses) - 1)])
    else:
        if role in member.roles:
            await vc.disconnect()
        print(f"{member} left {before.channel}")
"""

@client.event
async def on_message(message):
    content = message.content.lower()

    if message.author == client.user:
        return

    if message.content.startswith("bob"):
        prompt = message.content
        output = await asyncio.to_thread(llm, prompt, max_tokens=50, stop=["</s>"])
        await message.channel.send(output["choices"][0]["text"].strip())

client.run(os.getenv('BOT_TOKEN'))