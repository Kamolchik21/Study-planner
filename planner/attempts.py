from datetime import date, timedelta

from .reminders import add_reminder
from .tasks import get_task
from .utils import parse_date


def add_attempt(data, task_id, score, note="", repeat_in_days=0, day=None):
    task = get_task(data, task_id)
    if task is None:
        raise ValueError("Task not found.")
    try:
        score = float(str(score).replace(",", "."))
    except ValueError:
        raise ValueError("Score must be a number from 0 to 100.")
    if not 0 <= score <= 100:
        raise ValueError("Score must be a number from 0 to 100.")
    try:
        repeat_in_days = int(str(repeat_in_days).strip() or 0)
    except ValueError:
        raise ValueError("Repeat after must be a whole number of days (0 = no reminder).")
    if repeat_in_days < 0:
        raise ValueError("Repeat after cannot be negative.")
    day = day or date.today()
    attempt = {"date": str(day), "score": score, "note": note.strip()}
    task["attempts"].append(attempt)
    task["attempts"].sort(key=lambda a: a["date"])
    if repeat_in_days > 0:
        remind_day = date.today() + timedelta(days=repeat_in_days)
        add_reminder(data, f"Repeat and compare: {task['title']} ({task['subject']})", str(remind_day), "09:00")
    return attempt


def compare_attempts(task):
    attempts = task.get("attempts", [])
    if len(attempts) < 2:
        return None
    first, last = attempts[0], attempts[-1]
    change = round(last["score"] - first["score"], 1)
    days = (parse_date(last["date"]) - parse_date(first["date"])).days
    if change > 0:
        trend = "improved"
    elif change < 0:
        trend = "declined"
    else:
        trend = "same"
    scores = [a["score"] for a in attempts]
    return {
        "first": first,
        "last": last,
        "change": change,
        "days": days,
        "count": len(attempts),
        "best": max(scores),
        "average": round(sum(scores) / len(scores), 1),
        "trend": trend,
    }
