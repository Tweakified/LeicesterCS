import aiohttp
import os
import re
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from mcstatus import JavaServer
from modules import enums
import traceback
import json

load_dotenv()

verified_role_id = int(os.getenv("VERIFIED_ROLE_ID"))
dmu_verified_role_id = int(os.getenv("DMU_VERIFIED_ROLE_ID"))
get_verified_channel = int(os.getenv("GET_VERIFIED_CHANNEL"))
mc_whitelist_channel = int(os.getenv("MC_WHITELIST_CHANNEL"))
mcsmanager_host = os.getenv("MCSMANAGER_HOST")
mcsmanager_token = os.getenv("MCSMANAGER_API_KEY")
mcsmanager_daemon_id = os.getenv("MCSMANAGER_DAEMON_ID")
mcsmanager_instance_id = os.getenv("MCSMANAGER_INSTANCE_ID")
mc_whitelist_webhook_url = os.getenv("MC_WHITELIST_WEBHOOK_URL")
mc_address = os.getenv("MC_ADDRESS")
mc_port = os.getenv("MC_PORT")

MC_USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,16}$")


class Minecraft(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not os.path.exists(enums.FileLocations.MCData.value):
            with open(enums.FileLocations.MCData.value, "w", encoding="utf-8") as f:
                json.dump({}, f)
        print(f"{__name__} cog loaded.")
        bot.add_view(WhitelistButtons())

    @app_commands.command(
        name="mcstatus",
        description="Check the status of the LeicesterMC Minecraft server",
    )
    async def mcstatus(self, interaction: discord.Interaction):
        try:
            server = JavaServer.lookup(f"{mc_address}:{mc_port}")
            status = server.status()
            version = status.version.name
            online = True
            players_online = status.players.online
            max_players = status.players.max
            status_text = "🟢 Online"
        except Exception as e:
            version = "Unknown"
            online = False
            players_online = 0
            max_players = 0
            status_text = "🔴 Offline"

        embed = discord.Embed(
            title="🎮 LeicesterMC Server Status",
            color=discord.Color.green() if online else discord.Color.red(),
        )
        embed.add_field(name="Address", value=mc_address, inline=False)
        embed.add_field(name="Version", value=version, inline=True)
        embed.add_field(name="Status", value=status_text, inline=True)
        embed.add_field(
            name="Players", value=f"{players_online}/{max_players}", inline=True
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="whitelist", description="Link your MC account & whitelist it."
    )
    @app_commands.checks.has_any_role(1414992207282442300)  # Temp Beta tester role
    async def whitelist(self, interaction: discord.Interaction):
        # Ensure they’re verified
        roles = interaction.user.roles
        if not any(role.id in (verified_role_id, dmu_verified_role_id) for role in roles):
            await interaction.response.send_message(
                f"You must complete email verification first. Go to <#{get_verified_channel}> or run /verify",
                ephemeral=True,
            )
            return

        await interaction.response.send_modal(WhitelistModal())

    @app_commands.command(
        name="update-whitelist-message",
        description="Update the whitelist message in the whitelist channel.",
    )
    @app_commands.checks.has_any_role(enums.Roles.Administration.value)
    async def update_whitelistmessage(self, interaction: discord.Interaction):
        channel = self.bot.get_channel(mc_whitelist_channel)

        embed = discord.Embed(
            title="🎮 Minecraft Whitelist",
            description=(
                "⚠️ By whitelisting a Minecraft account, **you are responsible for the user**.\n\n"
                "You must ensure that the player follows all of our server rules.\n"
                "By clicking the Start button below you agree to this."
            ),
            color=discord.Color.green(),
        )
        embed.set_footer(text=interaction.guild.name + " Whitelist")

        await channel.send(embed=embed, view=WhitelistButtons())
        await interaction.response.send_message(
            f"✅ Whitelist message updated in {channel.mention}.", ephemeral=True
        )


class WhitelistButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Start", style=discord.ButtonStyle.green, custom_id="whitelist_button"
    )
    async def whitelist(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(WhitelistModal())


class WhitelistModal(discord.ui.Modal, title="Minecraft Whitelist"):
    username = discord.ui.TextInput(
        label="Minecraft Username",
        placeholder="⚠️ You are responsible for this account. Must follow rules.",
    )

    confirm = discord.ui.TextInput(
        label="Confirmation",
        placeholder='Type "Yes" to confirm you understand your responsibility.',
        style=discord.TextStyle.short,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        username = self.username.value
        confirm = self.confirm.value

        if confirm.strip().lower() != "yes":
            await interaction.response.send_message(
                "You must type `Yes` to confirm you agree to the server rules.",
                ephemeral=True,
            )
            return

        if not MC_USERNAME_PATTERN.match(username):
            await interaction.response.send_message(
                "Failed to add you to the whitelist. Please try again later.\nYou can DM a member of the committee to manually whitelist you.",
                ephemeral=True,
            )
            return

        with open(enums.FileLocations.MCData.value, "r", encoding="utf-8") as f:
            data = json.load(f)

        data[username] = str(interaction.user.id)

        with open(enums.FileLocations.MCData.value, "w", encoding="utf-8") as f:
            json.dump(data, f)

        async with aiohttp.ClientSession() as session:
            await session.post(
                mc_whitelist_webhook_url,
                json={
                    "content": f"<@{interaction.user.id}> whitelisted the Minecraft account `{username}`"
                },
            )

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
    await bot.add_cog(Minecraft(bot))
