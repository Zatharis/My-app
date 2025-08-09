import json
import os
from logic.utils import set_window_icon, resource_path
from tkinter import Toplevel, Label, Button, colorchooser, StringVar, Entry, Frame, LEFT, RIGHT, BOTH

DEFAULT_THEME = {
    "bg_main": "#ad7b93",
    "bg_entry": "#e5c3cc",
    "bg_button": "#8a6276",
    "fg_button": "black",
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

def open_color_editor(app):
    """
    Open a color editor dialog to edit the current theme.
    """
    theme = app.theme.copy()
    editor = Toplevel(app.root)
    editor.title("Edit Theme Colors")
    set_window_icon(editor)
    editor.geometry("400x500")
    editor.configure(bg=theme.get("bg_main", "#ad7b93"))

    color_keys = [
        "bg_main", "bg_entry", "bg_button", "fg_button",
        "bg_listbox", "bg_frame", "bg_label", "fg_text"
    ]
    color_vars = {k: StringVar(value=theme.get(k, "")) for k in color_keys}
    entries = {}

    def choose_color(key):
        color = colorchooser.askcolor(color_vars[key].get(), parent=editor)[1]
        if color:
            color_vars[key].set(color)
            entries[key].configure(bg=color)
            preview_theme()

    def preview_theme():
        # Update app theme live for preview
        preview = {k: v.get() for k, v in color_vars.items()}
        app.theme = preview
        app.apply_theme()

    def save_and_close():
        new_theme = {k: v.get() for k, v in color_vars.items()}
        theme_name = app.theme_name if hasattr(app, "theme_name") else "Custom"
        save_theme(theme_name, new_theme)
        app.theme = new_theme
        app.apply_theme()
        save_last_theme(theme_name)
        editor.destroy()

    Label(editor, text="Edit Theme Colors", font=app.custom_font, bg=theme.get("bg_main", "#ad7b93")).pack(pady=10)
    for key in color_keys:
        row = Frame(editor, bg=theme.get("bg_main", "#ad7b93"))
        row.pack(fill=BOTH, padx=10, pady=5)
        Label(row, text=key, width=12, anchor="w", bg=theme.get("bg_main", "#ad7b93"), font=app.custom_font).pack(side=LEFT)
        e = Entry(row, textvariable=color_vars[key], width=15, bg=color_vars[key].get(), font=app.custom_font)
        e.pack(side=LEFT, padx=5)
        entries[key] = e
        Button(row, text="Pick", command=lambda k=key: choose_color(k), font=app.custom_font).pack(side=RIGHT, padx=5)

    Button(
        editor,
        font=app.custom_font,
        text="Save",
        command=save_and_close,
        bg=color_vars["bg_button"].get(),
        fg=color_vars["fg_button"].get()
    ).pack(pady=20)

    # Live preview on entry change
    for var in color_vars.values():
        var.trace_add("write", lambda *args: preview_theme())
