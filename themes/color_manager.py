import json
import os
from logic.utils import resource_path

DEFAULT_THEME = {
    "bg_main": "#ad7b93",
    "bg_entry": "#e5c3cc",
    "bg_button": "#8a6276",
    "fg_button": "white",
    "bg_listbox": "#f5dfe8"
}

THEME_FILE = os.path.join(os.path.expanduser("~"), "Documents", "task_keeper_theme.json")

def load_theme():
    if not os.path.exists(THEME_FILE):
        save_theme(DEFAULT_THEME)
        return DEFAULT_THEME
    try:
        with open(THEME_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return DEFAULT_THEME
    
def save_theme(theme_dict):
    with open(THEME_FILE, "w") as file:
        json.dump(theme_dict, file, indent=2)

from tkinter import Toplevel, Label, Entry, Button, messagebox

def open_color_editor(app):
    theme = app.theme

    editor = Toplevel(app.root)
    editor.title("Edit Theme Colors")
    editor.configure(bg=theme.get("bg_main", "#ffffff"))

    entries = {}

    row = 0
    for key, value in theme.items():
        Label(editor, text=key, bg=theme["bg_main"], fg="black").grid(row=row, column=0, padx=5, pady=5, sticky="e")
        entry = Entry(editor)
        entry.insert(0, value)
        entry.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        entries[key] = entry
        row += 1

    def save_and_apply():
        new_theme = {}
        for key, entry in entries.items():
            new_theme[key] = entry.get().strip()

        # Save to file
        save_theme(new_theme)

        # Apply the new theme (restart required or reload theme parts)
        messagebox.showinfo("Saved", "Theme saved. Please restart the app to apply changes.")
        editor.destroy()

    Button(editor, text="Save", command=save_and_apply).grid(row=row, column=0, columnspan=2, pady=10)
