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
    "bg_label": "#8a6276",
    "fg_text": "black",
}

THEMES_FILE = os.path.join(os.path.expanduser("~"), "Documents", "task_keeper_themes.json")
THEME_PREF_FILE = os.path.join(os.path.expanduser("~"), "Documents", "task_keeper_theme_pref.json")

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
from tkinter import Toplevel, Label, Entry, Button, messagebox, Frame

def open_color_editor(app):
    theme = app.theme.copy()
    themes = load_themes()

    editor = Toplevel(app.root)
    editor.title("Edit Theme Colors")
    set_window_icon(editor)
    editor.configure(bg=theme.get("bg_main", "#ffffff"))

    Label(editor, text="Theme Name:", bg=theme.get("bg_main", "#ffffff"), fg=theme.get("fg_text", "black")).pack()
    name_entry = Entry(editor)
    name_entry.pack()
    name_entry.insert(0, "Custom")

    entries = {}
    for key in DEFAULT_THEME:
        Label(editor, text=key, bg=theme.get("bg_main", "#ffffff"), fg=theme.get("fg_text", "black")).pack()
        entry = Entry(editor)
        entry.pack()
        entry.insert(0, theme.get(key, DEFAULT_THEME[key]))
        entries[key] = entry

    def apply_and_save():
        theme_name = name_entry.get().strip() or "Custom"
        new_theme = {k: e.get().strip() for k, e in entries.items()}
        save_theme(theme_name, new_theme)  # Always save on apply
        app.theme = new_theme
        app.apply_theme()
        save_last_theme(theme_name)  # Remember the last theme

    def save_and_close():
        theme_name = name_entry.get().strip() or "Custom"
        new_theme = {k: e.get().strip() for k, e in entries.items()}
        save_theme(theme_name, new_theme)
        app.theme = new_theme
        app.apply_theme()
        save_last_theme(theme_name)
        messagebox.showinfo("Saved", f"Theme '{theme_name}' saved and applied.", parent=editor)
        editor.destroy()

    button_frame = Frame(editor, bg=theme.get("bg_frame", "#aaaaaa"))
    button_frame.pack(side="bottom", pady=10)

    Button(button_frame, text="Apply", command=apply_and_save).pack(side="left", padx=10)
    Button(button_frame, text="Save", command=save_and_close).pack(side="left", padx=10)

def save_last_theme(theme_name):
    with open(THEME_PREF_FILE, "w") as f:
        json.dump({"last_theme": theme_name}, f)

def load_last_theme():
    if os.path.exists(THEME_PREF_FILE):
        try:
            with open(THEME_PREF_FILE, "r") as f:
                data = json.load(f)
            return data.get("last_theme", "Default")
        except Exception:
            pass
    return "Default"
