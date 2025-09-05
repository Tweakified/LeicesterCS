import discord
from discord.ext import commands
from discord import app_commands
import os
from trello import TrelloApi

# Custom modules
from modules import enums

trello_key = os.getenv("TRELLO_KEY")
trello_token = os.getenv("TRELLO_TOKEN")

trello = None
if trello_key and trello_token:
    trello = TrelloApi(trello_key)
    trello.set_token(trello_token)


class Guild(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot
        print(f"{__name__} cog loaded.")

        bot.add_view(YearRoleAssign_buttons())
        bot.add_view(SocialRoleAssign_buttons())
        bot.add_view(PronounRoleAssign_buttons())

    @app_commands.checks.has_any_role(enums.Roles.Administration.value)
    @app_commands.guild_only()
    @app_commands.command(
        name="update-rules", description="Update the rules in the rules channel"
    )
    async def update_rules(self, interaction: discord.Interaction):
        channel = interaction.guild.rules_channel

        guild_name = enums.Guild(interaction.guild.id).name
        rules_list_id = enums.TrelloLists[guild_name].value.Rules.value

        list = [card for card in trello.lists.get_card(rules_list_id)]

        first_card = list[0]
        first_card_name = first_card["name"].split("|", 1)
        first_embed = discord.Embed(
            title=first_card_name[0], description=first_card_name[1]
        )
        first_embed.set_image(url=first_card["desc"])

        main_embed = discord.Embed()
        for card in list[1:-1]:
            main_embed.add_field(name=card["name"], value=card["desc"], inline=False)

        last_embed = discord.Embed(title=list[-1]["name"], description=list[-1]["desc"])

        embeds = [first_embed, main_embed, last_embed]

        async for message in channel.history(limit=50, oldest_first=True):
            if message.author == self.bot.user:
                await message.edit(embeds=embeds)
                await interaction.response.send_message(
                    f"📒 Rules updated in {channel.mention}.", ephemeral=True
                )
                return

        await channel.send(embeds=embeds)

        await interaction.response.send_message(
            f"📒 Rules updated in {channel.mention}.", ephemeral=True
        )

    @app_commands.command(
        name="update-role-assign",
        description="Update the role assign message in the role assign channel.",
    )
    @app_commands.checks.has_any_role(enums.Roles.Administration.value)
    @app_commands.guild_only()
    @app_commands.guilds(discord.Object(id=enums.Guild.LeicesterCS.value))
    async def update_roleassign(self, interaction: discord.Interaction):
        channel = self.bot.get_channel(
            enums.GuildChannels.LeicesterCS.value.RoleAssign.value
        )

        if channel is None:
            interaction.response.send_message(":x: Channel not found.")
            return

        embed = discord.Embed(
            title="Role assign",
            description="Assign roles to yourself!\nWhich year are you in?",
        )

        embed.add_field(name="🏗️ Foundation year", value="Foundation year")
        embed.add_field(name="1️⃣ Year 1", value="First year")
        embed.add_field(name="2️⃣ Year 2", value="Second year")
        embed.add_field(name="🥪 Year in Industry/Abroad", value="Year in Industry")
        embed.add_field(name="3️⃣ Year 3", value="Third year")
        embed.add_field(name="🎓 Postgraduate", value="Postgraduate")

        await channel.send(embed=embed, view=YearRoleAssign_buttons())

        embed2 = discord.Embed(
            title="Role assign", description="What are your pronouns?"
        )

        embed2.add_field(name=":male_sign: He/him", value="He/him")
        embed2.add_field(name=":female_sign: She/her", value="She/her")
        embed2.add_field(name=":transgender_symbol: They/them", value="They/them")
        embed2.add_field(name=":heart: Other", value="Other pronouns")

        await channel.send(embed=embed2, view=PronounRoleAssign_buttons())

        embed3 = discord.Embed(
            title="Role assign", description="What do you want notifications for?"
        )

        embed3.add_field(name="🖥️ Hackathons", value="Hackathons")
        embed3.add_field(name="📢 Talks", value="Talks")
        embed3.add_field(name="🍹 Socials", value="Socials")

        await channel.send(embed=embed3, view=SocialRoleAssign_buttons())

        await interaction.response.send_message(
            f"🔲 Role assign message updated in {channel.mention}.", ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Guild(bot))


def key(interaction: discord.Interaction):
    return interaction.user


class YearRoleAssign_buttons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cd = commands.CooldownMapping.from_cooldown(6, 10, key)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        retry_after = self.cd.update_rate_limit(interaction)

        if retry_after:
            await interaction.response.send_message(
                f":stopwatch: Slow down! Try again in **{int(retry_after)} seconds**.",
                ephemeral=True,
            )
            return False
        else:
            return True

    async def role_update(self, interaction: discord.Interaction, role_name):
        role = discord.utils.get(interaction.guild.roles, name=role_name)

        if role not in interaction.user.roles:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                f":black_square_button: {role.mention} role **added**.", ephemeral=True
            )
        else:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(
                f":black_square_button: {role.mention} role **removed**.",
                ephemeral=True,
            )

        return

    @discord.ui.button(
        label="Foundation year",
        style=discord.ButtonStyle.gray,
        emoji="🏗️",
        custom_id="foundation_year",
    )
    async def found(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.role_update(interaction, "Foundation year")

    @discord.ui.button(
        label="First year",
        style=discord.ButtonStyle.gray,
        emoji="1️⃣",
        custom_id="First_year",
    )
    async def year1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.role_update(interaction, "Year 1")

    @discord.ui.button(
        label="Second year",
        style=discord.ButtonStyle.gray,
        emoji="2️⃣",
        custom_id="Second_year",
    )
    async def year2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.role_update(interaction, "Year 2")

    @discord.ui.button(
        label="Year in Industry",
        style=discord.ButtonStyle.gray,
        row=2,
        emoji="🥪",
        custom_id="sandwich_year",
    )
    async def sandwich(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.role_update(interaction, "Year in Industry/Abroad")

    @discord.ui.button(
        label="Third year",
        style=discord.ButtonStyle.gray,
        row=2,
        emoji="3️⃣",
        custom_id="Third_year",
    )
    async def year3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.role_update(interaction, "Year 3")

    @discord.ui.button(
        label="Postgraduate",
        style=discord.ButtonStyle.gray,
        row=2,
        emoji="🎓",
        custom_id="postgraduate",
    )
    async def postg(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.role_update(interaction, "Postgraduate")


class PronounRoleAssign_buttons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cd = commands.CooldownMapping.from_cooldown(6, 10, key)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        retry_after = self.cd.update_rate_limit(interaction)

        if retry_after:
            await interaction.response.send_message(
                f":stopwatch: Slow down! Try again in **{int(retry_after)} seconds**.",
                ephemeral=True,
            )
            return False
        else:
            return True

    async def role_update(self, interaction: discord.Interaction, role_name):
        role = discord.utils.get(interaction.guild.roles, name=role_name)

        if role not in interaction.user.roles:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                f":black_square_button: {role.mention} role **added**.", ephemeral=True
            )
        else:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(
                f":black_square_button: {role.mention} role **removed**.",
                ephemeral=True,
            )

        return

    @discord.ui.button(
        label="♂️ He/him", style=discord.ButtonStyle.gray, custom_id="he_him"
    )
    async def hehim(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.role_update(interaction, "He/him")

    @discord.ui.button(
        label="♀️ She/her", style=discord.ButtonStyle.gray, custom_id="she_her"
    )
    async def sheher(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.role_update(interaction, "She/her")

    @discord.ui.button(
        label="⚧️ They/them", style=discord.ButtonStyle.gray, custom_id="they_them"
    )
    async def theythem(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.role_update(interaction, "They/them")

    @discord.ui.button(
        label="Other",
        style=discord.ButtonStyle.gray,
        emoji="❤️",
        custom_id="other_pronouns",
    )
    async def other(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.role_update(interaction, "Other pronouns")


class SocialRoleAssign_buttons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cd = commands.CooldownMapping.from_cooldown(6, 10, key)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        retry_after = self.cd.update_rate_limit(interaction)

        if retry_after:
            await interaction.response.send_message(
                f":stopwatch: Slow down! Try again in **{int(retry_after)} seconds**.",
                ephemeral=True,
            )
            return False
        else:
            return True

    async def role_update(self, interaction: discord.Interaction, role_name):
        role = discord.utils.get(interaction.guild.roles, name=role_name)

        if role not in interaction.user.roles:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                f":black_square_button: {role.mention} role **added**.", ephemeral=True
            )
        else:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(
                f":black_square_button: {role.mention} role **removed**.",
                ephemeral=True,
            )

        return

    @discord.ui.button(
        label="Hackathons",
        style=discord.ButtonStyle.gray,
        emoji="🖥️",
        custom_id="hackathons",
    )
    async def updates(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.role_update(interaction, "Hackathon Ping")

    @discord.ui.button(
        label="Talks", style=discord.ButtonStyle.gray, emoji="📢", custom_id="talks"
    )
    async def news(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.role_update(interaction, "Talks Ping")

    @discord.ui.button(
        label="Socials", style=discord.ButtonStyle.gray, emoji="🍹", custom_id="socials"
    )
    async def gamenights(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.role_update(interaction, "Social Ping")
