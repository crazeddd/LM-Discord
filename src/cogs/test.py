import discord
from discord import app_commands
from discord.ext import commands


class Test(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Ping the bot (works in DMs!)")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def ping(self, interaction: discord.Interaction) -> None:
        is_dm = interaction.guild is None
        location = "a DM" if is_dm else f"server: {interaction.guild.name}"
        await interaction.response.send_message(
            f"🏓 Pong! This message came from {location}.", ephemeral=is_dm
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Test(bot))
