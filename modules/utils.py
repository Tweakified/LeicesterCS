import os
import json


def ensure_json_exists(file_path: str):
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({}, f)
