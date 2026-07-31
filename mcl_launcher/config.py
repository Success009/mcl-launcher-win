import os
import json

CONFIG_DIR = os.path.expanduser("~/.config/mcl") if os.name != "nt" else os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "mcl")
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "username": "Player",
    "isolate_instances": True,
    "last_played_version": "",
    "jvm_args": "-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+AlwaysPreTouch",
    "isolate_saves": False,
    "isolate_resourcepacks": False
}

def load_settings():
    if not os.path.exists(CONFIG_FILE):
        return save_settings(DEFAULT_SETTINGS)
    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            updated = False
            for k, v in DEFAULT_SETTINGS.items():
                if k not in data:
                    data[k] = v
                    updated = True
            if updated:
                save_settings(data)
            return data
    except Exception:
        return DEFAULT_SETTINGS

def save_settings(settings):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(settings, f, indent=4)
    except Exception:
        pass
    return settings