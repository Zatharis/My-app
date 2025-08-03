from tkinter import *
from tkinter import ttk
from datetime import date
import os
from tkinter import font as tkfont
import json
from tkinter import messagebox# Keep your full import section and class start unchanged...

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Keeper")
        self.root.configure(bg="#ad7b93")
        self.root.minsize(1100, 400)

        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        if not os.path.exists(documents_path):
            os.makedirs(documents_path)

        self.today = date.today()
        self.date_string = self.today.strftime("%m-%d-%Y")

        self.dismissed_recurring_file = os.path.join(documents_path, "dismissed_recurring.json")
        self.task_file = os.path.join(documents_path, "tasks.json")
        self.complete_task_file = os.path.join(documents_path, "completed_tasks.json")

        self.dismissed_recurring_today = set()
        self.displayed_recurring_today = set()
        self.load_dismissed_recurring()

        self.custom_font = tkfont.Font(family="courier 10 pitch", size=16)

        self.style = ttk.Style()
        self.style.configure("TFrame", background="#ad7b93")
        self.style.configure("TLabel", background="#ad7b93")
        self.style.configure("ColoredLabel.TLabel",
                             foreground="white",
                             background="#8a6276",
                             font=self.custom_font)
        self.style.configure("Mainframe.TFrame", background="#ad7b93")
        self.style.map('CustomCombobox.TCombobox',
                       fieldbackground=[('readonly', '#b5889e')],
                       background=[('readonly', '#b5889e')],
                       foreground=[('readonly', 'black')])

        self.undo_info = None
        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(column=0, row=0, sticky="nsew")

        self.current_frame = ttk.Frame(self.notebook, style="Mainframe.TFrame")
        self.completed_frame = ttk.Frame(self.notebook, style="Mainframe.TFrame")

        self.notebook.add(self.current_frame, text="Current Tasks")
        self.notebook.add(self.completed_frame, text="Completed Tasks")

        self.mainframe = ttk.Frame(self.current_frame, padding="10 10 10 10", style="Mainframe.TFrame")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.mainframe.columnconfigure(1, weight=1)
        self.mainframe.rowconfigure(6, weight=1)

        ttk.Label(self.mainframe, text=self.date_string, font=self.custom_font,
                  style="ColoredLabel.TLabel").grid(column=0, row=0, pady=5, sticky='nw')

        # Due Date Field
        due_frame = Frame(self.mainframe, bg="#aaaaaa", bd=2, relief="solid")
        due_frame.grid(column=0, row=1, pady=5, sticky="ew")
        due_frame.columnconfigure(0, weight=1)
        ttk.Label(due_frame, text="Due Date (MM-DD-YY):", font=self.custom_font,
                  style="ColoredLabel.TLabel").grid(column=0, row=0, sticky="w", padx=5)
        self.due_date_entry = Entry(due_frame, bg="#b5889e", font=self.custom_font, relief="flat")
        self.due_date_entry.grid(column=0, row=1, sticky="ew", padx=5, pady=(0, 5))

        # Task Entry
        task_entry_frame = Frame(self.mainframe, bg="#aaaaaa", bd=2, relief="solid")
        task_entry_frame.grid(column=0, row=2, pady=5, sticky="ew")
        task_entry_frame.columnconfigure(1, weight=1)
        ttk.Label(task_entry_frame, text="Task:", font=self.custom_font,
                  style="ColoredLabel.TLabel").grid(column=0, row=0, padx=5, sticky='w')
        self.entry_widget = Entry(task_entry_frame, bg="#b5889e", font=self.custom_font, relief="flat")
        self.entry_widget.grid(column=1, row=0, padx=5, pady=5, sticky="ew")
        self.entry_widget.bind("<Return>", lambda event: self.get_task())

        # Recurring
        checkbox_frame = Frame(self.mainframe, bg="#aaaaaa", bd=2, relief="solid")
        checkbox_frame.grid(column=0, row=3, pady=5, sticky="ew")
        checkbox_frame.columnconfigure(1, weight=1)
        self.recurring_var = IntVar()
        self.recurring_checkbox = Checkbutton(checkbox_frame, text="Recurring Task",
                                              variable=self.recurring_var,
                                              font=self.custom_font,
                                              bg="#b5889e", relief="flat",
                                              padx=4, pady=2)
        self.recurring_checkbox.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.recurring_rate = StringVar(value="Daily")
        self.recurring_dropdown = ttk.Combobox(checkbox_frame, textvariable=self.recurring_rate,
                                               values=["Daily", "Weekly", "Monthly"],
                                               font=self.custom_font,
                                               width=10, state="readonly",
                                               style="CustomCombobox.TCombobox")
        self.recurring_dropdown.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Listbox Frame
        listbox_frame = Frame(self.mainframe, bg="#aaaaaa", bd=2, relief="solid")
        listbox_frame.grid(column=1, row=0, rowspan=6, padx=10, pady=10, sticky="nsew")
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)
        self.task_listbox = Listbox(listbox_frame, bg="#d5a6bd", font=self.custom_font,
                                    relief="flat", width=60)
        self.task_listbox.grid(column=0, row=0, sticky="nsew")
        self.scrollbar = Scrollbar(listbox_frame, orient=VERTICAL, command=self.task_listbox.yview)
        self.scrollbar.grid(column=1, row=0, sticky='ns')
        self.task_listbox.config(yscrollcommand=self.scrollbar.set)
        self.task_listbox.bind("<Button-1>", self.on_listbox_click)

        # Bottom Buttons
        bottom_button_frame = Frame(self.mainframe, bg="#aaaaaa", bd=2, relief="solid")
        bottom_button_frame.grid(column=0, row=6, columnspan=2, sticky="sew", pady=(5, 0))

        for label, command in [
            ("Add task", self.get_task),
            ("Mark as Done (Delete)", self.delete_task),
            ("Dismiss Recurring", self.dismiss_recurring)
        ]:
            Button(bottom_button_frame, text=label, command=command,
                   bg="#d5a6bd", fg="black", relief="flat",
                   font=self.custom_font).pack(side=LEFT, padx=10, pady=5, expand=True, fill=X)

        # Completed tab
        self.completed_listbox = Listbox(self.completed_frame, bg="#d5a6bd",
                                         font=self.custom_font, relief="flat", width=60)
        self.completed_listbox.pack(fill="both", expand=True, padx=10, pady=10)

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
        self.load_tasks()

    # Keep all your other methods unchanged, except:
    # Revised delete_task_from_file() so that recurring tasks are NOT added to completed_tasks.json

    def delete_task_from_file(self, task_text):
        if not os.path.exists(self.task_file):
            return

        try:
            with open(self.task_file, "r") as f:
                tasks = json.load(f)
        except json.JSONDecodeError:
            return

        recurring = " [R]" in task_text
        if "] - " in task_text:
            tag, rest = task_text.split("] - ", 1)
            tag = tag.strip("[]")
            rest = rest.replace(" [R]", "").split(" (Due")[0].strip()
        else:
            tag, rest = self.date_string, task_text.replace(" [R]", "")

        removed_tasks = []
        remaining_tasks = []

        for task in tasks:
            match = (
                task['text'] == rest and
                (task.get("recurring", False) == recurring) and
                (not recurring and task['date'] == tag or recurring)
            )
            if match:
                removed_tasks.append(task)
            else:
                remaining_tasks.append(task)

        if removed_tasks and not recurring:
            existing = []
            if os.path.exists(self.complete_task_file):
                try:
                    with open(self.complete_task_file, "r") as f:
                        existing = json.load(f)
                except json.JSONDecodeError:
                    pass
            existing.extend(removed_tasks)
            with open(self.complete_task_file, "w") as f:
                json.dump(existing, f, indent=4)

        with open(self.task_file, "w") as f:
            json.dump(remaining_tasks, f, indent=4)
