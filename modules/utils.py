import os
import json


def ensure_json_exists(file_path: str, empty_strutrure=None):
    if not os.path.exists(file_path):
        if empty_strutrure is None:
            empty_strutrure = {}
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(empty_strutrure, f)
