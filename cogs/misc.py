import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

# Custom modules
from modules import enums


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print(f"{__name__} cog loaded.")

    @app_commands.command(name="ping", description="Get the bot's response time")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f":stopwatch: Ping: **{round(self.bot.latency * 1000)} ms**"
        )

    @app_commands.command(name="help", description="Bot commands and information")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Help",
            description="I am the offical bot for the Leicester CS discord. To ask for support please contact a member of the committee.",
            color=enums.EmbedStyle.Round.value,
        )
        embed.add_field(
            name="Committee Contacts",
            value="Kieran `President` <@514100882661572619>\nNauman `Treasurer` <@1169668330567766169>\nKaranveer `Wellbeing` <@755453886248255719>\nSwayam `Social Sec` <@671774120131821648>\nJacinta `Publicity` <@993198933390151770>\nNeha `Publicity` <@1337718703290060812>\nShreya `Events Co-ordinator` <@1337738846095282199>\nPushkar `Sports Ambassador` <@649605009025007656>",
            inline=False,
        )
        embed.add_field(
            name="Contributions",
            value="Want to contribute to the bot? Check out the [GitHub repository](https://github.com/Tweakified/LeicesterCS) to get started.",
            inline=False,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="social", description="Official social channels")
    async def social(self, interaction: discord.Interaction):
        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label="Instagram",
                style=discord.ButtonStyle.blurple,
                url="https://www.instagram.com/uol_computerscience/",
            )
        )
        view.add_item(
            discord.ui.Button(
                label="Discord",
                style=discord.ButtonStyle.gray,
                url="https://discord.gg/VAg2SQfhEq",
            )
        )
        view.add_item(
            discord.ui.Button(
                label="LinkedIn",
                style=discord.ButtonStyle.secondary,
                url="https://www.linkedin.com/company/leicestercs",
            )
        )
        view.add_item(
            discord.ui.Button(
                label="WhatsApp",
                style=discord.ButtonStyle.green,
                url="https://chat.whatsapp.com/L01bDxP2tFWLf7p9QNbLyh",
            )
        )
        view.add_item(
            discord.ui.Button(
                label="Facebook",
                style=discord.ButtonStyle.primary,
                url="https://www.facebook.com/UoLCompSoc/",
            )
        )
        view.add_item(
            discord.ui.Button(
                label="Twitter",
                style=discord.ButtonStyle.danger,
                url="https://twitter.com/uolcompsoc",
            )
        )

        await interaction.response.send_message(
            ":thumbsup: Leicester CS **social channels**", view=view
        )

    @app_commands.command(name="slowmode", description="Set channel slowmode")
    @app_commands.checks.has_any_role(enums.Roles.Administration.value)
    async def slowmode(self, interaction: discord.Interaction, seconds: int):
        await interaction.channel.edit(slowmode_delay=seconds)
        await interaction.response.send_message(
            f":white_check_mark: {interaction.channel.mention} slowmode set to **{seconds} seconds**.",
            ephemeral=True,
        )

    @app_commands.command(name="utc", description="See UTC time")
    async def utc(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Time")

        utc = int(datetime.now().timestamp())

        embed.add_field(
            name="UTC - Coordinated Universal Time",
            value=datetime.utcnow().strftime("%d. %m. %Y %H:%M:%S"),
            inline=False,
        )
        embed.add_field(name="Your local time", value=f"<t:{utc}:d> <t:{utc}:T>")

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Misc(bot))
