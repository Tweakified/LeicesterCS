import traceback
import discord
from discord.ext import commands, tasks
from discord import app_commands, ui
import random
import re
from datetime import datetime, timedelta
import time
import json
import os

# Custom modules
from modules import enums

from mailjet_rest import Client
from dotenv import load_dotenv
from cogs.minecraft import unwhitelist_account, unwhitelist_pipeline

load_dotenv()

verified_role_id = int(os.getenv("VERIFIED_ROLE_ID"))
dmu_verified_role_id = int(os.getenv("DMU_VERIFIED_ROLE_ID"))
get_verified_channel = int(os.getenv("GET_VERIFIED_CHANNEL"))
general_channel_id = int(os.getenv("GENERAL_CHANNEL_ID"))

api_key = os.getenv("MAIL_JET_KEY")
api_secret = os.getenv("MAIL_JET_SECRET")

mailjet = None
if api_key and api_secret:
    mailjet = Client(auth=(api_key, api_secret), version="v3.1")

regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"

welcome_messages = [
    "Glad to have you here {}",
    "Welcome to the show {}",
    "{} joined. This is gonna be epic.",
    "Hey {}, great to see you!",
    "{} just landed in the server!",
    "Everyone, give a warm welcome to {}!",
    "Look who's here! {}, welcome!",
    "A wild {} appeared!",
    "{} has entered the chat. Brace yourselves!",
]


def sendEmail(email, code):
    formatCode = "{:05d}".format(code)

    data = {
        "Messages": [
            {
                "From": {
                    "Email": "auth@tweakified.co.uk",
                    "Name": "Verification Email",
                },
                "To": [
                    {
                        "Email": email,
                    }
                ],
                "Subject": "Verification Email",
                "TextPart": "Hi,\n\nBelow is your verification code, please enter it in the Discord field: "
                + formatCode
                + "\n\nKind Regards,\nLeicester Computer Science Society.",
            }
        ]
    }
    result = mailjet.send.create(data=data)
    return result


async def verificationRequest(interaction):
    roles = interaction.user.roles
    if any(role.id in (verified_role_id, dmu_verified_role_id) for role in roles):
        await interaction.response.send_message(
            "You have already verified!", ephemeral=True
        )
    else:
        await interaction.response.send_modal(EmailModal())


