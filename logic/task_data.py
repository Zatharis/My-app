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
    return f"{indicator} {task['text']} ({task['date']})"

def load_tasks(task_file, listbox, date_string, dismissed_today, displayed_today):
    try:
        with open(task_file, "r") as f:
            tasks = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        tasks = []

    for task in tasks:
        recurring_type = task.get("recurring_type", "No")
        display_text = get_display_text(task)
        if recurring_type in ["Daily", "Weekly", "Monthly"]:
            if should_show_recurring(task["text"], recurring_type):
                listbox.insert("end", display_text)
        else:
            listbox.insert("end", display_text)

def delete_task_from_file(task_file, completed_file, text, date_string):
    try:
        with open(task_file, "r") as f:
            tasks = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        tasks = []

    new_tasks = [t for t in tasks if t["text"] != text or (t.get("recurring", False) and t["date"] != date_string)]
    deleted = [t for t in tasks if t["text"] == text]

    if deleted:
        try:
            with open(completed_file, "r") as f:
                completed = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            completed = []

        completed.append(text)
        with open(completed_file, "w") as f:
            json.dump(completed, f, indent=2)

    with open(task_file, "w") as f:
        json.dump(new_tasks, f, indent=2)

def load_completed_tasks(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def clear_completed_tasks_file(file_path):
    with open(file_path, "w") as f:
        json.dump([], f)

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
    dismissed = load_dismissed_recurring()
    info = dismissed.get(task_text)
    if not info:
        return True  # Not dismissed

    try: 
        last_date = datetime.strptime(info["date"], "%Y-%m-%d")
    except Exception:
        return True  # Malformed date, show task

    today = datetime.today()

    if recurring_type == "Daily":
        return (today.date() != last_date.date())
    elif recurring_type == "Weekly":
        # Show if not dismissed in the same ISO week
        return today.isocalendar()[1] != last_date.isocalendar()[1] or today.year != last_date.year
    elif recurring_type == "Monthly":
        return today.month != last_date.month or today.year != last_date.year
    else:
        return True  # Not recurring or unknown type

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
