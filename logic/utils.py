import os
import sys
from tkinter import PhotoImage
import json

def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def set_window_icon(window):
    """
    Set the window icon using the PNG asset.
    """
    icon_path = resource_path("assets/icon.png")
    if os.path.exists(icon_path):
        try:
            icon_img = PhotoImage(file=icon_path)
            window.iconphoto(False, icon_img)
        except Exception as e:
            print("Failed to set window icon:", e)
    else:
        print("Icon not found at:", icon_path)

DATE_FORMAT_FILE = os.path.join(os.path.expanduser("~"), "Documents", "last_date_format.json")

def save_last_date_format(fmt):
    """
    Save the last used date format to a file.
    """
    with open(DATE_FORMAT_FILE, "w") as f:
        json.dump({"last_format": fmt}, f)

def load_last_date_format():
    """
    Load the last used date format from a file, or return 'MM-DD-YYYY' if not set.
    """
    if os.path.exists(DATE_FORMAT_FILE):
        try:
            with open(DATE_FORMAT_FILE, "r") as f:
                return json.load(f).get("last_format", "MM-DD-YYYY")
        except Exception:
            pass
    return "MM-DD-YYYY"