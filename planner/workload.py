from .config import SOON_DAYS, URGENT_DAYS
from .tasks import pending_tasks, quadrant, task_minutes
from .utils import days_left, format_minutes


def daily_limit(data):
    return data["settings"]["daily_limit_minutes"]


def minutes_due_on(data, day):
    return sum(task_minutes(t) for t in pending_tasks(data) if t["deadline"] == day)


def day_overload_message(data, day):
    total = minutes_due_on(data, day)
    limit = daily_limit(data)
    if total <= limit:
        return ""
    return (
        f"On {day} you have {format_minutes(total)} of work due, "
        f"but your daily limit is {format_minutes(limit)}. "
        "Consider moving a deadline or raising the limit."
    )


def overloaded_days(data):
    totals = {}
    for task in pending_tasks(data):
        totals[task["deadline"]] = totals.get(task["deadline"], 0) + task_minutes(task)
    limit = daily_limit(data)
    result = [(day, minutes) for day, minutes in totals.items() if minutes > limit and days_left(day) >= 0]
    result.sort()
    return result


def today_plan(data):
    candidates = []
    for task in pending_tasks(data):
        left = days_left(task["deadline"])
        if left <= URGENT_DAYS or (task["important"] and left <= SOON_DAYS):
            candidates.append(task)
    candidates.sort(key=lambda t: (quadrant(t), t["deadline"]))

    limit = daily_limit(data)
    plan, later, used = [], [], 0
    for task in candidates:
        minutes = task_minutes(task)
        if not plan or used + minutes <= limit:
            plan.append(task)
            used += minutes
        else:
            later.append(task)
    return {"plan": plan, "later": later, "minutes": used, "limit": limit}
