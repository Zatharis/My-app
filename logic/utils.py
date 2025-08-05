import os
import sys
from tkinter import PhotoImage

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