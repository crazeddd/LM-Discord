import discord
from discord.ui import View
from discord import app_commands
from discord.ext import commands


class Model(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.lm_client = bot.lm_client

    @property
    def current_model(self):
        return self.lm_client.model

    @app_commands.command(
        name="model",
        description=f"Change the current model",
    )
    async def model(self, interaction: discord.Interaction) -> None:
        models = await self.lm_client.get_models()
        models_formatted = "```\n" + "\n".join(m["id"] for m in models["data"]) + "```"
        is_dm = interaction.guild is None

        class Select(discord.ui.Select):
            def __init__(self, lm_client, bot: commands.Bot):
                self.bot = bot
                self.lm_client = lm_client
                options = [
                    discord.SelectOption(
                        label=m["id"], emoji="🤖", description=m["owned_by"]
                    )
                    for m in models["data"]
                    if m["id"] != self.lm_client.model
                ]
                super().__init__(
                    placeholder="Choose a Model",
                    max_values=1,
                    min_values=1,
                    options=options,
                )

            async def callback(self, interaction: discord.Interaction) -> None:
                selection = self.values[0]
                self.current_model = selection
                await self.lm_client.initialize_model(selection)

                await self.bot.change_presence(
                    status=discord.Status.online,
                    activity=discord.Activity(
                        type=discord.ActivityType.listening,
                        name=f"{self.current_model} 📦",
                    ),
                )

                await interaction.response.send_message(
                    f"Updated Model to: {selection}"
                )

        view = View()
        view.add_item(Select(self.lm_client, self.bot))

        embed = discord.Embed(
            title=f"Current model: `{self.current_model}`",
            description="Change the running model",
            color=discord.Color.from_rgb(15, 213, 121),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="Available Models", value=models_formatted)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=is_dm)


async def setup(bot: commands.Bot):
    await bot.add_cog(Model(bot))
