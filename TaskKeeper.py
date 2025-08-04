from tkinter import *
from tkinter import ttk
from datetime import date
import os
from tkinter import font as tkfont
import json
from tkinter import messagebox
import sys
import platform
from tkinter import PhotoImage

def rescource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

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

        self.complete_task_file = os.path.join(documents_path, "completed_tasks.json")



        self.create_menu()

        self.create_widgets()
        self.load_tasks()
        self.undo_info = None
        self.task_listbox.bind("<Button-1>", self.on_listbox_click)

    def create_menu(self):
            menubar = Menu(self.root)

            filemenu = Menu(menubar, tearoff=0)
            filemenu.add_command(label="Exit", command=self.root.quit)
            menubar.add_cascade(label="File", menu=filemenu)

            viewmenu = Menu(menubar, tearoff=0)
            viewmenu.add_command(label="Completed Tasks", command=self.show_completed_tasks)
            menubar.add_cascade(label="View", menu=viewmenu)

            self.root.config(menu=menubar)    
        
    def create_widgets(self):
        self.mainframe = ttk.Frame(self.root, padding="10 10 10 10", style="Mainframe.TFrame")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.mainframe.columnconfigure(1, weight=1)
        self.mainframe.rowconfigure(6, weight=1)

        # Date Label
        ttk.Label(self.mainframe, text=self.date_string, font=self.custom_font, style="ColoredLabel.TLabel").grid(column=0, row=0, pady=5, sticky='nw')

        # Due Date Label and Entry (framed)
        due_frame = Frame(self.mainframe, bg="#aaaaaa", bd=2, relief="solid", highlightthickness=0)
        due_frame.grid(column=0, row=1, pady=5, sticky="ew")
        due_frame.columnconfigure(0, weight=1)
        ttk.Label(due_frame, text="Due Date (MM-DD-YY):", font=self.custom_font, style="ColoredLabel.TLabel").grid(column=0, row=0, sticky="w", padx=5)
        self.due_date_entry = Entry(due_frame, bg="#b5889e", font=self.custom_font, relief="flat")
        self.due_date_entry.grid(column=0, row=1, sticky="ew", padx=5, pady=(0, 5))

        # Task Entry Frame
        task_entry_frame = Frame(self.mainframe, bg="#aaaaaa", bd=2, relief="solid")
        task_entry_frame.grid(column=0, row=2, pady=5, sticky="ew")
        task_entry_frame.columnconfigure(1, weight=1)

        ttk.Label(task_entry_frame, text="Task:", font=self.custom_font, style="ColoredLabel.TLabel").grid(column=0, row=0, padx=5, sticky='w')
        self.entry_widget = Entry(task_entry_frame, bg="#b5889e", font=self.custom_font, relief="flat")
        self.entry_widget.grid(column=1, row=0, padx=5, pady=5, sticky="ew")
        self.entry_widget.bind("<Return>", lambda event: self.get_task())

        # Recurring Checkbox + Dropdown (framed, using .grid())
        checkbox_frame = Frame(self.mainframe, bg="#aaaaaa", bd=2, relief="solid")
        checkbox_frame.grid(column=0, row=3, pady=5, sticky="ew")
        checkbox_frame.columnconfigure(1, weight=1)

        self.recurring_var = IntVar()

        self.recurring_checkbox = Checkbutton(
            checkbox_frame,
            text="Recurring Task",
            variable=self.recurring_var,
            font=self.custom_font,
            bg="#b5889e",
            relief="flat",
            padx=4, pady=2
        )
        self.recurring_checkbox.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.recurring_checkbox.config(command=self.toggle_recurring_dropdown)

        self.recurring_rate = StringVar()
        self.recurring_rate.set("Never")  # Default value
        self.recurring_dropdown = ttk.Combobox(
            checkbox_frame,
            textvariable=self.recurring_rate,
            values=["Never", "Daily", "Weekly", "Monthly"],
            font=self.custom_font,
            width=10,
            state="disabled",
            style="CustomCombobox.TCombobox"
        )
        self.recurring_dropdown.grid(row=0, column=1, sticky="w", padx=5, pady=5)


        # Task Listbox and Scrollbar (framed)
        listbox_frame = Frame(self.mainframe, bg="#aaaaaa", bd=2, relief="solid")
        listbox_frame.grid(column=1, row=0, rowspan=6, padx=10, pady=10, sticky="nsew")
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)

        self.task_listbox = Listbox(listbox_frame, bg="#d5a6bd", font=self.custom_font, relief="flat", width=60)
        self.task_listbox.grid(column=0, row=0, sticky="nsew")

        self.scrollbar = Scrollbar(listbox_frame, orient=VERTICAL, command=self.task_listbox.yview)
        self.scrollbar.grid(column=1, row=0, sticky='ns')
        self.task_listbox.config(yscrollcommand=self.scrollbar.set)

        # Bottom Buttons
        bottom_button_frame = Frame(self.mainframe, bg="#aaaaaa", bd=2, relief="solid")
        bottom_button_frame.grid(column=0, row=6, columnspan=2, sticky="sew", pady=(5, 0))

        submit_button = Button(
            bottom_button_frame, text="Add task", command=self.get_task,
            bg="#d5a6bd", fg="black",
            relief="flat", font=self.custom_font
        )
        submit_button.pack(side=LEFT, padx=10, pady=5, expand=True, fill=X)

        delete_button = Button(
            bottom_button_frame, text="Mark as Done (Delete)", command=self.delete_task,
            bg="#d5a6bd", fg="black",
            relief="flat", font=self.custom_font
        )
        delete_button.pack(side=LEFT, padx=10, pady=5, expand=True, fill=X)

        dismiss_button = Button(
            bottom_button_frame, text="Dismiss Recurring", command=self.dismiss_recurring,
            bg="#d5a6bd", fg="black",
            relief="flat", font=self.custom_font
        )
        dismiss_button.pack(side=LEFT, padx=10, pady=5, expand=True, fill=X)

    def toggle_recurring_dropdown(self):
            if self.recurring_var.get():
                self.recurring_dropdown.config(state="readonly")
            else:
                self.recurring_dropdown.config(state="disabled")

    def get_task(self):
        user_input = self.entry_widget.get().strip()
        due_date = self.due_date_entry.get().strip()
        recurring = bool(self.recurring_var.get()) and self.recurring_rate.get() != "Never"

        if user_input:
            display_date = self.date_string
            task_text = f"[{display_date}] - {user_input}"
            if due_date:
                task_text += f" (Due: {due_date})"
            if recurring:
                task_text += " [R]"

            self.task_listbox.insert(END, task_text)
            self.save_task(user_input, due_date=due_date, recurring=recurring)
            
            #OLD
            #self.save_task(task_text, recurring)

            self.entry_widget.delete(0, END)
            self.due_date_entry.delete(0, END)
            self.recurring_var.set(0)

    def save_task(self, task_name, due_date=None, recurring=False):
        task_data = {
            "date": self.date_string,
            "text": task_name,
            "due": due_date,
            "recurring": recurring
        }

        if recurring:
            task_data["repeat"] = self.recurring_rate.get()

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
                        if task.get("recurring"):
                            if task['text'] in self.dismissed_recurring_today:
                                continue
                            unique_id = (task['text'], self.date_string)
                            if unique_id in self.displayed_recurring_today:
                                continue
                            self.displayed_recurring_today.add(unique_id)

                            task_text = f"[{self.date_string}] - {task['text']}"
                            if task.get("due"):
                                task_text += f" (Due: {task['due']})"
                            task_text += " [R]"
                        else:
                            task_text = f"[{task['date']}] - {task['text']}"
                            if task.get("due"):
                                task_text += f" (Due: {task['due']})"

                        self.task_listbox.insert(END, task_text)
                except json.JSONDecodeError:
                    pass

    def delete_task(self):
        selected_index = self.task_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            task_text = self.task_listbox.get(index)

            if self.undo_info:
                self.root.after_cancel(self.undo_info['timer'])
                self.finalize_deletion()

            if " [R]" in task_text:
                undo_text = f"Undo Deletion: {task_text}?"
                self.task_listbox.delete(index)
                self.task_listbox.insert(index, undo_text)

                if self.undo_info:
                    self.root.after_cancel(self.undo_info['timer'])
                    self.finalize_deletion()

                self.undo_info = {
                    'index': index,
                    'task_text': task_text,
                    'timer': self.root.after(15000, self.finalize_deletion)
                    }
            else:
                self.task_listbox.delete(index)
                self.delete_task_from_file(task_text)

    def on_listbox_click(self,event):
        index = self.task_listbox.nearest(event.y)
        line_text = self.task_listbox.get(index)

        if line_text.startswith("Undo Deletion:"):
            answer = messagebox.askyesno("Undo Deletion", "Restore Task?")
            if answer:
                self.cancel_undo()
            else:
                if self.undo_info:
                    self.root.after_cancel(self.undo_info['timer'])
                    self.finalize_deletion()

    def cancel_undo(self):
        if self.undo_info:
            index = self.undo_info['index']
            task_text = self.undo_info['task_text']
            self.task_listbox.delete(index)
            self.task_listbox.insert(index, task_text)
            recurring = " [R]" in task_text
            self.save_task(task_text, recurring=recurring)

            self.root.after_cancel(self.undo_info['timer'])
            self.undo_info = None

    def finalize_deletion(self):
        if not self.undo_info or self.undo_info.get('index') is None:
            return


        index = self.undo_info['index']
        task_text = self.undo_info['task_text']

        self.undo_info = None
                    
        try:
            self.task_listbox.delete(index)
        except TclError:
            pass

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

        removed_tasks = []
        remaining_tasks = []

        for task in tasks:
            match =(
                task['text'] == rest and
                (task.get("recurring", False) == recurring)
                and (not recurring and task['date'] == tag or recurring)
            )
            if match:
                removed_tasks.append(task)
            else:
                remaining_tasks.append(task)

        if removed_tasks:
            existing = []
            if os.path.exists(self.complete_task_file):
                try:
                    with open(self.complete_task_file, "r") as f:
                        existing = json.load(f)
                except json.JSONDecodeError:
                    pass
            existing.extend(removed_tasks)
            with open(self.complete_task_file, "w") as f:
                json.dump(existing, f, indent=4)        #update the main task file
        with open(self.task_file, "w") as f:
            json.dump(remaining_tasks, f, indent=4)

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
    
    def dismiss_recurring(self):
        selected_index = self.task_listbox.curselection()
        if not selected_index:
            return
    
        task_text = self.task_listbox.get(selected_index)
        if " [R]" not in task_text:
            return
    
        if "] - " in task_text:
            _, rest = task_text.split("] - ", 1)
            rest = rest.replace(" [R]", "").split(" (Recurring")[0].strip()
        else:
            rest = task_text.replace(" [R]", "")

        self.dismissed_recurring_today.add(rest)
        self.save_dismissed_recurring()
        self.task_listbox.delete(selected_index)

    def show_completed_tasks(self):
        top = Toplevel(self.root)
        top.title("Completed Tasks")
        if platform.system() == "Windows":
            top.iconbitmap(rescource_path("icon32.ico"))
        else:
            try:
                icon_img = PhotoImage(file=rescource_path("icon.32png"))
                root.iconphoto(False, icon_img)
                top._icon_img = icon_img
            except Exception as e:
                print(f"Failed to set completed tasks icon: {e}")
        top.configure(bg="#ad7b93")
        top.lift()

        frame = Frame(top, bg="#aaaaaa", bd=2, relief="solid")
        frame.pack(padx=10, pady=10, fill=BOTH, expand=True)

        listbox = Listbox(frame, bg="#d5a6bd", font=self.custom_font, relief="flat", width=60)
        listbox.pack(side=LEFT, fill=BOTH, expand=True)
    
        scrollbar = Scrollbar(frame, orient=VERTICAL, command=listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        listbox.config(yscrollcommand=scrollbar.set)

        if os.path.exists(self.complete_task_file):
            try:
                with open(self.complete_task_file, "r") as f:
                    tasks = json.load(f)
                    for task in tasks:
                        task_text = f"[{task['date']}] - {task['text']}"
                        if task.get("recurring"):
                            task_text += " [R]"
                        listbox.insert(END, task_text)
            except json.JSONDecodeError:
                pass

        # --- Clear Button ---
        clear_btn = Button(
            top,
            text="Clear Completed Tasks",
            command=lambda: self.clear_completed_tasks(listbox),
            bg="#d5a6bd",
            fg="black",
            font=self.custom_font,
            relief="flat"
        )
        clear_btn.pack(pady=10)

    def clear_completed_tasks(self, listbox_widget):
        confirm = messagebox.askyesno("Clear History", "Are you sure you want to clear the completed tasks history?")
        if confirm:
            if os.path.exists(self.complete_task_file):
                try:
                    with open(self.complete_task_file, "w") as f:
                        json.dump([], f)
                except json.JSONDecodeError:
                    messagebox.showerror("Error", "Failed to clear completed tasks history.")
                    listbox_widget.delete(0, END)

#Run
if __name__ == "__main__":
    root = Tk()
    if platform.system() == "Windows":
        root.iconbitmap(rescource_path("icon.ico"))
    else:
        try:
            icon_img = PhotoImage(file=rescource_path("icon32.png"))
            root.iconphoto(False, icon_img)
            root._icon_img = icon_img
        except Exception as e:
            print(f"Failed to set icon: {e}")

    app = TaskManagerApp(root)
    root.mainloop()
