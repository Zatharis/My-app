import json
import os
from logic.utils import set_window_icon, resource_path

DEFAULT_THEME = {
    "bg_main": "#ad7b93",
    "bg_entry": "#e5c3cc",
    "bg_button": "#8a6276",
    "fg_button": "white",
    "bg_listbox": "#f5dfe8",
    "bg_frame": "#aaaaaa",
    "bg_label": "#8a6276",
    "fg_text": "black",
}

THEMES_DIR = resource_path("themes")
if not os.path.exists(THEMES_DIR):
    os.makedirs(THEMES_DIR)

THEMES_FILE = resource_path("themes/task_keeper_themes.json")
THEME_PREF_FILE = resource_path("themes/task_keeper_theme_pref.json")

def load_themes():
    """
    Load all themes from the themes file.
    If the file doesn't exist, create it with the default theme.
    """
    if not os.path.exists(THEMES_FILE):
        with open(THEMES_FILE, "w") as f:
            json.dump({"Default": DEFAULT_THEME}, f, indent=2)
    with open(THEMES_FILE, "r") as f:
        return json.load(f)

def save_theme(theme_name, theme_dict):
    """
    Save a theme to the themes file.
    """
    themes = load_themes()
    themes[theme_name] = theme_dict
    with open(THEMES_FILE, "w") as f:
        json.dump(themes, f, indent=2)

def load_theme(theme_name="Default"):
    """
    Load a specific theme by name, or return the default theme.
    """
    themes = load_themes()
    return themes.get(theme_name, DEFAULT_THEME)

def save_last_theme(theme_name):
    """
    Save the last selected theme name for persistence.
    """
    with open(THEME_PREF_FILE, "w") as f:
        json.dump({"last_theme": theme_name}, f)

def load_last_theme():
    """
    Load the last selected theme name, or return 'Default'.
    """
    if os.path.exists(THEME_PREF_FILE):
        try:
            with open(THEME_PREF_FILE, "r") as f:
                data = json.load(f)
            return data.get("last_theme", "Default")
        except Exception:
            pass
    return "Default"

# Color editor logic should be defined in a function and called from your app, not at module level.