class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not os.path.exists(enums.FileLocations.Verify.value):
            with open(enums.FileLocations.Verify.value, "w", encoding="utf-8") as f:
                json.dump({}, f)
        print(f"{__name__} cog loaded.")
        self.cleanup_task.start()
        bot.add_view(Verify_buttons())

    def cog_unload(self):
        self.cleanup_task.cancel()

    @app_commands.command(name="verify", description="Server verification")
    async def verify(self, interaction: discord.Interaction):
        await verificationRequest(interaction)

    @app_commands.command(
        name="unverify", description="Removes your data from the verify system."
    )
    async def unverify(self, interaction: discord.Interaction):
        roles = interaction.user.roles
        if not any(
            role.id in (verified_role_id, dmu_verified_role_id) for role in roles
        ):
            await interaction.response.send_message(
                "You are not verified!", ephemeral=True
            )
            return

        with open(enums.FileLocations.Verify.value, "r", encoding="utf-8") as f:
            data = json.load(f)

        if str(interaction.user.id) in data:
            data.pop(str(interaction.user.id), None)

            with open(enums.FileLocations.Verify.value, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

        await unwhitelist_account(interaction, str(interaction.user.id), False)

        roleIds = [verified_role_id, dmu_verified_role_id]
        userRoles = [role for role in roles if role.id in roleIds]

        if userRoles:
            await interaction.user.remove_roles(*userRoles)
            await interaction.response.send_message(
                "You have been unverified and your data has been removed.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "You do not have a verifed role.", ephemeral=True
            )

    @app_commands.command(
        name="update-verify-message",
        description="Update the verify message in the verify channel.",
    )
    @app_commands.checks.has_any_role(enums.Roles.Administration.value)
    async def update_verifymessage(self, interaction: discord.Interaction):
        channel = self.bot.get_channel(get_verified_channel)

        if channel is None:
            interaction.response.send_message(":x: Channel not found.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Email Verification",
            description="To be able talk in the server we have implemented a feature were you must verify your student email address.\nThis was made necessary to due bots.\n\nThis is a simple process that only takes a few minutes.",
        )
        embed.set_footer(text=interaction.guild.name + " Verification")

        await channel.send(embed=embed, view=Verify_buttons())
        await interaction.response.send_message(
            f"🔲 Verify message updated in {channel.mention}.", ephemeral=True
        )

    @tasks.loop(hours=24)
    async def cleanup_task(self):
        current_time = int(time.time())
        removed = []

        with open(enums.FileLocations.Verify.value, "r", encoding="utf-8") as f:
            verify_data = json.load(f)
        with open(enums.FileLocations.MCData.value, "r", encoding="utf-8") as f:
            mc_data = json.load(f)

        guild = self.bot.get_guild(enums.Guild.LeicesterCS.value)

        for discord_id, entry in list(verify_data.items()):
            if entry.get("expires") and current_time > entry["expires"]:
                removed.append(discord_id)
                verify_data.pop(discord_id, None)

                removed_usernames = mc_data.pop(discord_id, [])

                member = guild.get_member(int(discord_id))
                if member:
                    roleIds = [verified_role_id, dmu_verified_role_id]
                    roles_to_remove = [
                        role for role in member.roles if role.id in roleIds
                    ]

                    if roles_to_remove:
                        await member.remove_roles(*roles_to_remove)

                if removed_usernames:
                    await unwhitelist_pipeline(removed_usernames)

        with open(enums.FileLocations.Verify.value, "w", encoding="utf-8") as f:
            json.dump(verify_data, f, indent=4)
        with open(enums.FileLocations.MCData.value, "w", encoding="utf-8") as f:
            json.dump(mc_data, f, indent=4)

        if removed:
            print(
                f"[Cleanup] Removed {len(removed)} expired verification entries and their roles/accounts."
            )


class EmailModal(discord.ui.Modal, title="Enter Uni Email"):
    email = discord.ui.TextInput(
        label="Email",
        placeholder="Your uni email here...",
    )

    async def on_submit(self, interaction: discord.Interaction):
        email = self.email.value
        if not re.fullmatch(regex, email):
            await interaction.response.send_message(
                "Oops! Please enter a valid email", ephemeral=True
            )
            return

        domain = email[email.index("@") + 1 :]
        if (
            domain != "student.le.ac.uk"
            and domain != "leicester.ac.uk"
            and domain != "dmu.ac.uk"
        ):
            await interaction.response.send_message(
                "Oops! You must use your student email.", ephemeral=True
            )
            return

        code = random.randint(0, 99999)
        result = sendEmail(email, code)

        if result.status_code != 200:
            await interaction.response.send_message(
                "Oops! Something went wrong.", ephemeral=True
            )
            return

        await interaction.response.send_message(
            ":thumbsup: An email has been sent to the address you entered. Please press the button when you're ready",
            view=Ready_buttons(code, email, domain),
            ephemeral=True,
        )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        await interaction.response.send_message(
            "Oops! Something went wrong.", ephemeral=True
        )
        traceback.print_exception(type(error), error, error.__traceback__)


class Verify_buttons(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Verify", style=discord.ButtonStyle.green, custom_id="verify"
    )
    async def verify_button(self, interaction: discord.Interaction, button: ui.Button):
        await verificationRequest(interaction)

    @discord.ui.button(
        label="Privacy Policy",
        style=discord.ButtonStyle.grey,
        custom_id="verify_privacy_policy",
    )
    async def verify_privacy_policy(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        embed = discord.Embed(
            title="Student Email Verification Privacy Policy",
            color=discord.Color.green(),
        )
        embed.add_field(
            name="Data Collected",
            value="We collect your student email address and your Discord user ID when you complete the verification process.",
            inline=False,
        )
        embed.add_field(
            name="Purpose/Usage",
            value="This data is used only to:\n"
            "• Confirm your student status.\n"
            "• Enable participation in services that require student verification, such as our Minecraft server.\n"
            "• Assist in moderation if necessary (e.g., handling malicious behaviour).",
            inline=False,
        )
        embed.add_field(
            name="Retention & Expiry",
            value="Your email data will be stored for 1 year. After that, it will be automatically deleted and you will need to re-verify to continue accessing student-only services.",
            inline=False,
        )
        embed.add_field(
            name="Removal",
            value="You may use `/unverify` at any time to remove your email and associated data from our systems. This will also revoke your student access (including the Minecraft whitelist).",
            inline=False,
        )
        embed.set_footer(text=interaction.guild.name + " Verify Privacy Policy")

        await interaction.response.send_message(embed=embed, ephemeral=True)


class Ready_buttons(ui.View):
    def __init__(self, code, email, domain):
        super().__init__(timeout=None)
        self.codeSent = code
        self.email = email
        self.domain = domain

    @discord.ui.button(
        label="I Have It", style=discord.ButtonStyle.green, custom_id="ready"
    )
    async def verify_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(
            CodeModal(self.codeSent, self.email, self.domain)
        )


class CodeModal(discord.ui.Modal, title="Enter the Code"):
    def __init__(self, code, email, domain):
        super().__init__(timeout=None)
        self.codeSent = code
        self.email = email
        self.domain = domain

    code = discord.ui.TextInput(
        label="Code",
        placeholder="Enter your code here...",
    )

    async def on_submit(self, interaction: discord.Interaction):
        code = int(self.code.value)
        if code != int(self.codeSent):
            await interaction.response.send_message(
                "Oops! You entered the wrong code", ephemeral=True
            )
            return

        with open(enums.FileLocations.Verify.value, "r", encoding="utf-8") as f:
            data = json.load(f)

        expiry_time = int((datetime.utcnow() + timedelta(days=365)).timestamp())
        data[str(interaction.user.id)] = {"email": self.email, "expires": expiry_time}

        with open(enums.FileLocations.Verify.value, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        roleId = verified_role_id
        if self.domain == "dmu.ac.uk":
            roleId = dmu_verified_role_id
        role = interaction.guild.get_role(roleId)

        await interaction.user.add_roles(role)
        await interaction.response.send_message(
            f"You were given the <@&{str(roleId)}> role", ephemeral=True
        )

        general_channel = interaction.guild.get_channel(general_channel_id)
        if general_channel:
            message = random.choice(welcome_messages).format(interaction.user.mention)
            await general_channel.send(message)

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        await interaction.response.send_message(
            "Oops! Something went wrong.", ephemeral=True
        )
        traceback.print_exception(type(error), error, error.__traceback__)


async def setup(bot):
    await bot.add_cog(Verify(bot))
