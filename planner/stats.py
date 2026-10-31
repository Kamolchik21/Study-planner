from datetime import date, timedelta


def subject_progress(data):
    result = []
    for subject in data["subjects"]:
        items = [t for t in data["tasks"] if t["subject"] == subject]
        done = len([t for t in items if t["done"]])
        result.append((subject, done, len(items)))
    return result


def overall_progress(data):
    total = len(data["tasks"])
    done = len([t for t in data["tasks"] if t["done"]])
    return done, total


def goals_progress(data):
    total = len(data["goals"])
    done = len([g for g in data["goals"] if g["done"]])
    return done, total


def study_minutes_by_subject(data):
    subject_of = {t["id"]: t["subject"] for t in data["tasks"]}
    totals = {}
    for session in data["sessions"]:
        name = subject_of.get(session["task_id"], "No task")
        totals[name] = totals.get(name, 0) + session["minutes"]
    return totals


def minutes_today(data, today=None):
    today = str(today or date.today())
    return sum(s["minutes"] for s in data["sessions"] if s["date"] == today)


def activity_dates(data):
    days = set()
    for task in data["tasks"]:
        if task.get("done_date"):
            days.add(task["done_date"])
        for attempt in task.get("attempts", []):
            days.add(attempt["date"])
    for session in data["sessions"]:
        days.add(session["date"])
    return days


def streak(data, today=None):
    today = today or date.today()
    days = activity_dates(data)
    current = today if str(today) in days else today - timedelta(days=1)
    count = 0
    while str(current) in days:
        count += 1
        current -= timedelta(days=1)
    return count
