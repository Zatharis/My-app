import os
import sys
from tkinter import PhotoImage

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def set_window_icon(window):
    from logic.utils import resource_path
    icon_path = resource_path("assets/icon.png")
    if os.path.exists(icon_path):
        icon_img = PhotoImage(file=icon_path)
        window.iconphoto(False, icon_img)