import aiohttp
import os
import re
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from mcstatus import JavaServer
from modules import enums
from modules.utils import ensure_json_exists
import traceback
import json
from typing import List

load_dotenv()

verified_role_id = int(os.getenv("VERIFIED_ROLE_ID"))
dmu_verified_role_id = int(os.getenv("DMU_VERIFIED_ROLE_ID"))
get_verified_channel = int(os.getenv("GET_VERIFIED_CHANNEL"))
mc_whitelist_channel = int(os.getenv("MC_WHITELIST_CHANNEL"))
mcsmanager_host = os.getenv("MCSMANAGER_HOST")
mcsmanager_token = os.getenv("MCSMANAGER_API_KEY")
mcsmanager_daemon_id = os.getenv("MCSMANAGER_DAEMON_ID")
mcsmanager_instance_id = os.getenv("MCSMANAGER_INSTANCE_ID")
mc_whitelisted_role_id = int(os.getenv("MC_WHITELISTED_ROLE_ID"))
mc_address = os.getenv("MC_ADDRESS")
mc_port = os.getenv("MC_PORT")

MC_USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,16}$")
mcs_command_url = f"{mcsmanager_host}/api/protected_instance/command"


async def unwhitelist_pipeline(minecraft_usernames: List[str]):
    params = {
        "apikey": mcsmanager_token,
        "uuid": mcsmanager_instance_id,
        "daemonId": mcsmanager_daemon_id,
        "command": "; ".join([f"whitelist remove {u}" for u in minecraft_usernames]),
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(mcs_command_url, params=params) as resp:
            return resp.status == 200


async def unwhitelist_account(
    interaction: discord.Interaction, discord_id: str, respond: bool = True
):
    with open(enums.FileLocations.MCData.value, "r", encoding="utf-8") as f:
        data = json.load(f)

    removed_usernames = []

    if discord_id not in data:
        if respond:
            await interaction.response.send_message(
                "No Minecraft accounts found to unwhitelist.",
                ephemeral=True,
            )
        return

    removed_usernames = data.pop(discord_id, [])
    pretty_removed_usernames = ", ".join(f"`{u}`" for u in removed_usernames)

    member = interaction.guild.get_member(int(discord_id))
    if member:
        role = interaction.guild.get_role(mc_whitelisted_role_id)
        if role in member.roles:
            await member.remove_roles(role)

    with open(enums.FileLocations.MCData.value, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    success = await unwhitelist_pipeline(removed_usernames)
    if respond:
        if success:
            await interaction.response.send_message(
                f"Successfully removed whitelisted account(s): {pretty_removed_usernames}",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "Failed to remove the Minecraft account(s) from the whitelist. Please contact a member of the committee.",
                ephemeral=True,
            )


async def start_whitelist_process(interaction: discord.Interaction):
    # Ensure they’re verified
    roles = interaction.user.roles
    if not any(role.id in (verified_role_id, dmu_verified_role_id) for role in roles):
        await interaction.response.send_message(
            f"You must complete email verification first. Go to <#{get_verified_channel}> or run /verify",
            ephemeral=True,
        )
        return

    with open(enums.FileLocations.Verify.value, "r", encoding="utf-8") as f:
        verify_data = json.load(f)

    if str(interaction.user.id) not in verify_data:
        await interaction.response.send_message(
            "Please run `/verify` first. We migrated to a new process as of the 13/09/2025 so you'll need to run verify again.",
            ephemeral=True,
        )
        return

    await interaction.response.send_modal(WhitelistModal())


class Minecraft(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        ensure_json_exists(enums.FileLocations.MCData.value)
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
        except Exception:
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
    @app_commands.checks.has_any_role(verified_role_id, dmu_verified_role_id)
    async def whitelist(self, interaction: discord.Interaction):
        await start_whitelist_process(interaction)

    @app_commands.checks.has_any_role(mc_whitelisted_role_id)
    @app_commands.command(
        name="unwhitelist", description="Remove Minecraft accounts from the whitelist."
    )
    async def unwhitelist(self, interaction: discord.Interaction):
        await unwhitelist_account(interaction, str(interaction.user.id))

    @app_commands.checks.has_any_role(enums.Roles.Management.value)
    @app_commands.command(
        name="mod_unwhitelist",
        description="(Mod) Remove Minecraft accounts from the whitelist.",
    )
    async def mod_unwhitelist(
        self,
        interaction: discord.Interaction,
        discord_acc: discord.Member = None,
        mc_username: str = None,
    ):
        if not discord_acc and not discord_acc:
            await interaction.response.send_message(
                "You must provide either a Discord account or a Minecraft username.",
                ephemeral=True,
            )
            return

        if discord_acc and mc_username:
            await interaction.response.send_message(
                "Please provide either a Discord account or a Minecraft username, not both.",
                ephemeral=True,
            )
            return

        if discord_acc:
            await unwhitelist_account(interaction, str(discord_acc.id))
            return

        if mc_username:
            with open(enums.FileLocations.MCData.value, "r", encoding="utf-8") as f:
                data = json.load(f)

            username_lower = mc_username.strip().lower()
            target_discord_id = None

            for discord_id, usernames in data.items():
                if username_lower in [u.lower() for u in usernames]:
                    target_discord_id = discord_id
                    break

            if not target_discord_id:
                await interaction.response.send_message(
                    f"No user found linked to Minecraft account `{mc_username}`.",
                    ephemeral=True,
                )
                return

            await unwhitelist_account(interaction, target_discord_id)

    @app_commands.command(
        name="update-whitelist-message",
        description="Update the whitelist message in the whitelist channel.",
    )
    @app_commands.checks.has_any_role(enums.Roles.Administration.value)
    async def update_whitelistmessage(self, interaction: discord.Interaction):
        channel = self.bot.get_channel(mc_whitelist_channel)

        embed = discord.Embed(
            title="<:ada:1416635217283776573> Minecraft Whitelist",
            description=(
                "To whitelist a Minecraft username on the server, click the start button below. "
                "You must ensure that the player follows all of our server rules, as you will be responsible for their actions. "
                f"Your student email must be verified to use this feature. Please see <#{get_verified_channel}> for more information."
            ),
            color=discord.Color.green(),
        )
        embed.add_field(
            name="Consent",
            value=(
                ":warning: By completing the whitelisting process, you consent to the collection and processing of this data as described in the privacy policy button."
            ),
            inline=False,
        )
        embed.set_footer(text="LeicesterMC Whitelist")

        await channel.send(embed=embed, view=WhitelistButtons())
        await interaction.response.send_message(
            f"🔲 Whitelist message updated in {channel.mention}.", ephemeral=True
        )


class WhitelistButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Start", style=discord.ButtonStyle.green, custom_id="whitelist_button"
    )
    async def whitelist(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await start_whitelist_process(interaction)

    @discord.ui.button(
        label="Privacy Policy",
        style=discord.ButtonStyle.grey,
        custom_id="privacy_policy",
    )
    async def privacy_policy(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        embed = discord.Embed(
            title="<:ada:1416635217283776573> Minecraft Whitelist Privacy Policy",
            color=discord.Color.green(),
        )
        embed.add_field(
            name="Data Collected",
            value="We collect your Minecraft username and Discord user ID when you use our Minecraft whitelisting system.",
            inline=False,
        )
        embed.add_field(
            name="Purpose & Usage",
            value="This data is used only to:\n"
            "• Add your Minecraft username to our server whitelist.\n"
            "• Assist in moderation if necessary (e.g. handling rule violations).\n",
            inline=False,
        )
        embed.add_field(
            name="Retention & Expiry",
            value=(
                "Your Minecraft username and Discord user ID will be stored until "
                "your student email verification expires (1 year). After that, this data will be "
                "removed as part of our regular cleanup process. If you are banned from any of our services, "
                "your student email may be retained indefinitely to prevent re-registration across our services. "
                "Your Minecraft username and Discord ID may also be kept for moderation purposes, but will not be used for any other reason."
            ),
            inline=False,
        )
        embed.add_field(
            name="Data Removal",
            value="You may use `/unwhitelist` at any time to remove your Minecraft username and associated data from our systems. You may also use `/unverify` to remove your student email and its associated data. If you face any issues with this process, please contact a member of the committee.",
            inline=False,
        )
        embed.add_field(
            name="Data Access",
            value="Your data is only accessible to current members of the committee and the designated data handler (bot host) for security and administration purposes. It will not be shared with third parties.",
            inline=False,
        )
        embed.set_footer(text="LeicesterMC Privacy Policy")
        await interaction.response.send_message(embed=embed, ephemeral=True)


class WhitelistModal(discord.ui.Modal, title="Minecraft Whitelist"):
    username = discord.ui.TextInput(
        label="Minecraft Username",
        placeholder="⚠️ You are responsible for this account. Must follow rules.",
    )

    confirm = discord.ui.TextInput(
        label="Responsibility Confirmation",
        placeholder='Type "Yes" to confirm you understand your responsibility.',
        style=discord.TextStyle.short,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        username = self.username.value
        confirm = self.confirm.value

        if confirm.strip().lower() != "yes":
            await interaction.response.send_message(
                "You didn't type `Yes` in the `Responsibility Confirmation` field.\nYou must confirm you understand your responsibility to the Minecraft account and agree to the server rules.",
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

        discord_id = str(interaction.user.id)
        if discord_id not in data:
            data[discord_id] = []

        for temp_discordId, usernames in data.items():
            if username.lower() in [u.lower() for u in usernames]:
                await interaction.response.send_message(
                    "This Minecraft account is already whitelisted.",
                    ephemeral=True,
                )
                return

        data[discord_id].append(username)

        with open(enums.FileLocations.MCData.value, "w", encoding="utf-8") as f:
            json.dump(data, f)

        role = interaction.guild.get_role(mc_whitelisted_role_id)
        await interaction.user.add_roles(role)

        params = {
            "apikey": mcsmanager_token,
            "uuid": mcsmanager_instance_id,
            "daemonId": mcsmanager_daemon_id,
            "command": f"whitelist add {username}",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(mcs_command_url, params=params) as resp:
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
