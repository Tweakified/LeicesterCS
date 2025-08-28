import discord
import asyncio
from discord import app_commands
from discord.ext import commands


class Tutorials(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="Select a module",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="CO1102", description="Python Fundamentals"),
            discord.SelectOption(
                label="CO1105", description="Object Oriented Programming"
            ),
            discord.SelectOption(
                label="CO1106", description="Requirements Engineering"
            ),
            discord.SelectOption(
                label="CO1107", description="Python Programming & Algorithms"
            ),
            discord.SelectOption(
                label="CO1108", description="Foundations of Computation"
            ),
            discord.SelectOption(
                label="CO2101", description="Operating Systems and Networking"
            ),
            discord.SelectOption(
                label="CO2102", description="Databases & Domain Modelling"
            ),
            discord.SelectOption(label="CO2301", description="Project Management"),
            discord.SelectOption(
                label="CO2124",
                description="Software Architecture and System Development II",
            ),
        ],
    )
    async def on_select(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        embed = discord.Embed(
            title=f"Tutorial for {select.values[0]}",
            description="Here are some helpful tutorials/materials for this module",
            color=discord.Color.random(),
        )
        if select.values[0] == "CO1102":
            embed.set_image(
                url="https://cdn.freebiesupply.com/logos/large/2x/python-5-logo-png-transparent.png"
            )
            embed.add_field(
                name="Week 1",
                value="[Playlist](https://youtube.com/playlist?list=PLeVt6bfkArKeUHaPvDZIONynfnj3oyN5Y&si=5bIoxejRgdAEYoam)",
                inline=True,
            )
            embed.add_field(
                name="Week 2",
                value="[Playlist](https://www.youtube.com/playlist?list=PLeVt6bfkArKcWE9I9wZvv4Bbyd4e0Nvst)",
                inline=True,
            )
            embed.add_field(
                name="Week 3",
                value="[Playlist](https://www.youtube.com/playlist?list=PLeVt6bfkArKcLNCjLF0wUfWsoH64CtTfh&jct=ODlb5FmGrOHWXxwV4QyV3A)",
                inline=True,
            )
            embed.add_field(
                name="Week 4",
                value="[Playlist](https://youtube.com/playlist?list=PLeVt6bfkArKdmYvuMkYPaP3eeLpq6OPGt&si=5puLw5u2ZjhFC17T)",
                inline=True,
            )
            embed.add_field(
                name="Week 5",
                value="[Video](https://youtu.be/621C1FvvcCc?list=PLeVt6bfkArKc9GvP81JdNMw6j4K1BmttN)",
                inline=True,
            )
            embed.add_field(
                name="Week 6",
                value="[Playlist](https://www.youtube.com/playlist?list=PLeVt6bfkArKcLBDRLl6ZsJ0ans5C-rSHr)",
                inline=True,
            )
            embed.add_field(
                name="Week 7",
                value="[Playlist](https://www.youtube.com/playlist?list=PLeVt6bfkArKdTo7GTqxO-kXXqhrRivXL9)",
                inline=True,
            )
            embed.add_field(
                name="Week 8",
                value="[Playlist](https://youtube.com/playlist?list=PLeVt6bfkArKfPpT1z_fE9PJZrF6Afwc4o&si=0zOi6YwAhKWBtS0W)",
                inline=True,
            )
            embed.add_field(
                name="Week 9",
                value="[Video](https://youtu.be/q2SGW2VgwAM?si=VDlPbv59jsc8M3TM)",
                inline=True,
            )
            embed.add_field(
                name="Week 10",
                value="[Playlist](https://youtube.com/playlist?list=PLeVt6bfkArKfLRcApQxz69y_q-lpS9HbK&si=bW5sysAnl7ewuvkL)",
                inline=True,
            )
        elif select.values[0] == "CO1105":
            embed.set_image(
                url="https://cdn.freebiesupply.com/logos/large/2x/java-logo-png-transparent.png"
            )
            embed.add_field(
                name="Java Basics",
                value="[Link](https://www.codecademy.com/learn/java-introduction)",
                inline=True,
            )
            embed.add_field(
                name="Introduction to OOP",
                value="[Link](https://www.codecademy.com/learn/learn-java-object-oriented-programming)",
                inline=True,
            )
            embed.add_field(
                name="Inheritance & Polymorphism",
                value="[Link](https://www.codecademy.com/learn/learn-java-classes-and-methods)",
                inline=True,
            )
        elif select.values[0] == "CO1106":
            embed.set_image(
                url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Git_icon.svg/2048px-Git_icon.svg.png"
            )
            embed.add_field(
                name="Git",
                value="[Cheatsheet](https://education.github.com/git-cheat-sheet-education.pdf)",
                inline=True,
            )
        elif select.values[0] == "CO1107":
            embed.set_image(
                url="https://cdn.freebiesupply.com/logos/large/2x/python-5-logo-png-transparent.png"
            )
            embed.add_field(
                name="Week 2",
                value="[Playlist](https://www.youtube.com/playlist?list=PLeVt6bfkArKciyZXBQB4v48Z2ccA7L3El)",
                inline=True,
            )
            embed.add_field(
                name="Week 3",
                value="[Playlist](https://www.youtube.com/playlist?list=PLeVt6bfkArKdRvReeiigILJWhfepMHt6H)",
                inline=True,
            )
            embed.add_field(
                name="Week 4",
                value="[Video](https://youtu.be/m1Fjdnj_Mds)",
                inline=True,
            )
            embed.add_field(
                name="Week 5",
                value="[Playlist](https://www.youtube.com/playlist?list=PLeVt6bfkArKcKV42o5N8ITcGxnPCjCHdH)",
                inline=True,
            )
            embed.add_field(
                name="Week 6",
                value="[Video](https://youtu.be/JlMyYuY1aXU)",
                inline=True,
            )
            embed.add_field(
                name="Week 7",
                value="[Playlist](https://www.youtube.com/playlist?list=PLeVt6bfkArKdPM_kC0PWwlaG2-HswSa0g)",
                inline=True,
            )
            embed.add_field(
                name="Week 8",
                value="[Video](https://youtu.be/oSWTXtMglKE)",
                inline=True,
            )
        elif select.values[0] == "CO2101":
            embed.set_image(
                url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Tux.svg/1200px-Tux.svg.png"
            )
            embed.add_field(
                name="Anki Flashcards 1.1-5.1",
                value="[Flashcards](https://ankiweb.net/shared/info/127297956)",
                inline=True,
            )
            embed.add_field(
                name="Anki Flashcards 5.2-...",
                value="[Flashcards](https://ankiweb.net/shared/info/248961491)",
                inline=True,
            )
        elif select.values[0] == "CO2102":
            embed.set_image(
                url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Sql_data_base_with_logo.png/640px-Sql_data_base_with_logo.png"
            )
            embed.add_field(
                name="Week 1",
                value="[Playlist](https://www.youtube.com/playlist?list=PLeVt6bfkArKcDa27fwSMqOb7_LnAMeAOI)",
            )
            embed.add_field(
                name="Anki Flashcards",
                value="[Flashcards](https://ankiweb.net/shared/info/975442831)",
                inline=True,
            )
        elif select.values[0] == "CO2301":
            embed.set_image(url="https://static.thenounproject.com/png/3475197-200.png")
            embed.add_field(
                name="Anki Flashcards",
                value="[Flashcards](https://ankiweb.net/shared/info/203905190)",
            )
        elif select.values[0] == "CO2124":
            embed.set_image(
                url="https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/Spring_Boot.svg/220px-Spring_Boot.svg.png"
            )
            embed.add_field(
                name="Anki Flashcards",
                value="[Theory Flashcards](https://ankiweb.net/shared/info/1672898699)",
            )
        else:
            embed.set_image(
                url="https://cms-media.bartleby.com/wp-content/uploads/sites/2/2021/05/31175359/Theoretical-Computer-Science-1-1024x389.jpg"
            )
            embed.add_field(
                name="Theory",
                value="WIP! If you find any resources that would be helpful. Please reach out!",
                inline=True,
            )
        embed.set_footer(text="Tutorial resources created by: kaeini")
        await interaction.response.defer()
        user = interaction.user
        await user.send(embed=embed)
        await interaction.followup.send(
            f"The material for {select.values[0]} has been DM'd to you {user.mention}",
            ephemeral=True,
        )


class TutorialCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="tutorial", description="Select a module to view tutorials"
    )
    async def tutorial(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.followup.send(
            "Select a module from the dropdown below:", view=Tutorials(), ephemeral=True
        )
        await asyncio.sleep(15)
        await interaction.delete_original_response()


async def setup(bot: commands.Bot):
    await bot.add_cog(TutorialCog(bot))
