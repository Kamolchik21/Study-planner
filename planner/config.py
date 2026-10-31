import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "planner_data.json")

URGENT_DAYS = 2
SOON_DAYS = 7
REVIEW_DAYS = [1, 3, 7]
DEFAULT_TASK_MINUTES = 30

DEFAULT_SUBJECTS = ["Math", "Physics", "English", "ESS", "Russian", "Economics", "SAT", "IELTS"]

DEFAULT_SETTINGS = {
    "theme": "light",
    "daily_limit_minutes": 240,
    "pomodoro_work": 25,
    "pomodoro_break": 5,
}
