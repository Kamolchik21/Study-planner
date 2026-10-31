from tkinter import ttk

from planner import stats
from planner.utils import format_minutes


class ProgressTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=14)
        self.app = app

        ttk.Label(self, text="Your progress", style="Title.TLabel").pack(anchor="w")
        self.streak_label = ttk.Label(self, font=("Helvetica", 13))
        self.streak_label.pack(anchor="w", pady=(6, 0))
        self.time_label = ttk.Label(self, style="Muted.TLabel")
        self.time_label.pack(anchor="w", pady=(2, 10))
        self.bars = ttk.Frame(self)
        self.bars.pack(fill="both", expand=True)
        self.bars.columnconfigure(1, weight=1)

    def add_bar(self, row, name, done, total, extra=""):
        ttk.Label(self.bars, text=name, width=14).grid(row=row, column=0, sticky="w", pady=4)
        bar = ttk.Progressbar(self.bars, maximum=max(total, 1), value=done)
        bar.grid(row=row, column=1, sticky="ew", padx=10, pady=4)
        text = f"{done}/{total}" if total else "no tasks"
        ttk.Label(self.bars, text=f"{text}   {extra}").grid(row=row, column=2, sticky="w")

    def refresh(self):
        data = self.app.data
        days = stats.streak(data)
        self.streak_label.configure(text=f"Streak: {days} day(s) in a row")
        self.time_label.configure(text=f"Focused time today: {format_minutes(stats.minutes_today(data))}")

        for child in self.bars.winfo_children():
            child.destroy()
        minutes = stats.study_minutes_by_subject(data)
        row = 0
        done, total = stats.overall_progress(data)
        self.add_bar(row, "All tasks", done, total)
        row += 1
        for subject, done, total in stats.subject_progress(data):
            extra = f"studied {format_minutes(minutes[subject])}" if subject in minutes else ""
            self.add_bar(row, subject, done, total, extra)
            row += 1
        done, total = stats.goals_progress(data)
        self.add_bar(row, "Goals", done, total)
