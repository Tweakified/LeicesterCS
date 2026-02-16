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

        bot.add_view(PronounRoleAssign_buttons())
        bot.add_view(YearRoleAssign_buttons())
        bot.add_view(CourseRoleAssign_buttons())
        bot.add_view(SecondaryCourseRoleAssign_buttons())
        bot.add_view(DegreeRoleAssign_buttons())

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
            title="<:Ada:1416635217283776573> Year Roles",
            description="Which year of study are you?",
        )

        await channel.send(embed=embed, view=YearRoleAssign_buttons())

        embed2 = discord.Embed(
            title="<:Ada:1416635217283776573> Pronoun Roles",
            description="What pronouns do you prefer?",
        )

        await channel.send(embed=embed2, view=PronounRoleAssign_buttons())

        embed3 = discord.Embed(
            title="<:Ada:1416635217283776573> Primary Course Roles",
            description="What is the main part of your course?",
        )

        await channel.send(embed=embed3, view=CourseRoleAssign_buttons())

        embed4 = discord.Embed(
            title="<:Ada:1416635217283776573> Secondary Course Roles",
            description="What are the other parts of your course?",
        )

        await channel.send(embed=embed4, view=SecondaryCourseRoleAssign_buttons())

        embed5 = discord.Embed(
            title="<:Ada:1416635217283776573> Degree Type Roles",
            description="What degree level are you studying towards?",
        )

        await channel.send(embed=embed5, view=DegreeRoleAssign_buttons())

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
        label="Foundation Year",
        style=discord.ButtonStyle.gray,
        emoji="🏗️",
        custom_id="foundation_year",
    )
    async def found(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.role_update(interaction, "🧱 Foundation")

    @discord.ui.button(
        label="First Year",
        style=discord.ButtonStyle.gray,
        emoji="1️⃣",
        custom_id="First_year",
    )
    async def year1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.role_update(interaction, "🎓 Year 1")

    @discord.ui.button(
        label="Second Year",
        style=discord.ButtonStyle.gray,
        row=2,
        emoji="2️⃣",
        custom_id="Second_year",
    )
    async def year2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.role_update(interaction, "🎓 Year 2")

    @discord.ui.button(
        label="Sandwich",
        style=discord.ButtonStyle.gray,
        row=2,
        emoji="🥪",
        custom_id="sandwich_year",
    )
    async def sandwich(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.role_update(interaction, "🥪 Sandwich")

    @discord.ui.button(
        label="Third Year",
        style=discord.ButtonStyle.gray,
        row=3,
        emoji="3️⃣",
        custom_id="Third_year",
    )
    async def year3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.role_update(interaction, "🎓 Year 3")

    @discord.ui.button(
        label="Postgraduate",
        style=discord.ButtonStyle.gray,
        row=3,
        emoji="🎓",
        custom_id="postgraduate",
    )
    async def postg(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.role_update(interaction, "📜 Postgraduate")


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
        label="He/him",
        style=discord.ButtonStyle.gray,
        emoji="♂️",
        custom_id="he_him",
    )
    async def hehim(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.role_update(interaction, "📝 He/him")

    @discord.ui.button(
        label="She/her",
        style=discord.ButtonStyle.gray,
        emoji="♀️",
        custom_id="she_her",
    )
    async def sheher(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.role_update(interaction, "📝 She/her")

    @discord.ui.button(
        label="They/them",
        style=discord.ButtonStyle.gray,
        row=2,
        emoji="⚧",
        custom_id="they_them",
    )
    async def theythem(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.role_update(interaction, "📝 They/them")

    @discord.ui.button(
        label="Other",
        style=discord.ButtonStyle.gray,
        row=2,
        emoji="❤️",
        custom_id="other_pronouns",
    )
    async def other(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.role_update(interaction, "📝 Other Pronouns")


class CourseRoleAssign_buttons(discord.ui.View):
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
        label="Computer Science",
        style=discord.ButtonStyle.gray,
        emoji="🖥️",
        custom_id="computer_science",
    )
    async def computerscience(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.role_update(interaction, "🔷 Computer Science")

    @discord.ui.button(
        label="Creative Computing",
        style=discord.ButtonStyle.gray,
        emoji="🎨",
        custom_id="creative_computing",
    )
    async def creativecomputing(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.role_update(interaction, "🔷 Creative Computing")

    @discord.ui.button(
        label="Software Engineering",
        style=discord.ButtonStyle.gray,
        row=2,
        emoji="🔧",
        custom_id="software_engineering",
    )
    async def softwareengineering(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.role_update(interaction, "🔷 Software Engineering")

    @discord.ui.button(
        label="AI and Data Science",
        style=discord.ButtonStyle.gray,
        row=2,
        emoji="🥼",
        custom_id="ai_and_data_science",
    )
    async def aianddatascience(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.role_update(interaction, "🔷 AI and Data Science")

    @discord.ui.button(
        label="Mathematics",
        style=discord.ButtonStyle.gray,
        row=3,
        emoji="📊",
        custom_id="mathematics",
    )
    async def mathematics(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.role_update(interaction, "🔷 Mathematics")


class SecondaryCourseRoleAssign_buttons(discord.ui.View):
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
        label="with AI",
        style=discord.ButtonStyle.gray,
        emoji="👾",
        custom_id="with_ai",
    )
    async def withai(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.role_update(interaction, "🔹 with AI")

    @discord.ui.button(
        label="with Cyber Security",
        style=discord.ButtonStyle.gray,
        emoji="👩‍💻",
        custom_id="with_cyber_sec",
    )
    async def withcybersec(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.role_update(interaction, "🔹 with Cyber Security")

    @discord.ui.button(
        label="and Actuarial Science",
        style=discord.ButtonStyle.gray,
        row=2,
        emoji="🧪",
        custom_id="with_actuarial",
    )
    async def withactuarial(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.role_update(interaction, "🔹 and Actuarial Science")

    @discord.ui.button(
        label="with Year in Industry",
        style=discord.ButtonStyle.gray,
        row=2,
        emoji="💼",
        custom_id="with_placement",
    )
    async def withplacement(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.role_update(interaction, "🔸 with Year in Industry")

    @discord.ui.button(
        label="with Year Abroad",
        style=discord.ButtonStyle.gray,
        row=3,
        emoji="🌍",
        custom_id="with_abroad",
    )
    async def withabroad(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.role_update(interaction, "🔸 with Year Abroad")

    @discord.ui.button(
        label="with Foundation Year",
        style=discord.ButtonStyle.gray,
        row=3,
        emoji="🏗",
        custom_id="with_foundation",
    )
    async def withfoundation(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.role_update(interaction, "🔸 with Foundation Year")


class DegreeRoleAssign_buttons(discord.ui.View):
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
        label="BSc",
        style=discord.ButtonStyle.gray,
        emoji="👨‍🔬",
        custom_id="bsc",
    )
    async def bsc(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.role_update(interaction, "🔶 BSc")

    @discord.ui.button(
        label="MComp",
        style=discord.ButtonStyle.gray,
        emoji="💻",
        custom_id="mcomp",
    )
    async def mcomp(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.role_update(interaction, "🔶 MComp")

    @discord.ui.button(
        label="BEng",
        style=discord.ButtonStyle.gray,
        row=2,
        emoji="⚡",
        custom_id="beng",
    )
    async def beng(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.role_update(interaction, "🔶 BEng")

    @discord.ui.button(
        label="MMath",
        style=discord.ButtonStyle.gray,
        row=2,
        emoji="📈",
        custom_id="mmath",
    )
    async def mmath(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.role_update(interaction, "🔶 MMath")
