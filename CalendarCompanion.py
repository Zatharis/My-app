import os
import json
from tkinter import Tk, Frame, Label, BOTH
from datetime import datetime
import calendar
from logic.utils import resource_path, load_last_date_format
from themes.color_manager import load_theme, load_last_theme

TASK_FILE = os.path.join(os.path.expanduser("~"), "Documents", "tasks.json")

def load_tasks():
    try:
        with open(TASK_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Calendar Companion")
        self.theme = load_theme(load_last_theme())
        self.root.configure(bg=self.theme["bg_main"])  # <-- Add this line
        self.tasks = load_tasks()
        self.date_format = load_last_date_format()
        self.create_calendar()

    def create_calendar(self):
        now = datetime.now()
        # Dynamically get the number of days in the current month
        days_in_month = calendar.monthrange(now.year, now.month)[1]

        # Month name label at the top (smaller, centered, with main background)
        month_label = Label(
            self.root,
            text=now.strftime("%B %Y"),
            font=("Comic Sans MS", 14, "bold"),
            bg=self.theme["bg_label"],  # Use main background color
            fg=self.theme["fg_text"],
            borderwidth=2,
            relief="groove",
            pady=4
        )
        month_label.pack(padx=5, pady=(5, 0), anchor="n")  # No fill, minimal padding, top center

        calendar_frame = Frame(self.root, bg=self.theme["bg_main"])
        calendar_frame.pack(fill=BOTH, expand=True)

        # Choose the correct date format string for parsing
        if self.date_format == "MM-DD-YYYY":
            parse_fmt = "%m-%d-%Y"
        else:
            parse_fmt = "%d-%m-%Y"

        for day in range(1, days_in_month + 1):
            label_text = f"{day}\n"
            for task in self.tasks:
                show_date = task.get("due") or task.get("date")
                if show_date:
                    # Try both ISO and user format
                    parsed = None
                    for fmt in ("%Y-%m-%d", parse_fmt):
                        try:
                            parsed = datetime.strptime(show_date, fmt)
                            break
                        except Exception:
                            continue
                    if parsed and parsed.day == day and parsed.month == now.month:
                        label_text += f"- {task['text']}\n"
            day_label = Label(
                calendar_frame,
                text=label_text.strip(),
                anchor="nw",
                justify="left",
                borderwidth=1,
                relief="solid",
                width=15,
                height=5,
                bg=self.theme["bg_entry"],
                fg=self.theme["fg_text"],
                font=("Comic Sans MS", 12)
            )
            day_label.grid(row=(day-1)//7, column=(day-1)%7, padx=2, pady=2)

if __name__ == "__main__":
    root = Tk()
    app = CalendarApp(root)
    root.mainloop()