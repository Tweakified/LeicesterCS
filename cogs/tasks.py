import discord
from discord.ext import commands, tasks
from discord import app_commands
from typing import Optional
from itertools import cycle

# Custom modules
from modules import enums
import time
import json


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
    async def status(self, interaction: discord.Interaction, text: Optional[str]):
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
        with open(enums.FileLocations.UpTime.value, "w") as f:
            json.dump({"Time": int(time.time())}, f, indent=2)

        await self.bot.change_presence(activity=discord.Game(next(self.activity)))


async def setup(bot):
    await bot.add_cog(Tasks(bot))
