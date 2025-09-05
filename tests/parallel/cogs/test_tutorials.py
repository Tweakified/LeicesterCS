import pytest

from unittest.mock import AsyncMock, patch, PropertyMock
import discord

import sys
import importlib
from pathlib import Path

OLD_PATH = Path("old")
NEW_PATH = Path("new")

sys.path.insert(0, str(OLD_PATH))
old = importlib.import_module("old.cogs.tutorials")
sys.path.insert(0, str(NEW_PATH))
new = importlib.import_module("new.cogs.tutorials")

assert old is not new, "Modules should be different"

async def retrieve_module_information(code: str, view, interaction) -> dict:
    with patch.object(discord.ui.Select, 'values', new_callable=PropertyMock) as mock_on_select_values:
        mock_on_select_values.return_value = [code]
        await view.on_select.callback(interaction)

    interaction.user.send.assert_called_once()
    embed = interaction.user.send.call_args[1]["embed"]

    interaction.followup.send.assert_called_once()
    args, kwargs = interaction.followup.send.call_args

    option = [option for option in view.on_select.options if option.label == code][0]

    return {
        "option": {"label": option.label, "description": option.description},
        "embed": {"title": embed.title,
                  "description": embed.description,
                  "image": embed.image.url,
                  "fields": embed.fields,
                  "footer": embed.footer.text},
        "followup": {"message": args[0], "ephemeral": kwargs["ephemeral"]}
    }

codes = ["CO1102", "CO1105", "CO1106", "CO1107", "CO1108", "CO2101", "CO2102", "CO2301", "CO2124"]

@pytest.mark.asyncio
@pytest.mark.parametrize("code", [pytest.param(code, id=code) for code in codes])
async def test_on_select_embeds_match(code):
    interaction = AsyncMock()
    user = AsyncMock()
    interaction.user = user

    old_result = await retrieve_module_information(code, old.Tutorials(), interaction)
    interaction.reset_mock()

    result = await retrieve_module_information(code, new.Tutorials(), interaction)
    interaction.reset_mock()

    assert old_result["option"]["label"] == result["option"]["label"], f"Module code labels do not match for {code}"
    assert old_result["option"]["description"] == result["option"]["description"], f"Module descriptions do not match for {code}"

    assert old_result["embed"]["title"] == result["embed"]["title"], f"Titles do not match for {code}"
    assert old_result["embed"]["description"] == result["embed"]["description"], f"Descriptions do not match for {code}"
    assert old_result["embed"]["image"] == result["embed"]["image"], f"Images do not match for {code}"

    for old_field, new_field in zip(old_result["embed"]["fields"], result["embed"]["fields"]):
        assert old_field.name == new_field.name, f"Field names do not match for {code} (field {old_field.name})"
        assert old_field.value == new_field.value, f"Field values do not match for {code} (field {old_field.name})"
        assert old_field.inline == new_field.inline, f"Field inline values do not match for {code} (field {old_field.name})"

    assert old_result["embed"]["footer"] == result["embed"]["footer"], f"Footers do not match for {code}"

    assert old_result["followup"]["ephemeral"] == result["followup"]["ephemeral"], f"Ephemeral values do not match for {code}"
    assert old_result["followup"]["message"] == result["followup"]["message"], f"Followup messages do not match for {code}"
