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
mc_whitelisted_role_id = int(os.getenv("MC_WHITELISTED_ROLE_ID"))
mc_address = os.getenv("MC_ADDRESS")
mc_port = os.getenv("MC_PORT")

MC_USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,16}$")


async def unwhitelist_account(interaction: discord.Interaction, discord_id: str):
    with open(enums.FileLocations.MCData.value, "r", encoding="utf-8") as f:
        data = json.load(f)

    removed_usernames = []

    if discord_id not in data:
        await interaction.response.send_message(
            "No Minecraft accounts found to unwhitelist.",
            ephemeral=True,
        )
        return

    removed_usernames = data.pop(discord_id, [])
    member = interaction.guild.get_member(int(discord_id))
    if member:
        role = interaction.guild.get_role(mc_whitelisted_role_id)
        if role in member.roles:
            await member.remove_roles(role)

    with open(enums.FileLocations.MCData.value, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    for removed_username in removed_usernames:
        url = f"{mcsmanager_host}/api/protected_instance/command"
        params = {
            "apikey": mcsmanager_token,
            "uuid": mcsmanager_instance_id,
            "daemonId": mcsmanager_daemon_id,
            "command": f"whitelist remove {removed_username}",
        }
        async with aiohttp.ClientSession() as session:
            await session.post(url, params=params)

    await interaction.response.send_message(
        f"Successfully unwhitelisted: {', '.join(removed_usernames)}",
        ephemeral=True,
    )


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
    @app_commands.checks.has_any_role(1414992207282442300)  # Temp Beta tester role
    async def whitelist(self, interaction: discord.Interaction):
        # Ensure they’re verified
        roles = interaction.user.roles
        if not any(
            role.id in (verified_role_id, dmu_verified_role_id) for role in roles
        ):
            await interaction.response.send_message(
                f"You must complete email verification first. Go to <#{get_verified_channel}> or run /verify",
                ephemeral=True,
            )
            return

        await interaction.response.send_modal(WhitelistModal())

    @app_commands.checks.has_any_role(mc_whitelisted_role_id)
    @app_commands.command(
        name="unwhitelist", description="Remove Minecraft accounts from the whitelist."
    )
    async def unwhitelist(interaction: discord.Interaction):
        await unwhitelist_account(interaction, str(interaction.user.id))

    @app_commands.checks.has_any_role(enums.Roles.Management.value)
    @app_commands.command(
        name="unwhitelist",
        description="(Mod) Remove Minecraft accounts from the whitelist.",
    )
    async def mod_unwhitelist(
        interaction: discord.Interaction,
        member: discord.Member = None,
        username: str = None,
    ):
        if not member and not username:
            await interaction.response.send_message(
                "You must provide either a Discord member or a Minecraft username.",
                ephemeral=True,
            )
            return

        if member and username:
            await interaction.response.send_message(
                "Please provide either a Discord member or a Minecraft username, not both.",
                ephemeral=True,
            )
            return

        if member:
            await unwhitelist_account(interaction, str(member.id))
            return

        if username:
            with open(enums.FileLocations.MCData.value, "r", encoding="utf-8") as f:
                data = json.load(f)

            username_lower = username.strip().lower()
            target_discord_id = None

            for discord_id, usernames in data.items():
                if username_lower in [u.lower() for u in usernames]:
                    target_discord_id = discord_id
                    break

            if not target_discord_id:
                await interaction.response.send_message(
                    f"No user found linked to Minecraft account `{username}`.",
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
            title="🎮 Minecraft Whitelist",
            description=(
                "⚠️ By whitelisting a Minecraft account, **you are responsible for the user**.\n\n"
                "You must ensure that the player follows all of our server rules.\n"
                "By clicking the Start button below you agree to this."
            ),
            color=discord.Color.green(),
        )
        embed.set_footer(text="LeicesterMC Whitelist")

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
    async def whitelist(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(WhitelistModal())

    @discord.ui.button(
        label="Privacy Policy",
        style=discord.ButtonStyle.grey,
        custom_id="privacy_policy",
    )
    async def privacy_policy(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        embed = discord.Embed(title="Privacy Policy", color=discord.Color.green())
        embed.add_field(
            name="Data Collected",
            value="We only collect your **Minecraft username** and discord ID when you use `/whitelist`.",
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value="Your username is used **only** to add you to our Minecraft server whitelist.",
            inline=False,
        )
        embed.add_field(
            name="Usage",
            value="The data is strictly used for moderation and server access.",
            inline=False,
        )
        embed.add_field(
            name="Removal",
            value="Use `/unwhitelist` to remove your account, and your data will be **deleted immediately**.",
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

        discord_id = str(interaction.user.id)
        if discord_id not in data:
            data[discord_id] = []

        for temp_discordId, usernames in data.items():
            if username in [u.lower() for u in usernames]:
                await interaction.response.send_message(
                    "This Minecraft account is already verified by another Discord user.",
                    ephemeral=True,
                )
                return
        data[discord_id].append(username)

        with open(enums.FileLocations.MCData.value, "w", encoding="utf-8") as f:
            json.dump(data, f)

        role = interaction.guild.get_role(mc_whitelisted_role_id)
        await interaction.user.add_roles(role)

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
