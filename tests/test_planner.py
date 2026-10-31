import json
import os
import tempfile
import unittest
from datetime import date, datetime, timedelta

from planner import attempts, goals, pomodoro, reminders, stats, subjects, tasks, workload
from planner.storage import default_data, load_data, save_data


def in_days(n):
    return str(date.today() + timedelta(days=n))


class TaskTests(unittest.TestCase):
    def setUp(self):
        self.data = default_data()

    def test_quadrants(self):
        urgent_important = tasks.add_task(self.data, "A", "Math", in_days(1), True)
        important_later = tasks.add_task(self.data, "B", "Math", in_days(10), True)
        urgent_minor = tasks.add_task(self.data, "C", "Math", in_days(0), False)
        minor_later = tasks.add_task(self.data, "D", "Math", in_days(10), False)
        self.assertEqual(tasks.quadrant(urgent_important), 1)
        self.assertEqual(tasks.quadrant(important_later), 2)
        self.assertEqual(tasks.quadrant(urgent_minor), 3)
        self.assertEqual(tasks.quadrant(minor_later), 4)

    def test_overdue_is_urgent(self):
        task = tasks.add_task(self.data, "Late", "Math", in_days(-3), True)
        self.assertEqual(tasks.quadrant(task), 1)

    def test_validation(self):
        with self.assertRaises(ValueError):
            tasks.add_task(self.data, " ", "Math", in_days(1), True)
        with self.assertRaises(ValueError):
            tasks.add_task(self.data, "x", "Nope", in_days(1), True)
        with self.assertRaises(ValueError):
            tasks.add_task(self.data, "x", "Math", "05.11.2026", True)
        with self.assertRaises(ValueError):
            tasks.add_task(self.data, "x", "Math", in_days(1), True, "abc")

    def test_date_is_normalized(self):
        task = tasks.add_task(self.data, "x", "Math", "2030-1-5", True)
        self.assertEqual(task["deadline"], "2030-01-05")

    def test_mark_done_creates_review_reminders(self):
        task = tasks.add_task(self.data, "Essay", "English", in_days(3), True)
        tasks.mark_done(self.data, task["id"])
        self.assertTrue(task["done"])
        self.assertEqual(len(self.data["reminders"]), 3)
        with self.assertRaises(ValueError):
            tasks.mark_done(self.data, task["id"])

    def test_delete(self):
        task = tasks.add_task(self.data, "x", "Math", in_days(3), True)
        tasks.delete_task(self.data, task["id"])
        self.assertEqual(self.data["tasks"], [])


class SubjectTests(unittest.TestCase):
    def test_add_remove_rules(self):
        data = default_data()
        subjects.add_subject(data, "Chess")
        with self.assertRaises(ValueError):
            subjects.add_subject(data, "chess")
        tasks.add_task(data, "Study", "Chess", in_days(2), True)
        with self.assertRaises(ValueError):
            subjects.remove_subject(data, "Chess")
        tasks.delete_task(data, data["tasks"][0]["id"])
        subjects.remove_subject(data, "Chess")
        self.assertNotIn("Chess", data["subjects"])


class GoalReminderTests(unittest.TestCase):
    def test_goals(self):
        data = default_data()
        goal = goals.add_goal(data, "Get 1500 on SAT", "long", in_days(100))
        goals.complete_goal(data, goal["id"])
        self.assertEqual(len(goals.goals_by_type(data, "long")), 1)
        self.assertTrue(goal["done"])
        with self.assertRaises(ValueError):
            goals.add_goal(data, "x", "medium")

    def test_reminders_due(self):
        data = default_data()
        reminders.add_reminder(data, "Past", "2020-01-01", "08:00")
        reminders.add_reminder(data, "Future", "2999-01-01", "08:00")
        due = reminders.due_reminders(data)
        self.assertEqual([r["text"] for r in due], ["Past"])
        reminders.mark_shown(due)
        self.assertEqual(reminders.due_reminders(data), [])
        with self.assertRaises(ValueError):
            reminders.add_reminder(data, "x", "bad", "25:99")


