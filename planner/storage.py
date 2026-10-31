import json
import os
import shutil

from .config import DATA_FILE, DEFAULT_SETTINGS, DEFAULT_SUBJECTS


def default_data():
    return {
        "subjects": DEFAULT_SUBJECTS.copy(),
        "tasks": [],
        "goals": [],
        "reminders": [],
        "sessions": [],
        "settings": DEFAULT_SETTINGS.copy(),
        "next_id": 1,
    }


def migrate(data):
    for key, value in default_data().items():
        data.setdefault(key, value)
    for key, value in DEFAULT_SETTINGS.items():
        data["settings"].setdefault(key, value)
    for task in data["tasks"]:
        task.setdefault("estimate_min", 0)
        task.setdefault("attempts", [])
    return data


def load_data(path=DATA_FILE):
    if not os.path.exists(path):
        return default_data()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("unexpected file content")
    except (ValueError, OSError):
        try:
            shutil.copy(path, path + ".bak")
        except OSError:
            pass
        return default_data()
    return migrate(data)


def save_data(data, path=DATA_FILE):
    temp_path = path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(temp_path, path)


def new_id(data):
    current = data["next_id"]
    data["next_id"] += 1
    return current
