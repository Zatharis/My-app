from tkinter import Tk
from ui.layout import TaskKeeperApp
from logic.utils import resource_path
import platform


if __name__ == "__main__":
    root = Tk()
    if platform.system() == "Windows":
        root.iconbitmap(resource_path("assets/icon.ico"))
    else:
        try:
            icon_img = PhotoImage(file=rescource_path("icon32.png"))
            root.iconphoto(False, icon_img)
            root._icon_img = icon_img
        except Exception as e:
            print(f"Failed to set icon: {e}")

    app = TaskKeeperApp(root)
    root.mainloop()
