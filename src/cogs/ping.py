import discord
from discord import app_commands
from discord.ext import commands


class Test(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Pings the bot")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def ping(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            content=("Pong! {0}s".format(round(self.bot.latency, 1))), ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Test(bot))
