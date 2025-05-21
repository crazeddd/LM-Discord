import discord, asyncio
from discord import app_commands
from discord.ext import commands


class Prompt(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="prompt", description="Manually prompt the bot without context")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def ping(self, interaction: discord.Interaction, prompt: str) -> None:

        system_prompt = f"""\
            You are {self.bot.user.name}, a Discord-based assistant with memory and a dry sense of humor.
            Respond informally and helpfully, using provided memory to act like you've been part of the conversation.
            Avoid exaggeration or cheesy replies and use modern humor.
            Write your response in clean paragraphs with no more than **one** blank line between sections. Do not add extra line breaks or spacing.
            Use Discord markdown for emphasis.
            """

        print(system_prompt, prompt)

        is_first_chunk = True
        inside_think = False
        buffer_rate = 175
        reply = ""
        buffer = ""
        sent = None

        async for token in self.lm_client.stream(prompt, system_prompt):
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
                sent = await interaction.response.send_message(content=reply.rstrip())
                is_first_chunk = False

            if len(buffer) > buffer_rate:
                if sent is not None:
                    await sent.edit(content=reply.rstrip())
                buffer = ""
        if sent is not None:
            await interaction.response.edit_message(content=reply.rstrip())
        elif reply.strip():
            await interaction.response.send_message(content=reply.rstrip())
        else:
            await interaction.response.send_message(
                "Sorry, I couldn't generate a response ⛓️‍💥 (Is the API online?)."
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Prompt(bot))