class AttemptTests(unittest.TestCase):
    def test_compare(self):
        data = default_data()
        task = tasks.add_task(data, "SAT Math test 1", "SAT", in_days(20), True)
        self.assertIsNone(attempts.compare_attempts(task))
        attempts.add_attempt(data, task["id"], 55, "Weak at geometry", day=date.today() - timedelta(days=14))
        attempts.add_attempt(data, task["id"], 78, "Geometry is fine now", repeat_in_days=7)
        result = attempts.compare_attempts(task)
        self.assertEqual(result["change"], 23)
        self.assertEqual(result["days"], 14)
        self.assertEqual(result["trend"], "improved")
        self.assertEqual(result["best"], 78)
        self.assertEqual(len(data["reminders"]), 1)

    def test_invalid_score(self):
        data = default_data()
        task = tasks.add_task(data, "x", "Math", in_days(5), True)
        for bad in ["abc", "101", "-1"]:
            with self.assertRaises(ValueError):
                attempts.add_attempt(data, task["id"], bad)


class WorkloadTests(unittest.TestCase):
    def test_overload_message(self):
        data = default_data()
        data["settings"]["daily_limit_minutes"] = 120
        tasks.add_task(data, "A", "Math", in_days(2), True, 90)
        tasks.add_task(data, "B", "Physics", in_days(2), True, 60)
        self.assertIn("daily limit", workload.day_overload_message(data, in_days(2)))
        self.assertEqual(workload.day_overload_message(data, in_days(5)), "")
        self.assertEqual(len(workload.overloaded_days(data)), 1)

    def test_today_plan_respects_limit(self):
        data = default_data()
        data["settings"]["daily_limit_minutes"] = 100
        tasks.add_task(data, "A", "Math", in_days(0), True, 60)
        tasks.add_task(data, "B", "Physics", in_days(1), True, 60)
        tasks.add_task(data, "Far", "ESS", in_days(30), False, 60)
        result = workload.today_plan(data)
        self.assertEqual([t["title"] for t in result["plan"]], ["A"])
        self.assertEqual([t["title"] for t in result["later"]], ["B"])
        self.assertEqual(result["minutes"], 60)


class PomodoroStatsTests(unittest.TestCase):
    def test_timer_switches_modes(self):
        timer = pomodoro.PomodoroTimer(work_min=1, break_min=1)
        self.assertIsNone(timer.tick())
        timer.start()
        finished = None
        for _ in range(60):
            finished = timer.tick()
        self.assertEqual(finished, "work")
        self.assertEqual(timer.mode, "break")
        self.assertFalse(timer.running)
        self.assertEqual(timer.display(), "01:00")

    def test_streak_and_minutes(self):
        data = default_data()
        task = tasks.add_task(data, "x", "Math", in_days(5), True)
        pomodoro.log_session(data, task["id"], 25)
        pomodoro.log_session(data, None, 25, day=date.today() - timedelta(days=1))
        pomodoro.log_session(data, None, 25, day=date.today() - timedelta(days=2))
        pomodoro.log_session(data, None, 25, day=date.today() - timedelta(days=4))
        self.assertEqual(stats.streak(data), 3)
        self.assertEqual(stats.minutes_today(data), 25)
        self.assertEqual(stats.study_minutes_by_subject(data), {"Math": 25, "No task": 75})

    def test_progress(self):
        data = default_data()
        a = tasks.add_task(data, "a", "Math", in_days(5), True)
        tasks.add_task(data, "b", "Math", in_days(5), True)
        tasks.mark_done(data, a["id"])
        self.assertEqual(stats.overall_progress(data), (1, 2))
        self.assertIn(("Math", 1, 2), stats.subject_progress(data))


class StorageTests(unittest.TestCase):
    def test_roundtrip_and_migration(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "data.json")
            old = {"subjects": ["Math"], "tasks": [{"id": 1, "title": "t", "subject": "Math",
                   "deadline": "2030-01-01", "important": True, "done": False, "done_date": ""}],
                   "goals": [], "reminders": [], "next_id": 2}
            with open(path, "w", encoding="utf-8") as f:
                json.dump(old, f)
            data = load_data(path)
            self.assertEqual(data["tasks"][0]["attempts"], [])
            self.assertEqual(data["settings"]["theme"], "light")
            self.assertEqual(data["sessions"], [])
            data["settings"]["theme"] = "dark"
            save_data(data, path)
            self.assertEqual(load_data(path)["settings"]["theme"], "dark")

    def test_corrupted_file_is_backed_up(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "data.json")
            with open(path, "w") as f:
                f.write("{not json")
            data = load_data(path)
            self.assertEqual(data["tasks"], [])
            self.assertTrue(os.path.exists(path + ".bak"))


if __name__ == "__main__":
    unittest.main()
