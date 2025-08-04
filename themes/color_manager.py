import json
import os
from logic.utils import set_window_icon

DEFAULT_THEME = {
    "bg_main": "#ad7b93",
    "bg_entry": "#e5c3cc",
    "bg_button": "#8a6276",
    "fg_button": "white",
    "bg_listbox": "#f5dfe8",
    "bg_frame": "#aaaaaa",
    "bg_label": "#8a6276"
}

THEMES_FILE = os.path.join(os.path.expanduser("~"), "Documents", "task_keeper_themes.json")

def load_themes():
    if not os.path.exists(THEMES_FILE):
        with open(THEMES_FILE, "w") as f:
            json.dump({"Default": DEFAULT_THEME}, f, indent=2)
    with open(THEMES_FILE, "r") as f:
        return json.load(f)

def save_theme(theme_name, theme_dict):
    themes = load_themes()
    themes[theme_name] = theme_dict
    with open(THEMES_FILE, "w") as f:
        json.dump(themes, f, indent=2)

def load_theme(theme_name="Default"):
    themes = load_themes()
    return themes.get(theme_name, DEFAULT_THEME)

# Color editor logic
from tkinter import Toplevel, Label, Entry, Button, messagebox

def open_color_editor(app):
    theme = app.theme
    themes = load_themes()

    editor = Toplevel(app.root)
    set_window_icon(editor)
    editor.title("Edit Theme Colors")

    Label(editor, text="Theme Name:").pack()
    name_entry = Entry(editor)
    name_entry.pack()
    name_entry.insert(0, "Custom")

    entries = {}
    for key in DEFAULT_THEME:
        Label(editor, text=key).pack()
        entry = Entry(editor)
        entry.pack()
        entry.insert(0, theme.get(key, DEFAULT_THEME[key]))
        entries[key] = entry

    def save_and_apply():
        theme_name = name_entry.get().strip() or "Custom"
        new_theme = {k: e.get().strip() for k, e in entries.items()}
        save_theme(theme_name, new_theme)
        app.theme = new_theme
        app.apply_theme()
        messagebox.showinfo("Saved", f"Theme '{theme_name}' saved and applied.")
        editor.destroy()

    Button(editor, text="Save", command=save_and_apply).pack()
