from tkinter import *
from tkinter import ttk
from datetime import date
import os
from tkinter import font as tkfont
import json

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Keeper")
        self.root.configure(bg="#ad7b93")
        self.root.minsize(1100, 400)

        self.dismissed_recurring_file = "dismissed_recurring.json"
        self.dismissed_recurring_today = set()
        self.displayed_recurring_today = set()
        self.load_dismissed_recurring()

        self.today = date.today()
        self.date_string = self.today.strftime("%m-%d-%Y")
        self.task_file = "tasks.json"
        self.custom_font = tkfont.Font(family="courier 10 pitch", size=16)

        self.style = ttk.Style()
        self.style.configure("ColoredLabel.TLabel",
                              foreground="white",
                              background="#8a6276",
                              font=self.custom_font)

        self.create_widgets()
        self.load_tasks()

    def create_widgets(self):
        self.mainframe = ttk.Frame(self.root, padding="3 3 12 12", style="Mainframe.TFrame")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        for i in range(8):
            self.mainframe.rowconfigure(i, weight=0)

        self.mainframe.rowconfigure(3, weight=1)  # Spacer to push task input down
        self.mainframe.rowconfigure(6, weight=1)  # Task listbox expands
        self.mainframe.columnconfigure(1, weight=1)

        # Date Label
        ttk.Label(self.mainframe, text=self.date_string, font=self.custom_font, style="ColoredLabel.TLabel").grid(column=0, row=0, pady=5, sticky='nw')

        # Due Date Label and Entry
        ttk.Label(self.mainframe, text="Due Date (MM-DD-YY):", font=self.custom_font, style="ColoredLabel.TLabel").grid(column=0, row=1, pady=(5, 0), sticky="nw")
        self.due_date_entry = Entry(self.mainframe, width=10, bg="#b5889e", bd=2, relief="solid",
                                    highlightbackground="#aaa", highlightthickness=1, font=self.custom_font)
        self.due_date_entry.grid(column=0, row=2, pady=(0, 10), sticky="ew")

        # Task Entry Frame (centered lower)
        task_entry_frame = Frame(
            self.mainframe, bg="#aaaaaa", bd=2, relief="solid",
            highlightbackground="#aaaaaa", highlightthickness=1,
            )
        task_entry_frame.grid(column=0, row=4, pady=(10, 10), sticky="ew")
        task_entry_frame.columnconfigure(1, weight=1)

        ttk.Label(task_entry_frame, text="Task:", font=self.custom_font, style="ColoredLabel.TLabel").grid(column=0, row=0, padx=(0, 5), sticky='w')
        self.entry_widget = Entry(task_entry_frame, bg="#b5889e", bd=2, relief="solid",
                                  highlightbackground="#aaa", highlightthickness=1, font=self.custom_font)
        self.entry_widget.grid(column=1, row=0, sticky="ew")
        self.entry_widget.bind("<Return>", lambda event: self.get_task())

        # Recurring Checkbox (under task input)
        self.recurring_var = IntVar()
        self.recurring_checkbox = Checkbutton(self.mainframe,
                                            text="Recurring Task",
                                            variable=self.recurring_var,
                                            font=self.custom_font,
                                            bg="#b5889e",
                                            bd=2,
                                            relief="solid",
                                            highlightbackground="#aaaaaa",
                                            highlightcolor="#aaaaaa",
                                            highlightthickness=10,
                                            padx=4, pady=2
                                            )
        
        self.recurring_checkbox.grid(column=0, row=5, pady=5, sticky='nw')

        # Task Listbox and Scrollbar
        self.task_listbox = Listbox(self.mainframe, width=60, height=15, bg="#d5a6bd", bd=2,
                                    relief="solid", highlightbackground="#aaaaaa", highlightthickness=3, font=self.custom_font)
        self.task_listbox.grid(column=1, row=0, rowspan=7, pady=10, sticky="nsew")

        self.scrollbar = Scrollbar(self.mainframe, orient=VERTICAL, command=self.task_listbox.yview)
        self.scrollbar.grid(column=2, row=0, rowspan=7, sticky='ns', pady=10)
        self.task_listbox.config(yscrollcommand=self.scrollbar.set)

        # Bottom Buttons (aligned to bottom)
        bottom_button_frame = Frame(self.mainframe, bg="#aaaaaa")
        bottom_button_frame.grid(column=0, row=7, columnspan=2, sticky="sew", pady=(5, 0))

        submit_button = Button(
            bottom_button_frame, text="Add task", command=self.get_task,
            bg="#d5a6bd", fg="black",
            relief="solid", bd=2,
            highlightbackground="#aaaaaa", highlightcolor="#aaaaaa",highlightthickness=2,
            font=self.custom_font
            )
        
        submit_button.pack(side=LEFT, padx=10, pady=5, expand=True, fill=X)

        delete_button = Button(bottom_button_frame, text="Mark as Done (Delete)", command=self.delete_task,
                               bg="#d5a6bd", fg="black",
                               relief="solid", bd=2,
                               highlightbackground="#aaaaaa", highlightcolor="#aaaaaa", highlightthickness=2,
                               font=self.custom_font)
        delete_button.pack(side=LEFT, padx=10, pady=5, expand=True, fill=X)

    def get_task(self):
        user_input = self.entry_widget.get().strip()
        due_date = self.due_date_entry.get().strip()
        recurring = bool(self.recurring_var.get())

        if user_input:
            if due_date:
                task_text = f"[{due_date}] - {user_input} (Due: {due_date})"
            else:
                task_text = f"[{self.date_string}] - {user_input}"

            if recurring:
                task_text += " [R]"

            self.task_listbox.insert(END, task_text)
            self.save_task(task_text, recurring)

            self.entry_widget.delete(0, END)
            self.due_date_entry.delete(0, END)
            self.recurring_var.set(0)

    def save_task(self, task_text, recurring=False):
        if "] - " in task_text:
            tag, rest = task_text.split("] - ", 1)
            tag = tag.strip("[]")
        else:
            tag, rest = self.date_string, task_text

        task_data = {
            "date": tag,
            "text": rest.replace(" [R]", "").split(" (Due")[0].strip(),
            "recurring": recurring
        }

        tasks = []
        if os.path.exists(self.task_file):
            with open(self.task_file, "r") as f:
                try:
                    tasks = json.load(f)
                except json.JSONDecodeError:
                    pass

        tasks.append(task_data)
        with open(self.task_file, "w") as f:
            json.dump(tasks, f, indent=4)

    def load_tasks(self):
        if os.path.exists(self.task_file):
            with open(self.task_file, "r") as f:
                try:
                    tasks = json.load(f)
                    for task in tasks:
                        task_text = f"[{task['date']}] - {task['text']}"
                        if task.get("recurring"):
                            if task['text'] in self.dismissed_recurring_today:
                                continue
                            unique_id = (task['text'], self.date_string)
                            if unique_id in self.displayed_recurring_today:
                                continue
                            self.displayed_recurring_today.add(unique_id)
                            task_text = f"[{self.date_string}] - {task['text']} (Recurring)"
                            task_text += " [R]"
                        self.task_listbox.insert(END, task_text)
                except json.JSONDecodeError:
                    pass

    def delete_task(self):
        selected_index = self.task_listbox.curselection()
        if selected_index:
            task_text = self.task_listbox.get(selected_index)
            self.task_listbox.delete(selected_index)
            self.delete_task_from_file(task_text)

    def delete_task_from_file(self, task_text):
        if os.path.exists(self.task_file):
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

        if recurring:
            self.dismissed_recurring_today.add(rest)
            self.save_dismissed_recurring()
            return

        tasks = [task for task in tasks if not (task['date'] == tag and task['text'] == rest and not task.get("recurring", False))]

        with open(self.task_file, "w") as f:
            json.dump(tasks, f, indent=4)

    def load_dismissed_recurring(self):
        if os.path.exists(self.dismissed_recurring_file):
            with open(self.dismissed_recurring_file, "r") as f:
                try:
                    data = json.load(f)
                    self.dismissed_recurring_today = set(data.get(self.date_string, []))
                except json.JSONDecodeError:
                    self.dismissed_recurring_today = set()
        else:
            self.dismissed_recurring_today = set()

    def save_dismissed_recurring(self):
        data = {}
        if os.path.exists(self.dismissed_recurring_file):
            with open(self.dismissed_recurring_file, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}
        data[self.date_string] = list(self.dismissed_recurring_today)
        with open(self.dismissed_recurring_file, "w") as f:
            json.dump(data, f, indent=4)

if __name__ == "__main__":
    root = Tk()
    app = TaskManagerApp(root)
    root.mainloop()
