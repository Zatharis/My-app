from tkinter import Tk
from layout import TaskKeeperApp
from logic.utils import resource_path
from tkinter import PhotoImage
import os

def set_app_icon(root):
    icon_path = resource_path("assets/icon.png")
    if os.path.exists(icon_path):
        icon_img = PhotoImage(file=icon_path)
        root.iconphoto(False, icon_img)
    else:
        print("Icon not found at:", icon_path)

def main():
    root = Tk()
    root.title("Task Keeper")
    set_app_icon(root)
    app = TaskKeeperApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
