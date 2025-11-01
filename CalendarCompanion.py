import os
import json
from tkinter import Tk, Frame, Label, BOTH, Canvas, Scrollbar, Button
from datetime import datetime
import calendar
from logic.utils import format_date, parse_date, load_last_date_format
from themes.color_manager import load_theme, load_last_theme
from tkinter import ttk

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
        self.root.configure(bg=self.theme["bg_main"])
        self.tasks = load_tasks()
        self.completed_tasks = load_completed_tasks()
        self.dismissed_recurring = load_dismissed_recurring()
        self.date_format = load_last_date_format()

        # --- ttk Style Configuration ---
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure(
            "ExpBar.Horizontal.TProgressbar",
            troughcolor=self.theme.get("bg_entry", "#e5c3cc"),
            background=self.theme.get("fg_text", "black"),
            bordercolor=self.theme.get("bg_frame", "#aaaaaa"),
            lightcolor=self.theme.get("fg_text", "black"),
            darkcolor=self.theme.get("fg_text", "black"),
        )

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
            if "|" not in key:
                continue  # Skip malformed keys
            text, recurring_type = key.split("|", 1)
            for dismissed_date in info.get("dates", []):
                dismissed_set.add((text, dismissed_date, recurring_type))

        # Month name label at the top, inside a themed frame
        month_frame = Frame(
            self.root,
            bg=self.theme["bg_frame"],
            borderwidth=2,
            relief="groove",
            highlightbackground=self.theme["bg_frame"],
            highlightcolor=self.theme["bg_frame"]
        )
        month_frame.pack(padx=5, pady=(5, 0), anchor="n")

        month_label = Label(
            month_frame,
            text=format_date(now, self.date_format),
            font=("Comic Sans MS", 14, "bold"),
            bg=self.theme["bg_label"],
            fg=self.theme["fg_text"],
            borderwidth=0,
            pady=4
        )
        month_label.pack(padx=8, pady=4)

        calendar_frame = Frame(self.root, bg=self.theme["bg_main"])
        calendar_frame.pack(fill=BOTH, expand=True)

        # --- Make the grid stretch ---
        for row in range(7):  # 6 weeks + header row
            calendar_frame.rowconfigure(row, weight=1)
        for col in range(7):  # 7 days per week
            calendar_frame.columnconfigure(col, weight=1)

        # --- Add day-of-week headers ---
        days_of_week = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for col, day_name in enumerate(days_of_week):
            Label(
                calendar_frame,
                text=day_name,
                font=("Comic Sans MS", 12, "bold"),
                bg=self.theme["bg_label"],
                fg=self.theme["fg_text"],
                borderwidth=1,
                relief="ridge"
            ).grid(row=0, column=col, sticky="nsew", padx=1, pady=1)

        if self.date_format == "MM-DD-YYYY":
            parse_fmt = "%m-%d-%Y"
        else:
            parse_fmt = "%d-%m-%Y"

        first_weekday, _ = calendar.monthrange(now.year, now.month)
        for day in range(1, days_in_month + 1):
            current_date = datetime(now.year, now.month, day)
            is_today = (current_date.date() == datetime.now().date())
            cell_border = self.theme["bg_label"] if is_today else self.theme["bg_frame"]

            # PATCH: Calculate correct row and column for the calendar grid
            # first_weekday: 0=Monday, 6=Sunday (Python's calendar module)
            # We want columns: 0=Sunday, 1=Monday, ..., 6=Saturday
            # So shift first_weekday to Sunday=0
            python_first_weekday = first_weekday  # 0=Monday
            # Calculate the weekday for the first day of the month (0=Monday, 6=Sunday)
            # To shift so Sunday=0, use:
            sunday_first_weekday = (python_first_weekday + 1) % 7
            # Now, for each day:
            col = (sunday_first_weekday + day - 1) % 7
            row = (sunday_first_weekday + day - 1) // 7 + 1  # +1 for header row

            cell_frame = Frame(
                calendar_frame,
                bg=self.theme["bg_entry"],
                borderwidth=3 if is_today else 2,
                relief="solid" if is_today else "groove",
                highlightbackground=cell_border,
                highlightcolor=cell_border
            )
            cell_frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")

            canvas_height = 100
            canvas = Canvas(cell_frame, bg=self.theme["bg_entry"], highlightthickness=0, height=canvas_height)
            scrollbar = Scrollbar(cell_frame, orient="vertical", command=canvas.yview)
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both")
            scrollbar.pack(side="right", fill="y")

            inner_frame = Frame(canvas, bg=self.theme["bg_entry"])
            canvas.create_window((0, 0), window=inner_frame, anchor="nw")

            def _on_frame_configure(event, canvas=canvas):
                content_height = max(canvas.bbox("all")[3], canvas_height + 1)
                canvas.configure(scrollregion=(0, 0, canvas.winfo_width(), content_height))
            inner_frame.bind("<Configure>", _on_frame_configure)

            # Button inside a themed frame for border
            button_frame = Frame(
                inner_frame,
                bg=self.theme["bg_frame"],
                borderwidth=2,
                relief="groove",
                highlightbackground=self.theme["bg_frame"],
                highlightcolor=self.theme["bg_frame"]
            )
            button_frame.pack(anchor="nw", pady=2)

            Button(
                button_frame,
                text=str(day),
                font=("Comic Sans MS", 12, "bold"),
                bg=self.theme["bg_button"],
                fg=self.theme["fg_text"],
                anchor="w",
                command=lambda d=day: self.show_day_tasks(d, now, completed_set, dismissed_set, parse_fmt)
            ).pack(padx=2, pady=2)

            current_date_str = format_date(current_date, self.date_format)

            for task in self.tasks:
                show_date = task.get("due") or task.get("date")
                recurring_type = task.get("recurring_type", "No")
                parsed = parse_date(show_date, self.date_format)

                show_task = False
                if recurring_type == "Daily":
                    show_task = True
                elif recurring_type == "Weekly" and parsed:
                    if current_date.weekday() == parsed.weekday():
                        show_task = True
                elif recurring_type == "Monthly" and parsed:
                    if day == parsed.day:
                        show_task = True
                elif recurring_type == "No" and parsed:
                    if parsed.day == day and parsed.month == now.month:
                        show_task = True

                # Only show tasks that were created on or before this date
                created_date = parse_date(task.get("date", ""), self.date_format)
                if show_task and created_date and created_date > current_date:
                    show_task = False

                # PATCH: Hide if completed or dismissed for this day
                if show_task and recurring_type in ["Daily", "Weekly", "Monthly"]:
                    if (task["text"], current_date_str) in completed_set:
                        show_task = False
                    if (task["text"], current_date_str, recurring_type) in dismissed_set:
                        show_task = False

                if show_task:
                    Label(inner_frame, text=f"- {task['text']}", font=("Comic Sans MS", 13),
                          bg=self.theme["bg_entry"], fg=self.theme["fg_text"], anchor="w", wraplength=120).pack(anchor="nw")

            inner_frame.update_idletasks()
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
        current_date_str = format_date(current_date, self.date_format)

        for task in self.tasks:
            show_date = task.get("due") or task.get("date")
            recurring_type = task.get("recurring_type", "No")
            parsed = parse_date(show_date, self.date_format)

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
                Label(inner_frame, text=f"- {task['text']}", font=("Comic Sans MS", 13),
                      bg=self.theme["bg_entry"], fg=self.theme["fg_text"], anchor="w", wraplength=300).pack(anchor="nw", pady=2)

        inner_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

if __name__ == "__main__":
    root = Tk()
    app = CalendarApp(root)
    root.mainloop()