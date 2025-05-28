import discord, asyncio
from discord import app_commands
from discord.ext import commands


class Purge(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="purge",
        description=f"Deletes a number of recent messages in a channel",
    )
    async def purge(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        amount: int,
    ) -> None:
        messages = []
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
            messages.append(msg)
        await channel.delete_messages(messages)
        await interaction.edit_original_response(
            content=f"Finished deleting **{i}** messages\n-# (This message will be deleted in 5s)"
        )
        await asyncio.sleep(5)
        await interaction.delete_original_response()


async def setup(bot: commands.Bot):
    await bot.add_cog(Purge(bot))
