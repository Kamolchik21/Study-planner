import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from planner import attempts, reminders
from planner.config import DATA_FILE
from planner.storage import load_data, save_data

from .compare_tab import CompareTab
from .dialogs import ask_form
from .goals_tab import GoalsTab
from .pomodoro_tab import PomodoroTab
from .progress_tab import ProgressTab
from .reminders_tab import RemindersTab
from .tasks_tab import TasksTab
from .theme import THEMES, apply_theme
from .today_tab import TodayTab


class App(tk.Tk):
    def __init__(self, data_path=DATA_FILE):
        super().__init__()
        self.data_path = data_path
        self.data = load_data(data_path)
        self.title("Smart Study Planner")
        self.geometry("1020x700")
        self.minsize(880, 580)

        top = ttk.Frame(self, padding=(14, 10, 14, 0))
        top.pack(fill="x")
        ttk.Label(top, text="Smart Study Planner", style="Title.TLabel").pack(side="left")

        self.theme_var = tk.StringVar(value=self.data["settings"]["theme"])
        theme_box = ttk.Combobox(top, textvariable=self.theme_var, values=list(THEMES.keys()),
                                 state="readonly", width=7)
        theme_box.pack(side="right")
        theme_box.bind("<<ComboboxSelected>>", lambda event: self.change_theme())
        ttk.Label(top, text="Theme:").pack(side="right", padx=(16, 6))

        self.limit_var = tk.StringVar(value=str(self.data["settings"]["daily_limit_minutes"]))
        limit_spin = ttk.Spinbox(top, from_=30, to=1440, increment=30, width=6,
                                 textvariable=self.limit_var, command=self.change_limit)
        limit_spin.pack(side="right")
        limit_spin.bind("<Return>", lambda event: self.change_limit())
        limit_spin.bind("<FocusOut>", lambda event: self.change_limit())
        ttk.Label(top, text="Daily limit (min):").pack(side="right", padx=(16, 6))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        self.tabs = []
        for title, tab_class in [
            ("Today", TodayTab),
            ("Tasks", TasksTab),
            ("Goals", GoalsTab),
            ("Reminders", RemindersTab),
            ("Compare", CompareTab),
            ("Pomodoro", PomodoroTab),
            ("Progress", ProgressTab),
        ]:
            tab = tab_class(self.notebook, self)
            self.notebook.add(tab, text=title)
            self.tabs.append(tab)

        apply_theme(self, self.data["settings"]["theme"])
        self.refresh_all()
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.after(500, self.check_reminders)

    def save(self):
        save_data(self.data, self.data_path)

    def commit(self):
        self.save()
        self.refresh_all()

    def refresh_all(self):
        for tab in self.tabs:
            tab.refresh()

    def error(self, message, parent=None):
        messagebox.showerror("Oops", message, parent=parent or self)

    def restyle_window(self, window):
        from .theme import restyle
        restyle(window, THEMES[self.data["settings"]["theme"]])

    def change_theme(self):
        name = self.theme_var.get()
        self.data["settings"]["theme"] = name
        apply_theme(self, name)
        self.save()
        self.refresh_all()

    def change_limit(self):
        try:
            minutes = int(self.limit_var.get())
        except ValueError:
            minutes = self.data["settings"]["daily_limit_minutes"]
        minutes = min(max(minutes, 30), 1440)
        self.limit_var.set(str(minutes))
        if minutes != self.data["settings"]["daily_limit_minutes"]:
            self.data["settings"]["daily_limit_minutes"] = minutes
            self.commit()

    def log_attempt(self, task_id):
        fields = [
            ("score", "Score (0-100)", "text", None, ""),
            ("note", "How did you answer? (short note)", "text", None, ""),
            ("repeat", "Remind me to repeat in (days, 0 = no)", "text", None, "7"),
        ]
        result = ask_form(self, "Log attempt", fields)
        if not result:
            return
        try:
            attempts.add_attempt(self.data, task_id, result["score"], result["note"], result["repeat"])
        except ValueError as error:
            self.error(str(error))
            return
        self.commit()

    def check_reminders(self):
        due = reminders.due_reminders(self.data)
        if due:
            reminders.mark_shown(due)
            self.commit()
            messagebox.showinfo("Reminder", "\n".join(f"- {r['text']}" for r in due), parent=self)
        self.after(30000, self.check_reminders)

    def close(self):
        self.save()
        self.destroy()
