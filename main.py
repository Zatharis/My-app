import os
from tkinter import Tk, PhotoImage
from layout import TaskKeeperApp
from logic.utils import resource_path

def set_app_icon(root):
    """Set the window icon using the PNG asset."""
    icon_path = resource_path("assets/icon.png")
    print("Resolved icon path:", icon_path)  # Debugging
    if os.path.exists(icon_path):
        try:
            icon_img = PhotoImage(file=icon_path)
            root.iconphoto(False, icon_img)
        except Exception as e:
            print("Failed to set window icon:", e)
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
