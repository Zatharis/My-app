from tkinter import Tk
from layout import TaskKeeperApp
from logic.utils import resource_path
import platform
from tkinter import PhotoImage
import os





if __name__ == "__main__":
    root = Tk()

    icon_path = resource_path("assets/icon.png")

    if os.path.exists(icon_path):
        icon_img = PhotoImage(file=icon_path)
        root.iconphoto(False, icon_img)
    else:
        print("Icon not found at:", icon_path)

    app = TaskKeeperApp(root)
    root.mainloop()
