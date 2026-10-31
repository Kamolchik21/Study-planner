import tkinter as tk
from datetime import date
from tkinter import ttk

from planner import tasks, workload
from planner.utils import format_minutes

from .common import fill_listbox, format_task


class TodayTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=14)
        self.app = app
        self.plan_ids = []

        self.heading = ttk.Label(self, style="Title.TLabel")
        self.heading.pack(anchor="w")
        self.summary = ttk.Label(self, style="Muted.TLabel")
        self.summary.pack(anchor="w", pady=(2, 0))
        self.warning = ttk.Label(self, style="Warn.TLabel", wraplength=860, justify="left")
        self.warning.pack(anchor="w", pady=(4, 0))

        ttk.Label(self, text="Your plan for today").pack(anchor="w", pady=(12, 3))
        self.plan_list = tk.Listbox(self, height=9, exportselection=False, font=("Helvetica", 12))
        self.plan_list.pack(fill="x")
        ttk.Button(self, text="Mark selected as done", command=self.mark_done).pack(anchor="w", pady=(8, 0))

        ttk.Label(self, text="Does not fit into today's time limit").pack(anchor="w", pady=(14, 3))
        self.later_list = tk.Listbox(self, height=5, exportselection=False)
        self.later_list.pack(fill="x")

        self.heavy = ttk.Label(self, style="Warn.TLabel", wraplength=860, justify="left")
        self.heavy.pack(anchor="w", pady=(12, 0))

    def refresh(self):
        data = self.app.data
        result = workload.today_plan(data)
        self.plan_ids = [t["id"] for t in result["plan"]]

        self.heading.configure(text=f"Today, {date.today().strftime('%A %d %B %Y')}")
        self.summary.configure(
            text=f"Planned: {format_minutes(result['minutes'])} of {format_minutes(result['limit'])} daily limit"
        )
        if not result["plan"]:
            self.warning.configure(text="")
            fill_listbox(self.plan_list, ["Nothing urgent. Add tasks in the Tasks tab."])
        else:
            self.warning.configure(
                text="Your first task alone is longer than your daily limit." if result["minutes"] > result["limit"] else ""
            )
            fill_listbox(self.plan_list, [format_task(t) for t in result["plan"]])
        fill_listbox(self.later_list, [format_task(t) for t in result["later"]])

        heavy = workload.overloaded_days(data)
        if heavy:
            days = ", ".join(f"{day} ({format_minutes(minutes)})" for day, minutes in heavy[:5])
            self.heavy.configure(text=f"Heavy days ahead: {days}")
        else:
            self.heavy.configure(text="")

    def mark_done(self):
        selection = self.plan_list.curselection()
        if not selection or selection[0] >= len(self.plan_ids):
            return
        try:
            tasks.mark_done(self.app.data, self.plan_ids[selection[0]])
        except ValueError as error:
            self.app.error(str(error))
            return
        self.app.commit()
