from datetime import date

from .config import DEFAULT_TASK_MINUTES, URGENT_DAYS
from .reminders import add_review_reminders
from .storage import new_id
from .utils import days_left, parse_date

QUADRANT_NAMES = {
    1: "Urgent + Important: do it NOW",
    2: "Important, not urgent: plan it",
    3: "Urgent, not important: do it quickly",
    4: "Not urgent, not important: later",
}


def is_urgent(task):
    return days_left(task["deadline"]) <= URGENT_DAYS


def quadrant(task):
    urgent = is_urgent(task)
    important = task["important"]
    if urgent and important:
        return 1
    if important and not urgent:
        return 2
    if urgent and not important:
        return 3
    return 4


def task_minutes(task):
    return task.get("estimate_min") or DEFAULT_TASK_MINUTES


def add_task(data, title, subject, deadline, important, estimate_min=0):
    title = title.strip()
    if not title:
        raise ValueError("Title cannot be empty.")
    if subject not in data["subjects"]:
        raise ValueError("Please choose a subject (add one first if the list is empty).")
    try:
        deadline = parse_date(deadline).isoformat()
    except ValueError:
        raise ValueError("Deadline must look like 2026-11-05.")
    try:
        estimate_min = int(str(estimate_min).strip() or 0)
    except ValueError:
        raise ValueError("Time needed must be a whole number of minutes.")
    if not 0 <= estimate_min <= 1440:
        raise ValueError("Time needed must be between 0 and 1440 minutes.")
    task = {
        "id": new_id(data),
        "title": title,
        "subject": subject,
        "deadline": deadline,
        "important": bool(important),
        "estimate_min": estimate_min,
        "done": False,
        "done_date": "",
        "attempts": [],
    }
    data["tasks"].append(task)
    return task


def get_task(data, task_id):
    for task in data["tasks"]:
        if task["id"] == task_id:
            return task
    return None


def pending_tasks(data):
    return [t for t in data["tasks"] if not t["done"]]


def tasks_by_quadrant(data):
    groups = {1: [], 2: [], 3: [], 4: []}
    for task in pending_tasks(data):
        groups[quadrant(task)].append(task)
    for group in groups.values():
        group.sort(key=lambda t: t["deadline"])
    return groups


def mark_done(data, task_id):
    task = get_task(data, task_id)
    if task is None or task["done"]:
        raise ValueError("Task not found.")
    task["done"] = True
    task["done_date"] = str(date.today())
    add_review_reminders(data, task["title"], task["subject"])
    return task


def delete_task(data, task_id):
    task = get_task(data, task_id)
    if task is None:
        raise ValueError("Task not found.")
    data["tasks"].remove(task)
