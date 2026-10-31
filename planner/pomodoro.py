from datetime import date


class PomodoroTimer:
    def __init__(self, work_min=25, break_min=5):
        self.work_min = work_min
        self.break_min = break_min
        self.mode = "work"
        self.remaining = work_min * 60
        self.running = False

    def set_durations(self, work_min, break_min):
        self.work_min = work_min
        self.break_min = break_min
        if not self.running:
            self.remaining = (self.work_min if self.mode == "work" else self.break_min) * 60

    def start(self):
        self.running = True

    def pause(self):
        self.running = False

    def reset(self):
        self.running = False
        self.mode = "work"
        self.remaining = self.work_min * 60

    def tick(self):
        if not self.running:
            return None
        self.remaining -= 1
        if self.remaining > 0:
            return None
        finished = self.mode
        self.mode = "break" if finished == "work" else "work"
        minutes = self.break_min if self.mode == "break" else self.work_min
        self.remaining = minutes * 60
        self.running = False
        return finished

    def display(self):
        minutes, seconds = divmod(self.remaining, 60)
        return f"{minutes:02d}:{seconds:02d}"


def log_session(data, task_id, minutes, day=None):
    data["sessions"].append({"date": str(day or date.today()), "task_id": task_id, "minutes": minutes})
