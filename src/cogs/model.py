import discord
from discord.ui import View
from discord import app_commands
from discord.ext import commands

class Model(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.lm_client = bot.lm_client

    @app_commands.command(
        name="model",
        description=f"Change the current model",
    )
    async def model(self, interaction: discord.Interaction) -> None:
        current_model = self.lm_client.model
        models = await self.lm_client.get_models()
        models_formatted = "```\n" + "\n".join(m["id"] for m in models["data"]) + "```"
        is_dm = interaction.guild is None

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

            async def callback(self, interaction: discord.Interaction) -> None:
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

        await interaction.response.send_message(embed=embed, view=view, ephemeral=is_dm)


async def setup(bot: commands.Bot):
    await bot.add_cog(Model(bot))
