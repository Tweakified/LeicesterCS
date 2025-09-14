import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
from dotenv import load_dotenv
import os
from datetime import datetime
from typing import Optional

# CONFIGURATION
extensions = [
    "cogs.tasks",
    "cogs.misc",
    "cogs.guild",
    "cogs.verify",
    "cogs.tutorials",
    "cogs.minecraft",
]

load_dotenv()

# Intents
intents = discord.Intents.all()
# intents.dm_messages = False # Disable Bot's DMs


class aclient(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="a!", intents=intents)
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            # await self.tree.sync()
            self.synced = True
        print("Bot is ready.")

        for ext in extensions:
            await self.load_extension(ext)


bot = aclient()


# SYNC SLASH COMMANDS
@bot.command()
@app_commands.checks.has_permissions(administrator=True)
async def sync(ctx: commands.Context, globalSync=None):
    if globalSync:
        await bot.tree.sync()
        await ctx.reply(":globe_with_meridians: Synced commands globally.")
    else:
        try:
            await bot.tree.sync(guild=ctx.guild)
            await ctx.reply(
                ":globe_with_meridians: Synced commands to the current guild.\n(Tip: use `global` parameter to sync globally)"
            )
        except Exception:
            await ctx.reply(":warning: There was an error!")


@sync.error
async def sync_error(ctx, error):
    await ctx.reply(":warning: **Command error** (possibly no permission).")


# Cogs reload
@bot.tree.command(name="reload", description="Reload cogs")
@app_commands.describe(cog="Reload a specific cog")
@app_commands.choices(
    cog=[Choice(name=x.split(".")[1], value=x) for x in extensions]
)  # Copy extensions to Choice
@app_commands.guild_only()
@app_commands.default_permissions()
@app_commands.checks.has_permissions(administrator=True)
@app_commands.checks.cooldown(1, 10)
async def reload(interaction: discord.Interaction, cog: Optional[Choice[str]]):
    if cog is None:
        for ext in extensions:
            await bot.reload_extension(ext)
        await interaction.response.send_message(":white_check_mark: Cogs reloaded.")
    else:
        await bot.reload_extension(cog.value)
        await interaction.response.send_message(
            f":white_check_mark: **{cog.name}** cog reloaded."
        )


# Uptime command
uptime = datetime.now().timestamp()


@bot.tree.command(name="uptime", description="See bot's uptime")
async def uptime_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        f":clock3: Bot started: **<t:{int(uptime)}:R>**"
    )


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingAnyRole):
        required_roles = ', '.join(f"`{role}`" for role in error.missing_roles)
        await interaction.response.send_message(
            f"You need at least one of the following roles to use this command: {required_roles}",
            ephemeral=True
        )
    else:
        await interaction.response.send_message("An unexpected error occurred.", ephemeral=True)
        raise error


bot.run(os.getenv("DISCORD_TOKEN"))
