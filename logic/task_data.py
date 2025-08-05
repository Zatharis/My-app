import json
import os
from datetime import datetime
from tkinter import messagebox, END

DISMISSED_FILE = os.path.join(os.path.expanduser("~"), "Documents", "dismissed_recurring.json")

def save_task(task_file, task_data):
    tasks = []
    if os.path.exists(task_file):
        try:
            with open(task_file, "r") as f:
                tasks = json.load(f)
        except json.JSONDecodeError:
            pass
    tasks.append(task_data)
    with open(task_file, "w") as f:
        json.dump(tasks, f, indent=2)

def get_recurring_indicator(recurring_type):
    if recurring_type == "Daily":
        return "[D]"
    elif recurring_type == "Weekly":
        return "[W]"
    elif recurring_type == "Monthly":
        return "[M]"
    else:
        return ""

def get_display_text(task):
    indicator = get_recurring_indicator(task.get("recurring_type", "No"))
    due = f" | Due: {task['due']}" if task.get("due") else ""
    return f"{indicator} {task['text']} ({task['date']}){due}"

def load_tasks(task_file, listbox, date_string, dismissed_today, displayed_today):
    """
    Load tasks from the task file and display them in the listbox.
    Handles recurring and non-recurring tasks.
    """
    try:
        with open(task_file, "r") as f:
            tasks = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        tasks = []

    for task in tasks:
        recurring_type = task.get("recurring_type", "No")
        indicator = get_recurring_indicator(recurring_type)
        due = f" | Due: {task['due']}" if task.get("due") else ""
        display_text = f"{indicator} {task['text']} ({task['date']}){due}"
        if recurring_type in ["Daily", "Weekly", "Monthly"]:
            if should_show_recurring(task["text"], recurring_type):
                listbox.insert("end", display_text)
        else:
            listbox.insert("end", display_text)

def delete_task_from_file(task_file, complete_task_file, task_text, date_string):
    """
    Delete a task from the task file and add it to the completed file.
    """
    try:
        with open(task_file, "r") as f:
            tasks = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        tasks = []

    new_tasks = []
    deleted_task = None
    for task in tasks:
        if task["text"] == task_text:
            deleted_task = task
            continue
        new_tasks.append(task)

    with open(task_file, "w") as f:
        json.dump(new_tasks, f, indent=2)

    if deleted_task:
        try:
            with open(complete_task_file, "r") as f:
                completed = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            completed = []
        due = f" | Due: {deleted_task.get('due')}" if deleted_task.get("due") else ""
        completed.append(f'{deleted_task.get("text")} ({deleted_task.get("date")}){due}')
        with open(complete_task_file, "w") as f:
            json.dump(completed, f, indent=2)

def load_completed_tasks(file_path):
    """
    Load completed tasks from the completed file.
    """
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def clear_completed_tasks_file(file_path):
    """
    Clear all completed tasks from the completed file.
    """
    with open(file_path, "w") as f:
        json.dump([], f, indent=2)

def load_dismissed_recurring():
    if not os.path.exists(DISMISSED_FILE):
        return {}
    with open(DISMISSED_FILE, "r") as f:
        return json.load(f)

def save_dismissed_recurring(dismissed):
    with open(DISMISSED_FILE, "w") as f:
        json.dump(dismissed, f, indent=2)

def dismiss_recurring_task(task_text, recurring_type):
    dismissed = load_dismissed_recurring()
    today = datetime.today().strftime("%Y-%m-%d")
    dismissed[task_text] = {"date": today, "type": recurring_type}
    save_dismissed_recurring(dismissed)

def should_show_recurring(task_text, recurring_type):
    """
    Determine if a recurring task should be shown today.
    """
    # Implement your logic for recurring task display here
    # For now, always show unless dismissed
    return True

def get_task(self):
    task_text = self.task_entry.get().strip()
    due_date = self.due_entry.get().strip()
    recurring_type = self.recurring_var.get()  # Should be "No", "Daily", "Weekly", "Monthly"

    if not task_text:
        messagebox.showwarning("Input Error", "Please enter a task")
        return

    task_data = {
        "text": task_text,
        "date": self.date_string,
        "due": due_date if due_date else None,
        "recurring": recurring_type != "No",
        "recurring_type": recurring_type
    }

    if task_text in self.task_listbox.get(0, END):
        messagebox.showinfo("Duplicate Task", "This task already exists.")
        return

    save_task(self.task_file, task_data)
    self.task_entry.delete(0, END)
