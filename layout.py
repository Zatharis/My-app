from tkinter import *
from tkinter import ttk, messagebox, font  # <-- Add 'font' here
from themes.color_manager import load_themes, load_theme, save_last_theme, load_last_theme
from logic.task_data import (
    save_task,
    delete_task_from_file,
    load_completed_tasks,
    clear_completed_tasks_file,
    dismiss_recurring_task,
    should_show_recurring,
    get_display_text,
    load_tasks,
    display_tasks_in_listbox,
)
from logic.utils import set_window_icon, load_last_date_format, save_last_date_format, parse_date, format_date
from ui.ui_elements import create_entry, create_button, create_listbox, create_scrollbar, create_dropdown
import os
from datetime import date, datetime, timedelta
import json
from themes.color_manager import open_color_editor, save_theme
import subprocess
import sys


class TaskKeeperApp:
    def __init__(self, root):
        self.root = root
        self.calendar_process = None  # <-- Add this line

        # Theme and style
        self.theme = load_theme(load_last_theme())
        self.style = ttk.Style()
        self.style.theme_use('default')

        # Font
        self.custom_font = font.Font(family="Comic Sans MS", size=12, weight="bold")

        # Date format and string
        self.date_format = load_last_date_format()
        self.date_string = datetime.now().strftime("%m-%d-%Y")

        # Task file paths
        self.task_file = os.path.join(os.path.expanduser("~"), "Documents", "tasks.json")
        self.complete_task_file = os.path.join(os.path.expanduser("~"), "Documents", "completed_tasks.json")

        # EXP and level
        self.exp_var = IntVar(value=0)
        self.level_var = IntVar(value=1)

        # Recurring type variable
        self.recurring_type_var = StringVar(value="No")  # <-- Add this line

        # Other UI variables (if used)
        # self.task_listbox = None
        # self.due_date_frame = None
        # self.top_frame = None
        # ... (these will be set in create_widgets)

        self.create_widgets()
        self.create_menu()  
        self.apply_theme()
        self.load_tasks()
        if should_run_daily_exp_check():
            daily_exp_check(self)
        self.load_exp_level()  # Load experience and level on startup
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # <-- Add this line

    def create_menu(self):
        menubar = Menu(self.root)

        # --- File menu ---
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        # --- View menu ---
        viewmenu = Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Completed Tasks", command=self.show_completed_tasks)
        #viewmenu.add_command(label="Swap Date Format", command=self.swap_date_format)
        viewmenu.add_command(label="Open Calendar", command=self.launch_calendar)  # <-- Add this line
        menubar.add_cascade(label="View", menu=viewmenu)

        dateformatmenu = Menu(menubar, tearoff=0)
        for fmt in ["MM-DD-YYYY", "DD-MM-YYYY", "YYYY-MM-DD", "YYYY-DD-MM"]:
            dateformatmenu.add_command(
                label=fmt,
                command=lambda f=fmt: self.set_date_format(f)
            )
        menubar.add_cascade(label="Date Format", menu=dateformatmenu)

        # --- Themes menu (for picking themes only) ---
        themesmenu = Menu(menubar, tearoff=0)
        themes = load_themes()
        for theme_name in themes.keys():
            themesmenu.add_command(
                label=theme_name,
                command=lambda n=theme_name: self.select_theme(n)
            )
        menubar.add_cascade(label="Themes", menu=themesmenu)

         # --- Developer menu (for saving and editing themes) ---
        devmenu = Menu(menubar, tearoff=0)
        devmenu.add_command(label="Edit Custom", command=lambda: open_color_editor(self))
        devmenu.add_command(label="Save Custom", command=lambda: self.save_custom_theme())
        menubar.add_cascade(label="Developer", menu=devmenu)

        self.root.config(menu=menubar)  # <-- This attaches the menu bar to the window
  
    def create_widgets(self):
        self.main_frame = ttk.Frame(self.root, style="Mainframe.TFrame")
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # --- EXP BAR AT TOP LEFT ---
        self.exp_var = IntVar(value=0)
        self.level_var = IntVar(value=1)

        # Create the top frame for date, exp bar, and level
        self.top_frame = Frame(
            self.main_frame,
            bg=self.theme["bg_frame"],
            bd=2,
            relief=GROOVE,
            height=50
        )
        self.top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=(5, 0))
        self.top_frame.grid_propagate(False)

        # Do NOT set columnconfigure for self.top_frame, so columns don't expand

        self.date_label = Label(
            self.top_frame,
            text=self.date_string,
            font=self.custom_font,
            bg=self.theme["bg_label"],
            bd=1,
            relief=GROOVE
        )
        self.date_label.grid(row=0, column=0, padx=5, pady=10, sticky="w")

        self.exp_bar = ttk.Progressbar(
            self.top_frame,
            orient="horizontal",
            length=200,
            mode="determinate",
            variable=self.exp_var,
            maximum=100,
            style="ExpBar.Horizontal.TProgressbar"
        )
        self.exp_bar.grid(row=0, column=1, padx=5, pady=10, sticky="w")

        self.style.configure(
            "ExpBar.Horizontal.TProgressbar",
            troughcolor=self.theme.get("exp_bar_bg", "#e5c3cc"),
            background=self.theme.get("exp_bar_fg", "#00cc66"),
            bordercolor=self.theme.get("bg_frame", "#aaaaaa"),
            lightcolor=self.theme.get("exp_bar_fg", "#00cc66"),
            darkcolor=self.theme.get("exp_bar_fg", "#00cc66"),
        )
        self.exp_bar.configure(style="ExpBar.Horizontal.TProgressbar")

        self.level_label = Label(
            self.top_frame,
            text=f"Lv. {self.level_var.get()}",
            font=self.custom_font,
            bg=self.theme.get("bg_label", "#8a6276"),
            fg=self.theme.get("fg_text", "black"),
            bd=1,
            relief=GROOVE
        )
        self.level_label.grid(row=0, column=2, padx=5, pady=10, sticky="w")

        # Due date group frame
        self.due_date_frame = Frame(self.main_frame, bg=self.theme["bg_frame"], bd=2, relief=GROOVE)
        self.due_date_frame.grid(row=1, column=0, padx=5, pady=5, sticky=W+E, columnspan=2)
        self.due_label = Label(self.due_date_frame, text=self.get_due_label_text(), font=self.custom_font, bg=self.theme["bg_label"])
        self.due_label.pack(side=LEFT, padx=5, pady=5)
        self.due_entry = create_entry(self.due_date_frame, font=self.custom_font, bg=self.theme["bg_entry"])
        self.due_entry.pack(side=LEFT, padx=5, pady=5, fill=X, expand=True)

        # Task group frame
        self.task_frame = Frame(self.main_frame, bg=self.theme["bg_frame"], bd=2, relief=GROOVE)
        self.task_frame.grid(row=3, column=0, padx=5, pady=5, sticky=W+E, columnspan=2)
        self.task_label = Label(self.task_frame, text="Task:", font=self.custom_font, bg=self.theme["bg_label"])
        self.task_label.pack(side=LEFT, padx=5, pady=5)
        self.task_entry = create_entry(self.task_frame, font=self.custom_font, bg=self.theme["bg_entry"])
        self.task_entry.pack(side=LEFT, padx=5, pady=5, fill=X, expand=True)

        # Recurring group frame
        self.recurring_frame = Frame(self.main_frame, bg=self.theme["bg_frame"], bd=2, relief=GROOVE)
        self.recurring_frame.grid(row=5, column=0, padx=5, pady=5, sticky=W)
        self.recurring_dropdown = create_dropdown(
            self.recurring_frame,
            self.recurring_type_var,
            ["No", "Daily", "Weekly", "Monthly"],
            font=self.custom_font,
        )
        self.recurring_dropdown.pack(side=LEFT, padx=5, pady=5)

        # --- RIGHT SIDE ---
        self.task_listbox = create_listbox(self.main_frame, font=self.custom_font, bg=self.theme["bg_listbox"])
        self.task_listbox.grid(row=0, column=2, rowspan=6, padx=5, pady=10, sticky=NSEW)
        self.scrollbar = create_scrollbar(self.main_frame)
        self.scrollbar.grid(row=0, column=3, rowspan=6, sticky=N+S)
        self.task_listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.task_listbox.yview)

        # --- BOTTOM BUTTONS FRAME ---
        self.button_frame = Frame(self.main_frame, bg=self.theme["bg_frame"], bd=2, relief=GROOVE)
        self.button_frame.grid(row=99, column=0, columnspan=3, padx=5, pady=10, sticky="nsew")  # Use a high row number and columnspan to ensure it's at the bottom and stretches

        self.main_frame.rowconfigure(99, weight=1)  # Make bottom row expand

        self.submit_button = create_button(self.button_frame, font=self.custom_font, text="Add task", command=self.get_task, bg=self.theme["bg_button"], fg=self.theme["fg_button"])
        self.submit_button.pack(side=LEFT, padx=5, pady=5, fill=X, expand=True)

        self.delete_button = create_button(self.button_frame, font=self.custom_font, text="Mark as Done (Delete)", command=self.delete_task, bg=self.theme["bg_button"], fg=self.theme["fg_button"])
        self.delete_button.pack(side=LEFT, padx=5, pady=5, fill=X, expand=True)

        self.dismiss_button = create_button(self.button_frame, font=self.custom_font, text="Dismiss Recurring", command=self.dismiss_recurring, bg=self.theme["bg_button"], fg=self.theme["fg_button"])
        self.dismiss_button.pack(side=LEFT, padx=5, pady=5, fill=X, expand=True)

        # Grid weights for resizing
        self.main_frame.columnconfigure(0, weight=0)
        self.main_frame.columnconfigure(1, weight=0)
        self.main_frame.columnconfigure(2, weight=1)
        self.main_frame.rowconfigure(7, weight=1)  # Make bottom row stretch

    def get_task(self):
        task_text = self.task_entry.get().strip()
        due_date = self.due_entry.get().strip()
        recurring_type = self.recurring_type_var.get()
        recurring = recurring_type != "No"

        if not task_text:
            messagebox.showwarning("Input Error", "Please enter a task")
            return

        # Use the user's format for today's date
        iso_date = format_date(date.today(), self.date_format)
        task_data = {
            "text": task_text,
            "date": iso_date,
            "due": due_date if due_date else None,
            "recurring": recurring,
            "recurring_type": recurring_type
        }

        # Check for duplicates using just the task text
        for i in range(self.task_listbox.size()):
            display_text = self.task_listbox.get(i)
            if task_text in display_text:
                messagebox.showinfo("Duplicate Task", "This task already exists.")
                return

        save_task(self.task_file, task_data)
        self.task_entry.delete(0, END)
        self.due_entry.delete(0, END)
        self.recurring_type_var.set("No")  # Reset dropdown

        self.task_listbox.delete(0, END)
        self.load_tasks()

    def delete_task(self):
        selected_index = self.task_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("No selection", "Please select a task to delete.")
            return
        display_text = self.task_listbox.get(selected_index)
        task_text = self.extract_task_text(display_text)

        # Before deleting:
        task_due_date = None
        try:
            with open(self.task_file, "r") as f:
                tasks = json.load(f)
            for task in tasks:
                if task["text"] == task_text:
                    task_due_date = task.get("due")
                    break
        except Exception:
            pass

        if task_due_date:
            today = date.today()
            parsed_due = parse_date(task_due_date, self.date_format)
            if not parsed_due or parsed_due.date() != today:
                messagebox.showinfo("Not Due Yet", "This task can't be completed until its due date.")
                return

        delete_task_from_file(self.task_file, self.complete_task_file, task_text, self.date_string, self.date_format)
        self.task_listbox.delete(selected_index)
        self.gain_exp(10)

    def dismiss_recurring(self):
        selected_index = self.task_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("No selection", "Please select a recurring task to dismiss.")
            return
        display_text = self.task_listbox.get(selected_index)
        recurring_type = self.get_recurring_type(display_text)
        task_text = self.extract_task_text(display_text)
        dismiss_recurring_task(task_text, recurring_type, self.date_format)
        self.task_listbox.delete(selected_index)
        self.gain_exp(5)

    def extract_task_text(self, display_text):
        # Handles format: "[D] Task name (date) | Due: ..."
        if display_text.startswith("["):
            parts = display_text.split(" ", 1)
            if len(parts) == 2:
                text_and_date = parts[1]
                text_and_date = text_and_date.split(" | Due:")[0]
                task_text = text_and_date.rsplit(" (", 1)[0]
                return task_text.strip()
        text_and_date = display_text.split(" | Due:")[0]
        return text_and_date.rsplit(" (", 1)[0].strip()

    def get_recurring_type(self, display_text):
        task_text = self.extract_task_text(display_text)
        try:
            with open(self.task_file, "r") as f:
                tasks = json.load(f)
            for task in tasks:
                if task["text"] == task_text:
                    # Always return the actual recurring_type, not "Yes"/"No"
                    return task.get("recurring_type", "No")
        except Exception:
            pass
        return "No"

    def apply_theme(self):
        self.root.configure(bg=self.theme.get("bg_main", "#ad7b93"))
        self.style.configure("Mainframe.TFrame", background=self.theme.get("bg_main", "#ad7b93"))
        self.main_frame.configure(style="Mainframe.TFrame")

        # --- PATCH: Update progress bar style for live color changes ---
        self.style.configure(
            "ExpBar.Horizontal.TProgressbar",
            troughcolor=self.theme.get("exp_bar_bg", "#e5c3cc"),
            background=self.theme.get("exp_bar_fg", "#00cc66"),
            bordercolor=self.theme.get("bg_frame", "#aaaaaa"),
            lightcolor=self.theme.get("exp_bar_fg", "#00cc66"),
            darkcolor=self.theme.get("exp_bar_fg", "#00cc66"),
        )
        self.exp_bar.configure(style="ExpBar.Horizontal.TProgressbar")
        # --- END PATCH ---

        self.top_frame.configure(bg=self.theme.get("bg_frame", "#aaaaaa"))  # <-- Add this line
        self.due_date_frame.configure(bg=self.theme.get("bg_frame", "#aaaaaa"))
        self.task_frame.configure(bg=self.theme.get("bg_frame", "#aaaaaa"))
        self.recurring_frame.configure(bg=self.theme.get("bg_frame", "#aaaaaa"))
        self.button_frame.configure(bg=self.theme.get("bg_frame", "#aaaaaa"))
        self.date_label.configure(bg=self.theme.get("bg_label", "#8a6276"), fg=self.theme.get("fg_text", "black"))
        self.due_label.configure(bg=self.theme.get("bg_label", "#8a6276"), fg=self.theme.get("fg_text", "black"))
        self.due_entry.configure(bg=self.theme.get("bg_entry", "#e5c3cc"), fg=self.theme.get("fg_text", "black"))
        self.task_label.configure(bg=self.theme.get("bg_label", "#8a6276"), fg=self.theme.get("fg_text", "black"))
        self.task_entry.configure(bg=self.theme.get("bg_entry", "#e5c3cc"), fg=self.theme.get("fg_text", "black"))
        self.recurring_dropdown.configure(background=self.theme.get("bg_button", "#8a6276"), foreground=self.theme.get("fg_text", "black"))
        self.task_listbox.configure(bg=self.theme.get("bg_listbox", "#f5dfe8"), fg=self.theme.get("fg_text", "black"))
        self.delete_button.configure(bg=self.theme.get("bg_button", "#8a6276"), fg=self.theme.get("fg_button", "white"))
        self.dismiss_button.configure(bg=self.theme.get("bg_button", "#8a6276"), fg=self.theme.get("fg_button", "white"))
        self.submit_button.configure(bg=self.theme.get("bg_button", "#8a6276"), fg=self.theme.get("fg_button", "white"))
        self.level_label.configure(
            bg=self.theme.get("bg_label", "#8a6276"),
            fg=self.theme.get("fg_text", "black")
        )

    def select_theme(self, theme_name):
        self.theme = load_theme(theme_name)
        self.apply_theme()
        save_last_theme(theme_name)

    def show_completed_tasks(self):
        window = Toplevel(self.root)
        window.title("Completed Tasks")
        window.configure(bg=self.theme["bg_main"])
        set_window_icon(window)

        listbox = Listbox(window, font=self.custom_font, bg=self.theme["bg_listbox"])
        listbox.pack(padx=10, pady=10, fill=BOTH, expand=True)

        completed = load_completed_tasks(self.complete_task_file)
        for task in completed:
            if isinstance(task, dict):
                text = task.get("text", "")
                completed_on = task.get("completed_on", "")
                dt = parse_date(completed_on, self.date_format)
                display_date = format_date(dt, self.date_format) if dt else completed_on
                display = f"{text} (Completed on: {display_date})"
                listbox.insert(END, display)
            else:
                listbox.insert(END, str(task))

        clear_button = create_button(window, font=self.custom_font, text="Clear Completed", command=lambda: self.clear_completed_tasks(listbox), bg=self.theme["bg_button"], fg=self.theme["fg_button"])
        clear_button.pack(pady=5)

    def clear_completed_tasks(self, listbox_widget):
        clear_completed_tasks_file(self.complete_task_file)
        listbox_widget.delete(0, END)

    def save_custom_theme(self):
        window = Toplevel(self.root)
        window.title("Save Custom Theme")
        set_window_icon(window)
        window.configure(bg=self.theme["bg_main"])
        window.resizable(False, False)

        label = Label(window, text="Enter a name for your custom theme:", font=self.custom_font, bg=self.theme["bg_main"], fg=self.theme["fg_button"])
        label.pack(padx=20, pady=(20, 5))

        entry = Entry(window, font=self.custom_font)
        entry.pack(padx=20, pady=5)
        entry.focus_set()

        def save_and_close():
            theme_name = entry.get().strip()
            if theme_name:
                save_theme(theme_name, self.theme)
                messagebox.showinfo("Theme Saved", f"Theme '{theme_name}' saved.", parent=window)
                window.destroy()
            else:
                messagebox.showwarning("Input Error", "Please enter a theme name.", parent=window)

        save_btn = Button(window, text="Save", command=save_and_close, font=self.custom_font, bg=self.theme["bg_button"], fg=self.theme["fg_button"])
        save_btn.pack(pady=(10, 20))

        window.grab_set()
        window.wait_window()

    #def swap_date_format(self):
        # Toggle between two formats
        #if self.date_format == "MM-DD-YYYY":
            #self.date_format = "DD-MM-YYYY"
        #else:
            #self.date_format = "MM-DD-YYYY"

        # Update the displayed date string
        #today = datetime.today()
        #if self.date_format == "MM-DD-YYYY":
            #self.date_string = today.strftime("%m-%d-%Y")
        #else:
            #self.date_string = today.strftime("%d-%m-%Y")

        # Update the date label if it exists
        #if hasattr(self, "date_label"):
            #self.date_label.config(text=self.date_string)
        #if hasattr(self, "due_label"):
            #self.due_label.config(text=self.get_due_label_text())
        #save_last_date_format(self.date_format)
        #self.load_tasks()

    def set_date_format(self, fmt):
        self.date_format = fmt
        from logic.utils import save_last_date_format
        save_last_date_format(fmt)
        # Update all date displays
        today = datetime.today()
        self.date_string = format_date(today, self.date_format)
        if hasattr(self, "date_label"):
            self.date_label.config(text=self.date_string)
        if hasattr(self, "due_label"):
            self.due_label.config(text=f"Due Date ({self.date_format}):")
        self.load_tasks()

    def get_due_label_text(self):
        if self.date_format == "MM-DD-YYYY":
            return "Due Date (MM-DD-YYYY):"
        else:
            return "Due Date (DD-MM-YYYY):"

    def load_tasks(self):
        dismissed_today = set()
        displayed_today = set()
        display_tasks_in_listbox(self.task_file, self.task_listbox, self.date_format, dismissed_today, displayed_today)

    def launch_calendar(self):
        calendar_path = os.path.join(os.path.dirname(__file__), "CalendarCompanion.py")
        if self.calendar_process is None or self.calendar_process.poll() is not None:
            self.calendar_process = subprocess.Popen([sys.executable, calendar_path])

    def on_close(self):
        # Close calendar if open
        if self.calendar_process and self.calendar_process.poll() is None:
            self.calendar_process.terminate()
        self.root.destroy()

    def exp_to_level(self, level):
        # Progressive curve: +10 per level, cap at 400 at level 30+
        if level < 30:
            return 100 + (level - 1) * 10
        else:
            return 400

    def gain_exp(self, amount):
        exp = self.exp_var.get()
        level = self.level_var.get()
        while amount > 0 and level < 99:
            needed = self.exp_to_level(level) - exp
            if amount >= needed:
                amount -= needed
                level += 1
                exp = 0
            else:
                exp += amount
                amount = 0
        self.exp_var.set(exp)
        self.level_var.set(level)
        self.level_label.config(text=f"Lv. {level}")
        self.save_exp_level()

    def lose_exp(self, amount):
        exp = self.exp_var.get()
        level = self.level_var.get()
        while amount > 0 and level > 1:
            if exp >= amount:
                exp -= amount
                amount = 0
            else:
                amount -= exp
                level -= 1
                exp = self.exp_to_level(level)
        exp = max(exp, 0)
        self.exp_var.set(exp)
        self.level_var.set(level)
        self.level_label.config(text=f"Lv. {level}")
        self.save_exp_level()

    def save_exp_level(self):
        data = {
            "exp": self.exp_var.get(),
            "level": self.level_var.get()
        }
        exp_file = os.path.join(os.path.expanduser("~"), "Documents", "exp_level.json")
        with open(exp_file, "w") as f:
            json.dump(data, f)

    def load_exp_level(self):
        exp_file = os.path.join(os.path.expanduser("~"), "Documents", "exp_level.json")
        if os.path.exists(exp_file):
            try:
                with open(exp_file, "r") as f:
                    data = json.load(f)
                self.exp_var.set(data.get("exp", 0))
                self.level_var.set(data.get("level", 1))
                self.level_label.config(text=f"Lv. {self.level_var.get()}")
            except Exception:
                self.exp_var.set(0)
                self.level_var.set(1)
                self.level_label.config(text="Lv. 1")
        else:
            self.exp_var.set(0)
            self.level_var.set(1)
            self.level_label.config(text="Lv. 1")

