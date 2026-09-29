import time
from itertools import cycle

import discord
from discord import app_commands
from discord.ext import commands, tasks

# Custom modules
from modules import enums
from modules.utils import save_json


class Tasks(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot
        print(f"{__name__} cog loaded.")

        self.activity = cycle(["/help", "Leicester CS bot", '"About me" for more'])

        self.start_tasks()

    def start_tasks(self):
        self.activityUpdate.start()

    # RELATED COMMANDS

    @app_commands.checks.has_any_role(enums.Roles.Administration.value)
    @app_commands.checks.cooldown(1, 30)
    @app_commands.command(
        name="status",
        description="Update the bot's status message. To remove the status, do not provide any parameter.",
    )
    async def status(self, interaction: discord.Interaction, text: str | None):
        if text is None:
            if self.activityUpdate.is_running() is False:
                self.activityUpdate.start()
            else:
                await interaction.response.send_message(
                    ":x: Custom status is already cleared."
                )
                return

            await interaction.response.send_message(":pencil: Custom status cleared.")

            return

        self.activityUpdate.cancel()

        await self.bot.change_presence(activity=discord.Game(text))

        await interaction.response.send_message(
            f":pencil: Custom status set to `{text}`."
        )

    # Discord status task
    @tasks.loop(seconds=30)
    async def activityUpdate(self):
        await save_json(
            enums.FileLocations.UpTime.value, {"Time": int(time.time())}, indent=2
        )

        await self.bot.change_presence(activity=discord.Game(next(self.activity)))


async def setup(bot):
    await bot.add_cog(Tasks(bot))
