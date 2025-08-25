import os
import json
from tkinter import Tk, Frame, Label, BOTH, Canvas, Scrollbar, Button
from datetime import datetime
import calendar
from logic.utils import resource_path, load_last_date_format
from themes.color_manager import load_theme, load_last_theme

TASK_FILE = os.path.join(os.path.expanduser("~"), "Documents", "tasks.json")
COMPLETED_FILE = os.path.join(os.path.expanduser("~"), "Documents", "completed_tasks.json")

def load_tasks():
    try:
        with open(TASK_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def load_completed_tasks():
    try:
        with open(COMPLETED_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def load_dismissed_recurring():
    try:
        with open(os.path.join(os.path.expanduser("~"), "Documents", "dismissed_recurring.json"), "r") as f:
            return json.load(f)
    except Exception:
        return {}

class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Calendar Companion")
        self.theme = load_theme(load_last_theme())
        self.root.configure(bg=self.theme["bg_main"])  # <-- Add this line
        self.tasks = load_tasks()
        self.completed_tasks = load_completed_tasks()
        self.dismissed_recurring = load_dismissed_recurring()
        self.date_format = load_last_date_format()
        self.create_calendar()

    def create_calendar(self):
        now = datetime.now()
        days_in_month = calendar.monthrange(now.year, now.month)[1]

        # --- Build completed_set before the calendar loop ---
        completed = load_completed_tasks()
        completed_set = set()
        for entry in completed:
            if isinstance(entry, dict):
                text = entry.get("text")
                completed_on = entry.get("completed_on") or entry.get("date")
                if text and completed_on:
                    completed_set.add((text, completed_on))

        dismissed = load_dismissed_recurring()
        dismissed_set = set()
        for key, info in dismissed.items():
            text, recurring_type = key.split("|")
            for dismissed_date in info.get("dates", []):
                dismissed_set.add((text, dismissed_date, recurring_type))

        month_label = Label(
            self.root,
            text=now.strftime("%B %Y"),
            font=("Comic Sans MS", 14, "bold"),
            bg=self.theme["bg_label"],
            fg=self.theme["fg_text"],
            borderwidth=2,
            relief="groove",
            pady=4
        )
        month_label.pack(padx=5, pady=(5, 0), anchor="n")

        calendar_frame = Frame(self.root, bg=self.theme["bg_main"])
        calendar_frame.pack(fill=BOTH, expand=True)

        # --- Make the grid stretch ---
        for row in range(6):  # Up to 6 weeks in a month
            calendar_frame.rowconfigure(row, weight=1)
        for col in range(7):  # 7 days per week
            calendar_frame.columnconfigure(col, weight=1)

        if self.date_format == "MM-DD-YYYY":
            parse_fmt = "%m-%d-%Y"
        else:
            parse_fmt = "%d-%m-%Y"

        for day in range(1, days_in_month + 1):
            cell_frame = Frame(calendar_frame, bg=self.theme["bg_entry"], borderwidth=1, relief="solid")
            cell_frame.grid(row=(day-1)//7, column=(day-1)%7, padx=2, pady=2, sticky="nsew")

            # Set a fixed height for the canvas
            canvas_height = 100  # Try 100 or adjust as needed
            canvas = Canvas(cell_frame, bg=self.theme["bg_entry"], highlightthickness=0, height=canvas_height)
            scrollbar = Scrollbar(cell_frame, orient="vertical", command=canvas.yview)
            canvas.configure(yscrollcommand=scrollbar.set)

            # Do NOT use expand=True here!
            canvas.pack(side="left", fill="both")
            scrollbar.pack(side="right", fill="y")

            inner_frame = Frame(canvas, bg=self.theme["bg_entry"])
            canvas.create_window((0, 0), window=inner_frame, anchor="nw")

            def _on_frame_configure(event, canvas=canvas):
                # Always make the scrollregion at least 1 pixel taller than the canvas
                content_height = max(canvas.bbox("all")[3], canvas_height + 1)
                canvas.configure(scrollregion=(0, 0, canvas.winfo_width(), content_height))
            inner_frame.bind("<Configure>", _on_frame_configure)

            Button(inner_frame, text=str(day), font=("Comic Sans MS", 12, "bold"),
                   bg=self.theme["bg_button"], fg=self.theme["fg_text"], anchor="w",
                   command=lambda d=day: self.show_day_tasks(d, now, completed_set, dismissed_set, parse_fmt)
            ).pack(anchor="nw")

            current_date = datetime(now.year, now.month, day)
            current_date_str = current_date.strftime("%Y-%m-%d")  # ISO format for matching

            for task in self.tasks:
                show_date = task.get("due") or task.get("date")
                recurring_type = task.get("recurring_type", "No")
                parsed = None
                for fmt in ("%Y-%m-%d", parse_fmt):
                    try:
                        parsed = datetime.strptime(show_date, fmt)
                        break
                    except Exception:
                        continue

                show_task = False
                if recurring_type == "Daily":
                    show_task = True
                elif recurring_type == "Weekly" and parsed:
                    if current_date.weekday() == parsed.weekday():
                        show_task = True
                elif recurring_type == "Monthly" and parsed:
                    if day == parsed.day:
                        show_task = True
                elif recurring_type == "No" and parsed and parsed.day == day and parsed.month == now.month:
                    show_task = True

                # --- Hide recurring tasks if completed on this date ---
                if show_task and recurring_type in ["Daily", "Weekly", "Monthly"]:
                    if (task["text"], current_date_str) in completed_set:
                        show_task = False

                # --- Hide recurring tasks if dismissed on this date ---
                if show_task and recurring_type in ["Daily", "Weekly", "Monthly"]:
                    if (task["text"], current_date_str, recurring_type) in dismissed_set:
                        show_task = False

                if show_task:
                    Label(inner_frame, text=f"- {task['text']}", font=("Comic Sans MS", 11),
                          bg=self.theme["bg_entry"], fg=self.theme["fg_text"], anchor="w", wraplength=120).pack(anchor="nw")

            inner_frame.update_idletasks()
            # Only update scrollregion here, not canvas height
            content_height = max(canvas.bbox("all")[3], canvas_height + 1)
            canvas.config(scrollregion=(0, 0, canvas.winfo_width(), content_height))
            canvas.yview_moveto(0)
            scrollbar.lift()

    def show_day_tasks(self, day, now, completed_set, dismissed_set, parse_fmt):
        popup = Tk()
        popup.title(f"Tasks for {now.strftime('%B')} {day}")
        popup.configure(bg=self.theme["bg_main"])

        canvas = Canvas(popup, bg=self.theme["bg_entry"], highlightthickness=0)
        scrollbar = Scrollbar(popup, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        inner_frame = Frame(canvas, bg=self.theme["bg_entry"])
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        current_date = datetime(now.year, now.month, day)
        current_date_str = current_date.strftime("%Y-%m-%d")

        for task in self.tasks:
            show_date = task.get("due") or task.get("date")
            recurring_type = task.get("recurring_type", "No")
            parsed = None
            for fmt in ("%Y-%m-%d", parse_fmt):
                try:
                    parsed = datetime.strptime(show_date, fmt)
                    break
                except Exception:
                    continue

            show_task = False
            if recurring_type == "Daily":
                show_task = True
            elif recurring_type == "Weekly" and parsed:
                if current_date.weekday() == parsed.weekday():
                    show_task = True
            elif recurring_type == "Monthly" and parsed:
                if day == parsed.day:
                    show_task = True
            elif recurring_type == "No" and parsed and parsed.day == day and parsed.month == now.month:
                show_task = True

            if show_task and recurring_type in ["Daily", "Weekly", "Monthly"]:
                if (task["text"], current_date_str) in completed_set:
                    show_task = False
                if (task["text"], current_date_str, recurring_type) in dismissed_set:
                    show_task = False

            if show_task:
                Label(inner_frame, text=f"- {task['text']}", font=("Comic Sans MS", 11),
                      bg=self.theme["bg_entry"], fg=self.theme["fg_text"], anchor="w", wraplength=300).pack(anchor="nw", pady=2)

        inner_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

if __name__ == "__main__":
    root = Tk()
    app = CalendarApp(root)
    root.mainloop()