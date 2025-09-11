import traceback
import discord
from discord.ext import commands
from discord import app_commands, ui
import random

# Custom modules
import os
from modules import enums
import re

from mailjet_rest import Client
from dotenv import load_dotenv

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
        print(f"{__name__} cog loaded.")
        bot.add_view(Verify_buttons())

    @app_commands.command(name="verify", description="Server verification")
    async def verify(self, interaction: discord.Interaction):
        await verificationRequest(interaction)

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
            view=Ready_buttons(code, domain),
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


class Ready_buttons(ui.View):
    def __init__(self, code, domain):
        super().__init__(timeout=None)
        self.codeSent = code
        self.domain = domain

    @discord.ui.button(
        label="I Have It", style=discord.ButtonStyle.green, custom_id="ready"
    )
    async def verify_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(CodeModal(self.codeSent, self.domain))


class CodeModal(discord.ui.Modal, title="Enter the Code"):
    def __init__(self, code, domain):
        super().__init__(timeout=None)
        self.codeSent = code
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

        roleId = verified_role_id
        if self.domain == "dmu.ac.uk":
            roleId = dmu_verified_role_id
        role = interaction.guild.get_role(roleId)

        await interaction.user.add_roles(role)
        # add to file
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
