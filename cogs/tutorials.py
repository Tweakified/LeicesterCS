import discord
import asyncio
from discord import app_commands
from discord.ext import commands

from json import load

from modules.enums import FileLocations

with open(FileLocations.Modules.value, mode="r", encoding="utf-8") as f:
    modules = load(f)

def make_human_readable_list(items: list[str]) -> str:
    if len(items) == 0:
        return ""
    elif len(items) == 1:
        return items[0]
    else:
        return ", ".join(items[:-1]) + " and " + items[-1]

class Tutorials(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="Select a module",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label=code,
                description=module["description"],
            )
            for code, module in modules.items()
        ],
    )
    async def on_select(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        embed = discord.Embed(
            title=f"Tutorial for {select.values[0]}",
            description="Here are some helpful tutorials/materials for this module",
            color=discord.Color.random(),
        )
        embed_data = modules.get(select.values[0], modules["CO1108"])
        embed.set_image(url=embed_data["image"])
        for field in embed_data["fields"]:
            embed.add_field(name=field["name"], value=field["value"], inline=True)

        authors = make_human_readable_list(embed_data["authors"])

        embed.set_footer(text=f"Tutorial resources created by: {authors}")
        await interaction.response.defer()
        user = interaction.user
        await user.send(embed=embed)
        await interaction.followup.send(
            f"The material for {select.values[0]} has been DM'd to you {user.mention}",
            ephemeral=True,
        )


class TutorialCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="tutorial", description="Select a module to view tutorials"
    )
    async def tutorial(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.followup.send(
            "Select a module from the dropdown below:", view=Tutorials(), ephemeral=True
        )
        await asyncio.sleep(15)
        await interaction.delete_original_response()


async def setup(bot: commands.Bot):
    await bot.add_cog(TutorialCog(bot))
