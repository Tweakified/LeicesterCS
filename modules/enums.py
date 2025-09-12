from enum import Enum
from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv()

# DISCORD GUILDS


class Guild(Enum):
    LeicesterCS = int(os.getenv("LEICESTER_CS_ID"))


class Roles(Enum):
    """Roles in case they would have their name changed in the future."""

    Administration = "🌳 Root"
    Management = "💾 Committee"
    Staff = "💾 Committee"


class _guildChannels(Enum):
    Announcements = int(os.getenv("ANNOUNCEMENTS_CHANNEL_ID"))
    RoleAssign = 939540767611957279  # role assign channel is not used in newer versions of discord.


class GuildChannels(Enum):
    """Discord guild channels"""

    LeicesterCS = _guildChannels


class FileLocations(Enum):
    UpTime = os.path.join(BASE_DIR, "..", "uptime.json")
    Modules = os.path.join(BASE_DIR, "..", "data", "modules.json")
    MCData = os.path.join(BASE_DIR, "..", "data", "minecraft.json")


# COLOURS (HEX)


class Colours(Enum):
    """Embed left side colors."""

    Embed = 0x2F3136  # Dark theme embed background (round corners)
    LightGreen = 0x2ECC71
    LightRed = 0xE74C3C
    Turquoise = 0x1ABC9C
    Yellow = 0xF1C40F
    Orange = 0xF39C12
    DarkOrange = 0xE67E22
    LightBlue = 0x3498DB


# DISCORD EMBED STYLES


class EmbedStyle(Enum):
    """Custom embed styles, mainly so they can be easily changed there instead of all scripts. Round style changes the left color to match embeds dark theme background."""

    Round = Colours.Embed.value
    Database = Round


class _lists(Enum):
    """[INTERNAL] Trello lists"""

    Announcements = "64ca77c98a073058fb32b963"
    Rules = "64ca70bd5717f44c6afcf27a"


class TrelloLists(Enum):
    """Trello list keys"""

    LeicesterCS = _lists
