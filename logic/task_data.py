import json
import os

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

def load_tasks(task_file, listbox, date_string, dismissed_recurring_today, displayed_recurring_today):
    try:
        with open(task_file, "r") as f:
            tasks = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        tasks = []

    for task in tasks:
        if task["recurring"] and task["text"] in dismissed_recurring_today:
            continue
        if task["recurring"] and task["text"] in displayed_recurring_today:
            continue
        if not task["recurring"] and task["date"] != date_string:
            continue

        task_str = task["text"]
        if task["due"]:
            task_str += f" (Due: {task['due']})"
        listbox.insert("end", task_str)

        if task["recurring"]:
            displayed_recurring_today.add(task["text"])

def delete_task_from_file(task_file, completed_file, text, date_string):
    try:
        with open(task_file, "r") as f:
            tasks = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        tasks = []

    new_tasks = [t for t in tasks if t["text"] != text or (t["recurring"] and t["date"] != date_string)]
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

def load_dismissed_recurring(file_path, date_str):
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            return data.get(date_str, [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_dismissed_recurring(file_path, task_list, date_str):
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    data[date_str] = task_list

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
