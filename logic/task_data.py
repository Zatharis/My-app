import json
import os
from datetime import datetime, date
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

def load_tasks(task_file, listbox, date_format, dismissed_today, displayed_today):
    listbox.delete(0, END)  # Clear existing items
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

        # Format the date for display
        try:
            dt = datetime.strptime(task["date"], "%Y-%m-%d")
            if date_format == "MM-DD-YYYY":
                display_date = dt.strftime("%m-%d-%Y")
            else:
                display_date = dt.strftime("%d-%m-%Y")
        except Exception:
            display_date = task["date"]  # fallback if parsing fails

        display_text = f"{indicator} {task['text']} ({display_date}){due}"
        if recurring_type in ["Daily", "Weekly", "Monthly"]:
            if should_show_recurring(task["text"], recurring_type):
                listbox.insert("end", display_text)
        else:
            listbox.insert("end", display_text)

      # Clear existing items
    dismissed_today = set()
    displayed_today = set()
    

def delete_task_from_file(task_file, complete_task_file, task_text, date_string):
    try:
        with open(task_file, "r") as f:
            tasks = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        tasks = []

    deleted_task = None
    for i, task in enumerate(tasks):
        if task["text"] == task_text:
            deleted_task = tasks.pop(i)
            break

    with open(task_file, "w") as f:
        json.dump(tasks, f, indent=2)

    if deleted_task:
        try:
            with open(complete_task_file, "r") as f:
                completed = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            completed = []
        completed.append({
            "text": deleted_task.get("text"),
            "date": deleted_task.get("date"),
            "due": deleted_task.get("due"),
            "recurring_type": deleted_task.get("recurring_type", "No"),
            "completed_on": datetime.today().strftime("%Y-%m-%d")  # <-- ISO format!
        })
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
    """
    Dismiss a recurring task for a specific day.
    Stores a list of dismissed dates for each task+type.
    """
    dismissed = load_dismissed_recurring()
    today = datetime.today().strftime("%Y-%m-%d")
    key = f"{task_text}|{recurring_type}"
    # Always ensure 'dates' is a list
    if key not in dismissed:
        dismissed[key] = {"dates": [], "type": recurring_type}
    if "dates" not in dismissed[key] or not isinstance(dismissed[key]["dates"], list):
        dismissed[key]["dates"] = []
    if today not in dismissed[key]["dates"]:
        dismissed[key]["dates"].append(today)
    save_dismissed_recurring(dismissed)

def should_show_recurring(task_text, recurring_type, check_date=None):
    """
    Determine if a recurring task should be shown, based on its dismissal and type.
    Uses a composite key to match the correct recurrence.
    If check_date is None, uses today.
    """
    dismissed = load_dismissed_recurring()
    key = f"{task_text}|{recurring_type}"
    info = dismissed.get(key)
    if not info or info.get("type") != recurring_type:
        return True

    if check_date is None:
        check_date = datetime.today().strftime("%Y-%m-%d")
    return check_date not in info.get("dates", [])
