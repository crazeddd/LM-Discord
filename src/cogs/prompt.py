import discord
from discord import app_commands
from discord.ext import commands


class Prompt(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.lm_client = bot.lm_client
        self.bot = bot

    @app_commands.command(
        name="prompt", description="Manually prompt the bot without context"
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def ping(self, interaction: discord.Interaction, prompt: str) -> None:

        system_prompt = f"""\
            You are {self.bot.user.name}, a Discord-based assistant with a dry sense of humor.
            Respond informally and helpfully, avoid exaggeration or cheesy replies and use modern humor.
            Write your response in clean paragraphs with no more than **one** blank line between sections. Do not add extra line breaks or spacing.
            Use Discord markdown for emphasis.
            """

        print(system_prompt, prompt)

        inside_think = False
        buffer_rate = 175
        reply = ""
        buffer = ""

        await interaction.response.send_message("Loading...")

        async for token in self.lm_client.stream(prompt, system_prompt):
            buffer += token

            if "<think>" in buffer:
                buffer = ""
                inside_think = True
                continue

            if "</think>" in buffer:
                buffer = ""
                inside_think = False
                continue

            if inside_think:
                continue

            reply += token

            if len(buffer) > buffer_rate:
                await interaction.edit_original_response(content=reply.rstrip())
                buffer = ""

        if reply.strip():
            await interaction.edit_original_response(content=reply.rstrip())
        else:
            await interaction.edit_original_response(
                "Sorry, I couldn't generate a response ⛓️‍💥 (Is the API online?)."
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Prompt(bot))
