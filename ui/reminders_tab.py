import tkinter as tk
from datetime import date, timedelta
from tkinter import ttk

from planner import reminders

from .common import fill_listbox
from .dialogs import ask_form


class RemindersTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=14)
        self.app = app
        self.ids = []

        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=(0, 10))
        ttk.Button(bar, text="Add reminder", command=self.add).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="Delete", command=self.delete).pack(side="left")

        ttk.Label(self, text="Upcoming reminders", style="Title.TLabel").pack(anchor="w", pady=(0, 4))
        self.listbox = tk.Listbox(self, exportselection=False, activestyle="none")
        self.listbox.pack(fill="both", expand=True)
        ttk.Label(self, style="Muted.TLabel",
                  text="Reminders pop up while the program is open. Finished tasks add review reminders automatically."
                  ).pack(anchor="w", pady=(8, 0))

    def refresh(self):
        items = reminders.upcoming_reminders(self.app.data)
        self.ids = [r["id"] for r in items]
        fill_listbox(self.listbox, [f"{r['when']}   {r['text']}" for r in items])

    def add(self):
        tomorrow = str(date.today() + timedelta(days=1))
        fields = [
            ("text", "Reminder", "text", None, ""),
            ("day", "Date (YYYY-MM-DD)", "text", None, tomorrow),
            ("hour", "Time (HH:MM)", "text", None, "09:00"),
        ]
        result = ask_form(self, "Add reminder", fields)
        if not result:
            return
        try:
            reminders.add_reminder(self.app.data, result["text"], result["day"], result["hour"])
        except ValueError as error:
            self.app.error(str(error))
            return
        self.app.commit()

    def delete(self):
        selection = self.listbox.curselection()
        if not selection or selection[0] >= len(self.ids):
            self.app.error("Select a reminder first.")
            return
        try:
            reminders.delete_reminder(self.app.data, self.ids[selection[0]])
        except ValueError as error:
            self.app.error(str(error))
            return
        self.app.commit()