def daily_exp_check(app):
    today = date.today()
    yesterday = today - timedelta(days=1)
    yesterday_str = format_date(yesterday, app.date_format)

    penalty_file = os.path.join(os.path.expanduser("~"), "Documents", "exp_penalties.json")
    if os.path.exists(penalty_file):
        with open(penalty_file, "r") as f:
            penalties = json.load(f)
    else:
        penalties = {}

    # Load tasks, completed, and dismissed
    try:
        with open(app.task_file, "r") as f:
            tasks = json.load(f)
    except Exception:
        tasks = []
    try:
        with open(app.complete_task_file, "r") as f:
            completed = json.load(f)
    except Exception:
        completed = []
    try:
        from logic.task_data import load_dismissed_recurring
        dismissed = load_dismissed_recurring()
    except Exception:
        dismissed = {}

    # Build lookup sets using user format
    from logic.utils import parse_date

    completed_set = set()
    for entry in completed:
        if isinstance(entry, dict):
            text = entry.get("text")
            completed_on = entry.get("completed_on")
            if text and completed_on:
                completed_set.add((text, completed_on))

    dismissed_set = set()
    for key, info in dismissed.items():
        if "|" not in key:
            continue
        text, recurring_type = key.split("|", 1)
        for dismissed_date in info.get("dates", []):
            dismissed_set.add((text, dismissed_date, recurring_type))

    # Only check yesterday's tasks
    for task in tasks:
        text = task.get("text")
        recurring_type = task.get("recurring_type", "No")
        due = task.get("due")
        created = task.get("date")

        # Only check recurring tasks that should have appeared yesterday
        if recurring_type in ["Daily", "Weekly", "Monthly"]:
            if not should_show_recurring(text, recurring_type, app.date_format, check_date=yesterday_str):
                continue

        # If due date is in the future, skip
        if due:
            try:
                due_date = parse_date(due, app.date_format)
                if due_date and due_date.date() > yesterday:
                    continue
            except Exception:
                pass

        # If task was created after yesterday, skip
        if created:
            try:
                created_date = parse_date(created, app.date_format)
                # PATCH: Only penalize if task was created on or before yesterday
                if created_date and created_date.date() < (date.today() - timedelta(days=1)):
                    continue  # Skip penalty for tasks older than a day ago
            except Exception:
                pass

        penalty_key = f"{text}|{recurring_type}|{yesterday_str}"

        # If completed or dismissed yesterday, gain exp
        if (text, yesterday_str) in completed_set or (text, yesterday_str, recurring_type) in dismissed_set:
            app.gain_exp(10)
        else:
            # Only penalize if not already penalized for this task/date
            if not penalties.get(penalty_key):
                app.lose_exp(5)
                penalties[penalty_key] = True

    # Save updated penalties
    with open(penalty_file, "w") as f:
        json.dump(penalties, f)

def should_run_daily_exp_check():
    check_file = os.path.join(os.path.expanduser("~"), "Documents", "last_exp_check.json")
    today_str = date.today().isoformat()
    if os.path.exists(check_file):
        try:
            with open(check_file, "r") as f:
                last_check = json.load(f).get("date")
            if last_check == today_str:
                return False  # Already checked today
        except Exception:
            pass
    with open(check_file, "w") as f:
        json.dump({"date": today_str}, f)
    return True

