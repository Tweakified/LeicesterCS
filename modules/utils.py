import asyncio
import json
import os


def ensure_json_exists(file_path: str, empty_strutrure=None):
    if not os.path.exists(file_path):
        if empty_strutrure is None:
            empty_strutrure = {}
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(empty_strutrure, f)


async def load_json(file_path: str):
    return await asyncio.to_thread(_load_json, file_path)


def _load_json(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


async def save_json(file_path: str, data, **kwargs):
    await asyncio.to_thread(_save_json, file_path, data, kwargs)


def _save_json(file_path: str, data, kwargs):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, **kwargs)
