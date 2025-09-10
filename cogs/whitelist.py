import aiohttp
import os
import re
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import traceback

load_dotenv()

verified_role_id = int(os.getenv("VERIFIED_ROLE_ID"))
get_verified_channel = int(os.getenv("GET_VERIFIED_CHANNEL"))
mcsmanager_host = os.getenv("MCSMANAGER_HOST")
mcsmanager_token = os.getenv("MCSMANAGER_API_KEY")
mcsmanager_daemon_id = os.getenv("MCSMANAGER_DAEMON_ID")
mcsmanager_instance_id = os.getenv("MCSMANAGER_INSTANCE_ID")

MC_USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,16}$")


class Whitelist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print(f"{__name__} cog loaded.")

    @app_commands.command(
        name="whitelist", description="Link your MC account & whitelist it."
    )
    @app_commands.checks.has_any_role(1414992207282442300)  # Temp Beta tester role
    async def whitelist(self, interaction: discord.Interaction):
        # Ensure they’re verified
        role = interaction.guild.get_role(verified_role_id)
        if role not in interaction.user.roles:
            await interaction.response.send_message(
                f"You must complete email verification first. Go to <#{get_verified_channel}> or run /verify",
                ephemeral=True,
            )
            return

        await interaction.response.send_modal(MinecraftModal())


class MinecraftModal(discord.ui.Modal, title="Enter Minecraft Username"):
    username = discord.ui.TextInput(
        label="Username",
        placeholder="Your minecraft username here...",
    )

    async def on_submit(self, interaction: discord.Interaction):
        username = self.username.value

        if not MC_USERNAME_PATTERN.match(username):
            await interaction.response.send_message(
                "Failed to add you to the whitelist. Please try again later.\nYou can DM a member of the committee to manually whitelist you.",
                ephemeral=True,
            )
            return

        url = f"{mcsmanager_host}/api/protected_instance/command"
        params = {
            "apikey": mcsmanager_token,
            "uuid": mcsmanager_instance_id,
            "daemonId": mcsmanager_daemon_id,
            "command": f"whitelist add {username}",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params) as resp:
                if resp.status == 200:
                    await interaction.response.send_message(
                        f"Successfully whitelisted `{username}`!", ephemeral=True
                    )
                else:
                    await interaction.response.send_message(
                        "Failed to add you to the whitelist. Please try again later.\nYou can DM a member of the committee to manually whitelist you.",
                        ephemeral=True,
                    )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        await interaction.response.send_message(
            "Oops! Something went wrong.", ephemeral=True
        )
        traceback.print_exception(type(error), error, error.__traceback__)


async def setup(bot):
    await bot.add_cog(Whitelist(bot))
