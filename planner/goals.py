from .storage import new_id
from .utils import parse_date


def add_goal(data, title, kind, deadline=""):
    title = title.strip()
    if not title:
        raise ValueError("Goal cannot be empty.")
    if kind not in ("short", "long"):
        raise ValueError("Goal type must be short or long.")
    deadline = deadline.strip()
    if deadline:
        try:
            deadline = parse_date(deadline).isoformat()
        except ValueError:
            raise ValueError("Target date must look like 2026-11-05 (or be empty).")
    goal = {"id": new_id(data), "title": title, "type": kind, "deadline": deadline, "done": False}
    data["goals"].append(goal)
    return goal


def find_goal(data, goal_id):
    for goal in data["goals"]:
        if goal["id"] == goal_id:
            return goal
    raise ValueError("Goal not found.")


def complete_goal(data, goal_id):
    find_goal(data, goal_id)["done"] = True


def delete_goal(data, goal_id):
    data["goals"].remove(find_goal(data, goal_id))


def goals_by_type(data, kind):
    return [g for g in data["goals"] if g["type"] == kind]
