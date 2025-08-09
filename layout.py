from tkinter import *
from tkinter import ttk, messagebox
from themes.color_manager import load_themes, load_theme, save_last_theme, load_last_theme
from logic.task_data import (
    save_task,
    delete_task_from_file,
    load_completed_tasks,
    clear_completed_tasks_file,
    dismiss_recurring_task,
    should_show_recurring,
    get_display_text,
)
from logic.utils import set_window_icon
from ui.ui_elements import create_entry, create_button, create_listbox, create_scrollbar, create_dropdown
import os
from datetime import date
import json
from themes.color_manager import open_color_editor, save_theme


class TaskKeeperApp:
    def __init__(self, root):
        self.root = root
        set_window_icon(self.root)
        self.style = ttk.Style(self.root)
        last_theme = load_last_theme()
        self.theme = load_theme(last_theme)
        self.date_string = date.today().strftime("%m-%d-%Y")
        self.custom_font = ("Comic Sans MS", 12)
        self.recurring_var = StringVar(value="No")
        self.recurring_type_var = StringVar(value="No")
        self.task_file = os.path.join(os.path.expanduser("~"), "Documents", "tasks.json")
        self.complete_task_file = os.path.join(os.path.expanduser("~"), "Documents", "completed_tasks.json")
        self.create_menu()
        self.date_format = "MM-DD-YYYY"
        self.create_widgets()
        self.apply_theme()
        self.load_tasks()

    def create_menu(self):
        menubar = Menu(self.root)

        # --- File menu ---
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        # --- View menu ---
        viewmenu = Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Completed Tasks", command=self.show_completed_tasks)
        viewmenu.add_command(label="Swap Date Format", command=self.swap_date_format)
        menubar.add_cascade(label="View", menu=viewmenu)

        

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

        self.root.config(menu=menubar)

        # ...existing code...
    
    def create_widgets(self):
        self.main_frame = ttk.Frame(self.root, style="Mainframe.TFrame")
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # --- LEFT SIDE ---
        # Date label
        self.date_label = Label(self.main_frame, text=self.date_string, font=self.custom_font, bg=self.theme["bg_label"])
        self.date_label.grid(row=0, column=0, padx=5, pady=5, sticky=W)

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
            bg=self.theme["bg_button"],
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
        recurring_type = self.recurring_type_var.get()  # "No", "Daily", "Weekly", "Monthly"
        recurring = recurring_type != "No"

        if not task_text:
            messagebox.showwarning("Input Error", "Please enter a task")
            return

        task_data = {
            "text": task_text,
            "date": self.date_string,
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

    def load_tasks(self):
        self.task_listbox.delete(0, END)
        dismissed_today = set()  # Load from file if needed
        displayed_today = set()  # Track displayed recurring tasks if needed
        from logic.task_data import load_tasks
        load_tasks(self.task_file, self.task_listbox, self.date_string, dismissed_today, displayed_today)

#    def get_task(self):
#        task_text = self.task_entry.get().strip()
#        due_date = self.due_entry.get().strip()
#        recurring_type = self.recurring_type_var.get()
#        recurring = recurring_type != "No"

#        if not task_text:
#            messagebox.showwarning("Input Error", "Please enter a task")
#            return

#        task_data = {
#            "text": task_text,
#            "date": self.date_string,
#            "due": due_date if due_date else None,
#            "recurring": recurring,
#            "recurring_type": recurring_type
#        }

#        if task_text in self.task_listbox.get(0, END):
#            messagebox.showinfo("Duplicate Task", "This task already exists.")
#            return

#        save_task(self.task_file, task_data)
#        self.task_entry.delete(0, END)
#        completed = load_completed_tasks(self.complete_task_file)
#        for task in completed:
#            if isinstance(task, dict):
#                display = f'{task.get("text")} ({task.get("date")})'
#                if task.get("due"):
#                    display += f' | Due: {task["due"]}'
#                listbox.insert(END, display)
#            else:
#                listbox.insert(END, task)


    def delete_task(self):
        selected_index = self.task_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("No selection", "Please select a task to delete.")
            return
        display_text = self.task_listbox.get(selected_index)
        task_text = self.extract_task_text(display_text)
        delete_task_from_file(self.task_file, self.complete_task_file, task_text, self.date_string)
        self.task_listbox.delete(selected_index)

    def dismiss_recurring(self):
        selected_index = self.task_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("No selection", "Please select a recurring task to dismiss.")
            return
        display_text = self.task_listbox.get(selected_index)
        recurring_type = self.get_recurring_type(display_text)
        task_text = self.extract_task_text(display_text)
        dismiss_recurring_task(task_text, recurring_type)
        self.task_listbox.delete(selected_index)

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
        self.due_date_frame.configure(bg=self.theme.get("bg_frame", "#aaaaaa"))
        self.task_frame.configure(bg=self.theme.get("bg_frame", "#aaaaaa"))
        self.recurring_frame.configure(bg=self.theme.get("bg_frame", "#aaaaaa"))
        self.button_frame.configure(bg=self.theme.get("bg_frame", "#aaaaaa"))
        self.date_label.configure(bg=self.theme.get("bg_label", "#8a6276"), fg=self.theme.get("fg_text", "black"))
        self.due_label.configure(bg=self.theme.get("bg_label", "#8a6276"), fg=self.theme.get("fg_text", "black"))
        self.due_entry.configure(bg=self.theme.get("bg_entry", "#e5c3cc"), fg=self.theme.get("fg_text", "black"))
        self.task_label.configure(bg=self.theme.get("bg_label", "#8a6276"), fg=self.theme.get("fg_text", "black"))
        self.task_entry.configure(bg=self.theme.get("bg_entry", "#e5c3cc"), fg=self.theme.get("fg_text", "black"))
        self.recurring_dropdown.configure(background=self.theme.get("bg_entry", "#e5c3cc"), foreground=self.theme.get("fg_text", "black"))
        self.task_listbox.configure(bg=self.theme.get("bg_listbox", "#f5dfe8"), fg=self.theme.get("fg_text", "black"))
        self.delete_button.configure(bg=self.theme.get("bg_button", "#8a6276"), fg=self.theme.get("fg_button", "white"))
        self.dismiss_button.configure(bg=self.theme.get("bg_button", "#8a6276"), fg=self.theme.get("fg_button", "white"))
        self.submit_button.configure(bg=self.theme.get("bg_button", "#8a6276"), fg=self.theme.get("fg_button", "white"))
        

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
            listbox.insert(END, task)

        clear_button = create_button(window, text="Clear Completed", command=lambda: self.clear_completed_tasks(listbox), bg=self.theme["bg_button"], fg=self.theme["fg_button"])
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

    def swap_date_format(self):
        # Toggle between two formats
        if hasattr(self, "date_format") and self.date_format == "MM-DD-YYYY":
            self.date_format = "DD-MM-YYYY"
        else:
            self.date_format = "MM-DD-YYYY"

        # Update the displayed date string
        from datetime import datetime
        today = datetime.today()
        if self.date_format == "MM-DD-YYYY":
            self.date_string = today.strftime("%m-%d-%Y")
        else:
            self.date_string = today.strftime("%d-%m-%Y")

        # Update the date label if it exists
        if hasattr(self, "date_label"):
            self.date_label.config(text=self.date_string)
        if hasattr(self, "due_label"):
            self.due_label.config(text=self.get_due_label_text())
        self.load_tasks()

    def get_due_label_text(self):
        if self.date_format == "MM-DD-YYYY":
            return "Due Date (MM-DD-YYYY):"
        else:
            return "Due Date (DD-MM-YYYY):"


