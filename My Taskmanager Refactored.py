from tkinter import *
from tkinter import ttk
from datetime import date
import os
from tkinter import font as tkfont

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("My Task Manager")
        self.root.configure(bg="#ad7b93")

        #Today's date
        self.today = date.today()
        self.date_string = self.today.strftime("%m-%d-%y")
        self.task_file = "tasks.txt"
        self.custom_font = tkfont.Font(family="courier 10 pitch", size=16)

        self.style = ttk.Style()
        self.style.configure("Mainframe.TFrame", background="#aaaaaa")

        self.create_widgets()
        self.load_tasks()

    def create_widgets(self):
        self.mainframe = ttk.Frame(self.root, padding="3 3 12 12", style="Mainframe.TFrame")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.columnconfigure(1, weight=0)
        self.mainframe.columnconfigure(2, weight=1)

        #date label
        ttk.Label(self.mainframe, text=self.date_string, font=self.custom_font).grid(column=1, row=0, pady=5)

        #Due Date Entry
        ttk.Label(self.mainframe, text="Due Date (MM-DD-YY):", font=self.custom_font).grid(column=0, row=1, pady=5, sticky=E)
        self.due_date_entry = Entry(self.mainframe, width=10, bg="#dddddd", bd=2, relief="solid", highlightbackground="#aaa", highlightthickness=1, font=self.custom_font)
        self.due_date_entry.grid(column=0, row=2, pady=5, sticky=W)

        #Task Entry
        self.entry_widget = Entry(self.mainframe, width=50, bg="#dddddd", bd=2, relief="solid", highlightbackground="#aaa", highlightthickness=1, font=self.custom_font)
        self.entry_widget.grid(column=1, row=1, pady=5)
        self.entry_widget.bind("<Return>", lambda event: self.get_task())

        #submit button
        submit_button = Button(self.root, text="Add task", command=self.get_task, bg="#d5a6bd", relief="raised", bd=2, font=self.custom_font)
        submit_button.grid(column=1, row=2, pady=5)

        #Task Listbox with scrollbar
        self.task_listbox = Listbox(self.mainframe, width=60, height=10, bg="#d5a6bd", bd=2, relief="solid", highlightbackground="#aaa", highlightthickness=1, font=self.custom_font)
        self.task_listbox.grid(column=1, row=3, pady=10)

        self.scrollbar = Scrollbar(self.mainframe, orient=VERTICAL, command=self.task_listbox.yview)
        self.scrollbar.grid(column=2, row=3, sticky='ns', pady=10)
        self.task_listbox.config(yscrollcommand=self.scrollbar.set)

        #Delete Task Button
        delete_button = Button(self.mainframe, text="Mark as Done (Delete)", command=self.delete_task, bg="#d5a6bd", relief="raised", bd=2, font=self.custom_font)
        delete_button.grid(column=1, row=4, pady=5)

    def get_task(self):
        user_input = self.entry_widget.get().strip()
        due_date = self.due_date_entry.get().strip()
        if user_input:
            if due_date:
                task_text = f"[{due_date}] - {user_input} (Due: {due_date})"
            else:
                task_text = f"[{self.date_string}] - {user_input}"
            self.task_listbox.insert(END, task_text)
            self.save_task(task_text)
            self.entry_widget.delete(0, END)
            self.due_date_entry.delete(0, END)

    def save_task(self, task_text):
        with open(self.task_file, "a") as f:
            f.write(task_text + "\n")

    def load_tasks(self):
        if os.path.exists(self.task_file):
            with open(self.task_file, "r") as f:
                for line in f:
                    self.task_listbox.insert(END, line.strip())

    def delete_task(self):
        selected_index = self.task_listbox.curselection()
        if selected_index:
            task_text = self.task_listbox.get(selected_index)
            self.task_listbox.delete(selected_index)
            self.delete_task_from_file(task_text)

    def delete_task_from_file(self, task_text):
        if os.path.exists(self.task_file):
            with open(self.task_file, "r") as f:
                lines = f.readlines()
            with open(self.task_file, "w") as f:
                for line in lines:
                    if line.strip() != task_text:
                        f.write(line)


if __name__ == "__main__":
    root = Tk()
    app = TaskManagerApp(root)
    root.mainloop()