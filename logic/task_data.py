import json
import os
from datetime import date, datetime
from tkinter import messagebox, END
from logic.utils import format_date, parse_date

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

def display_tasks_in_listbox(task_file, listbox, date_format, dismissed_today, displayed_today):
    listbox.delete(0, END)
    """
    Load tasks from the task file and display them in the listbox.
    Handles recurring and non-recurring tasks.
    """
    try:
        with open(task_file, "r") as f:
            tasks = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        tasks = []

    today_str = format_date(date.today(), date_format)
    for task in tasks:
        show_date = task.get("due") or task.get("date")
        parsed = parse_date(show_date, date_format)
        recurring_type = task.get("recurring_type", "No")
        indicator = get_recurring_indicator(recurring_type)
        due = f" | Due: {task['due']}" if task.get("due") else ""

        # Format the date for display
        try:
            dt = parse_date(task["date"], date_format)
            if dt:
                display_date = format_date(dt, date_format)
            else:
                display_date = task["date"]  # fallback if parsing fails
        except Exception:
            display_date = task["date"]  # fallback if parsing fails

        display_text = f"{indicator} {task['text']} ({display_date}){due}"

        if recurring_type in ["Daily", "Weekly", "Monthly"]:
            # Always show recurring tasks for today unless dismissed/completed for today
            if should_show_recurring(task["text"], recurring_type, date_format, check_date=today_str):
                listbox.insert("end", f"{indicator} {task['text']} ({today_str}){due}")
        else:
            listbox.insert("end", display_text)

      # Clear existing items
    dismissed_today = set()
    displayed_today = set()
    

def delete_task_from_file(task_file, complete_task_file, task_text, date_string, date_format):
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
            "completed_on": format_date(date.today(), date_format)  # Use user format
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

def dismiss_recurring_task(task_text, recurring_type, date_format, dismiss_date=None):
    dismissed = load_dismissed_recurring()
    if dismiss_date is None:
        dismiss_date = date.today()
    dismiss_str = format_date(dismiss_date, date_format)
    key = f"{task_text}|{recurring_type}"
    if key not in dismissed:
        dismissed[key] = {"dates": [], "type": recurring_type}
    if "dates" not in dismissed[key] or not isinstance(dismissed[key]["dates"], list):
        dismissed[key]["dates"] = []
    if dismiss_str not in dismissed[key]["dates"]:
        dismissed[key]["dates"].append(dismiss_str)
    save_dismissed_recurring(dismissed)

def should_show_recurring(task_text, recurring_type, date_format, check_date=None):
    """
    Returns True if the recurring task should be shown on the given date,
    and False if it was dismissed for that date.
    """
    dismissed = load_dismissed_recurring()
    key = f"{task_text}|{recurring_type}"
    info = dismissed.get(key)
    if not info or info.get("type") != recurring_type:
        return True

    # Determine which date to check
    if check_date is None:
        check_date = format_date(date.today(), date_format)
    else:
        # If check_date is a datetime/date object, format it
        if isinstance(check_date, (datetime, date)):
            check_date = format_date(check_date, date_format)

    # If the date is in the dismissed list, do not show
    dismissed_dates = info.get("dates", [])
    # Normalize all dismissed dates to the current format for comparison
    normalized_dismissed = set()
    for d in dismissed_dates:
        parsed = parse_date(d, date_format)
        if parsed:
            normalized_dismissed.add(format_date(parsed, date_format))
        else:
            normalized_dismissed.add(d)
    return check_date not in normalized_dismissed

def load_tasks(task_file):
    if not os.path.exists(task_file):
        return []
    try:
        with open(task_file, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Don't overwrite the file, just return empty
        return []
