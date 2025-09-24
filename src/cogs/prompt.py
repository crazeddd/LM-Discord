import discord
from discord import app_commands
from discord.ext import commands


class Prompt(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.lm_client = getattr(bot, "lm_client", None)
        self.bot = bot

    @app_commands.command(
        name="prompt", description="Manually prompt the bot without context"
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def prompt(self, interaction: discord.Interaction, prompt: str) -> None:

        bot_name = (
            self.bot.user.name
            if self.bot.user and hasattr(self.bot.user, "name")
            else "the bot"
        )
        system_prompt = f"""\
            You are a Discord-based assistant with a dry sense of humor.
                Do NOT include any tags like <|start|>, <|end|>, <|assistant|>, <|channel|>, <|message|>, or tool-call wrappers.
                Use Discord markdown for emphasis, respond helpfully.
            """

        inside_think = False
        buffer_rate = 175
        reply = ""
        buffer = ""

        await interaction.response.send_message("Thinking...")

        if not self.lm_client or not hasattr(self.lm_client, "stream"):
            await interaction.edit_original_response(
                content="Sorry, I couldn't generate a response ⛓️‍💥 (Is the API online?)."
            )
            return

        async for token in self.lm_client.stream(
            [{"role": "user", "name": interaction.user.name, "content": prompt}],
            system_prompt,
        ):
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
                content="Sorry, I couldn't generate a response ⛓️‍💥 (Is the API online?)."
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Prompt(bot))
