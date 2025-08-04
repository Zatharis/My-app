from tkinter import *
from tkinter import ttk, messagebox
from datetime import date
from tkinter import font as tkfont
import platform
from tkinter import PhotoImage
import os
import json

from themes.color_manager import load_theme

from ui.ui_elements import (
    create_entry, create_button,
    create_dropdown, create_listbox,
    create_scrollbar
)

from logic.utils import resource_path
from logic.task_data import(
    save_task, load_tasks,
    delete_task_from_file,
    load_dismissed_recurring,
    save_dismissed_recurring,
    load_completed_tasks,
    clear_completed_tasks_file
)
from themes.color_manager import open_color_editor

class TaskKeeperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Keeper")
        self.theme = load_theme()
        self.root.configure(bg=self.theme["bg_main"])
        self.root.minsize(1100, 400)

        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        if not os.path.exists(documents_path):
            os.makedirs(documents_path)

        self.today = date.today()
        self.date_string = self.today.strftime("%m-%d-%Y")

        self.task_file = os.path.join(documents_path, "tasks.json")
        self.complete_task_file = os.path.join(documents_path, "completed_tasks.json")
        self.dismissed_recurring_file = os.path.join(documents_path, "dismissed_recurring.json")

        self.dismissed_recurring_today = load_dismissed_recurring(self.dismissed_recurring_file, self.date_string)
        self.displayed_recurring_today = set()

        self.custom_font = tkfont.Font(family="courier 10 pitch", size=16)
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#ad7b93")
        self.style.configure("TLabel", background="#ad7b93")
        self.style.configure("ColoredLabel.TLabel", foreground="white", background="#8a6276", font=self.custom_font)
        self.style.configure("Mainframe.TFrame", background="#ad7b93")
        self.style.map('CustomCombobox.TCombobox', fieldbackground=[('readonly', '#b5889e')],
                       background=[('readonly', '#b5889e')], foreground=[('readonly', 'black')])
        self.create_menu()
        self.create_widgets()
        self.load_tasks()

        self.undo_info = None
        self.task_listbox.bind("<Button 1>", self.on_listbox_click)


    def create_menu(self):
        menubar = Menu(self.root)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add.cascade(label="File", menu=filemenu)

        viewmenu = Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Completed Tasks", command=self.show_completed_tasks)
        menubar.add_cascade(label="View", menu=viewmenu)

        devmenu = Menu(menubar, tearoff=0)
        devmenu.add_command(label="Edit Colors", command=lambda: open_color_editor(self))
        menubar.add_cascade(label="Developer", menu=devmenu)

        self.root.config(menu=menubar)

    def create_widgets(self):
        self.main_frame = ttk.Frame (self.root, style="Mainframe.TFrame")
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.task_entry = create_entry(self.main_frame, font=self.custom_font, bg=self.theme["bg_entry"])
        self.task_entry.grid(row=0, column=0, padx=5, pady=5, sticky=W+E)

        self.due_entry = create_entry(self.main_frame, font=self.custom_font, bg=self.theme["bg_entry"])
        self.due_entry.grid(row=0, column=1, padx=5, pady=5, sticky=W+E)

        self.recurring_var = StringVar(value="No")
        self.recurring_dropdown = create_dropdown(
            self.main_frame, self.recurring_var, ["No", "Yes"]
        )

        self.recurring_dropdown.grid(row=0, column=2, padx=5, pady=5)

        self.submit_button = create_button(self.main_frame, text="Submit", command=self.get_task, bg=self.theme["bg_button"], fg=self.theme["fg_button"])
        self.submit_button.grid(row=0, column=3, padx=5, pady=5)

        self.delete_button = create_button(self.main_frame, text="Delete", command=self.delete_task, bg=self.theme["bg_button"], fg=self.theme["fg_button"])
        self.delete_button.grid(row=0, column=4, padx=5, pady=5)

        self.undo_button = create_button(self.main_frame, text="Undo", command=self.cancel_undo, bg=self.theme["bg_button"], fg=self.theme["fg_button"])
        self.undo_button.grid(row=0, column=5, padx=5, pady=5)

        self.task_listbox = create_listbox(self.main_frame, font=self.custom_font, bg=self.theme["bg_listbox"])
        self.task_listbox.grid(row=1, column=0, columnspan=6, padx=5, pady=10, sticky=NSEW)
        self.main_frame.rowconfigure(1, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

        self.scrollbar = create_scrollbar(self.main_frame)
        self.scrollbar.grid(row=1, column=6, sticky=N+S)

        self.task_listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.task_listbox.yview)

        self.dismiss_button = create_button(self.main_frame, text="Dismiss Recurring", command=self.dismiss_recurring, fg=self.theme["fg_button"])
        self.dismiss_button.grid(row=0, column=6, padx=5, pady=5)

    def get_task(self):
        task_text = self.task_entry.get().strip()
        due_date = self.due_entry.get().strip()
        recurring = self.recurring_var.get().lower() == "yes"

        if not task_text:
            messagebox.showwarning("Input Error", "Please enter a task")
            return
        
        task_data = {
            "text": task_text,
            "date": self.date_string,
            "due": due_date if due_date else None,
            "recurring": recurring
        }

        if task_text in self.task_listbox.get(0, END):
            messagebox.showinfo("Duplicate Task", "This task already exists.")
            return

        save_task(self.task_file, task_data)
        self.task_entry.delete(0, END)
        self.due_entry.delete(0, END)
        self.recurring_var.set("No")

        self.task_listbox.delete(0, END)
        self.displayed_recurring_today.clear()
        self.load_tasks()

    def load_tasks(self):
        load_tasks(self.task_file, self.task_listbox, self.date_string,
                   self.dismissed_recurring_today, self.displayed_recurring_today)
        
    def delete_task(self):
        selected_index = self.task_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("No selection", "Please select a task to delete.")
            return
        
        selected_text = self.task_listbox.get(selected_index)
        self.undo_info = {
            "text": selected_text,
            "date": self.date_string,
            "due": None,
            "recurring":False
        }

        delete_task_from_file(self.task_file, self.complete_task_file, selected_text, self.date_string)
        self.task_listbox.delete(selected_index)
        

    def on_listbox_click(self, event):
        self.task_listbox.selection_clear(0, END)

    def cancel_undo(self):
        if self.undo_info:
            try:
                with open(self.task_file, "r") as f:
                    tasks = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                tasks = []  

            tasks.append(self.undo_info)
            with open(self.task_file, "w") as f:
                json.dump(tasks, f, indent=2)
                
            self.undo_info = None
            self.task_listbox.delete(0, END)
            self.dismissed_recurring_today.clear()
            self.load_tasks()

    def finalize_deletion(self):
        self.undo_info = None

    def dismiss_recurring(self):
        dismissed_task = self.task_listbox.get(ACTIVE)
        self.dismissed_recurring_today.append(dismissed_task)
        save_dismissed_recurring(self.dismissed_recurring_file, self.dismissed_recurring_today, self.date_string)
        self.task_listbox.delete(ACTIVE)



    def show_completed_tasks(self):
        window = Toplevel(self.root)
        window.title("Completed Tasks")
        window.configure(bg=self.theme["bg_main"])

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


