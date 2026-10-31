from datetime import date, datetime, timedelta

from .config import REVIEW_DAYS
from .storage import new_id

WHEN_FORMAT = "%Y-%m-%d %H:%M"


def add_reminder(data, text, day, hour):
    text = text.strip()
    if not text:
        raise ValueError("Reminder text cannot be empty.")
    try:
        when = datetime.strptime(f"{day.strip()} {hour.strip()}", WHEN_FORMAT)
    except ValueError:
        raise ValueError("Use date YYYY-MM-DD and time HH:MM, for example 2026-11-05 and 18:30.")
    reminder = {"id": new_id(data), "text": text, "when": when.strftime(WHEN_FORMAT), "shown": False}
    data["reminders"].append(reminder)
    return reminder


def add_review_reminders(data, title, subject, start=None):
    start = start or date.today()
    for days in REVIEW_DAYS:
        day = start + timedelta(days=days)
        add_reminder(data, f"Review: {title} ({subject})", str(day), "09:00")


def due_reminders(data, now=None):
    now = now or datetime.now()
    due = []
    for r in data["reminders"]:
        when = datetime.strptime(r["when"], WHEN_FORMAT)
        if not r["shown"] and when <= now:
            due.append(r)
    return due


def mark_shown(reminders):
    for r in reminders:
        r["shown"] = True


def upcoming_reminders(data):
    items = [r for r in data["reminders"] if not r["shown"]]
    items.sort(key=lambda r: r["when"])
    return items


def delete_reminder(data, reminder_id):
    for r in data["reminders"]:
        if r["id"] == reminder_id:
            data["reminders"].remove(r)
            return
    raise ValueError("Reminder not found.")
