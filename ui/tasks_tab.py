import tkinter as tk
from datetime import date, timedelta
from tkinter import messagebox, ttk

from planner import tasks, workload

from .common import fill_listbox, format_task
from .dialogs import SubjectsDialog, ask_form
from .theme import QUADRANT_COLORS


class TasksTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=14)
        self.app = app
        self.lists = {}
        self.ids = {1: [], 2: [], 3: [], 4: []}

        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=(0, 10))
        buttons = [
            ("Add task", self.add_task),
            ("Mark done", self.mark_done),
            ("Delete", self.delete_task),
            ("Log attempt", self.log_attempt),
            ("Subjects", self.open_subjects),
        ]
        for text, command in buttons:
            ttk.Button(bar, text=text, command=command).pack(side="left", padx=(0, 6))

        grid = ttk.Frame(self)
        grid.pack(fill="both", expand=True)
        grid.columnconfigure((0, 1), weight=1, uniform="col")
        grid.rowconfigure((0, 1), weight=1, uniform="row")

        positions = {1: (0, 0), 2: (0, 1), 3: (1, 0), 4: (1, 1)}
        for q, (row, column) in positions.items():
            cell = tk.Frame(grid)
            cell.grid(row=row, column=column, sticky="nsew", padx=4, pady=4)
            header = tk.Label(cell, text=tasks.QUADRANT_NAMES[q], bg=QUADRANT_COLORS[q], fg="white",
                              font=("Helvetica", 11, "bold"), anchor="w", padx=8, pady=5)
            header.keep_color = True
            header.pack(fill="x")
            listbox = tk.Listbox(cell, exportselection=False, activestyle="none")
            listbox.pack(fill="both", expand=True)
            listbox.bind("<<ListboxSelect>>", lambda event, number=q: self.on_select(number))
            self.lists[q] = listbox

    def on_select(self, quadrant_number):
        for q, listbox in self.lists.items():
            if q != quadrant_number:
                listbox.selection_clear(0, "end")

    def selected_id(self):
        for q, listbox in self.lists.items():
            selection = listbox.curselection()
            if selection and selection[0] < len(self.ids[q]):
                return self.ids[q][selection[0]]
        return None

    def refresh(self):
        groups = tasks.tasks_by_quadrant(self.app.data)
        for q, listbox in self.lists.items():
            self.ids[q] = [t["id"] for t in groups[q]]
            fill_listbox(listbox, [format_task(t) for t in groups[q]])

    def add_task(self):
        subjects = self.app.data["subjects"]
        if not subjects:
            self.app.error("Add a subject first (Subjects button).")
            return
        tomorrow = str(date.today() + timedelta(days=1))
        fields = [
            ("title", "Title", "text", None, ""),
            ("subject", "Subject", "combo", subjects, subjects[0]),
            ("deadline", "Deadline (YYYY-MM-DD)", "text", None, tomorrow),
            ("important", "Important", "check", None, True),
            ("estimate", "Time needed (minutes)", "text", None, "30"),
        ]
        result = ask_form(self, "Add task", fields)
        if not result:
            return
        try:
            task = tasks.add_task(self.app.data, result["title"], result["subject"], result["deadline"],
                                  result["important"], result["estimate"])
        except ValueError as error:
            self.app.error(str(error))
            return
        self.app.commit()
        warning = workload.day_overload_message(self.app.data, task["deadline"])
        if warning:
            messagebox.showwarning("Heavy day", warning, parent=self.app)

    def mark_done(self):
        task_id = self.selected_id()
        if task_id is None:
            self.app.error("Select a task first.")
            return
        try:
            tasks.mark_done(self.app.data, task_id)
        except ValueError as error:
            self.app.error(str(error))
            return
        self.app.commit()
        messagebox.showinfo("Great job!", "Done! Review reminders were added for 1, 3 and 7 days from now.",
                            parent=self.app)

    def delete_task(self):
        task_id = self.selected_id()
        if task_id is None:
            self.app.error("Select a task first.")
            return
        if not messagebox.askyesno("Delete task", "Delete the selected task?", parent=self.app):
            return
        try:
            tasks.delete_task(self.app.data, task_id)
        except ValueError as error:
            self.app.error(str(error))
            return
        self.app.commit()

    def log_attempt(self):
        task_id = self.selected_id()
        if task_id is None:
            self.app.error("Select a task first.")
            return
        self.app.log_attempt(task_id)

    def open_subjects(self):
        SubjectsDialog(self.app, self.app)
