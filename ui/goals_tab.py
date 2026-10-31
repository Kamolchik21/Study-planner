import tkinter as tk
from tkinter import messagebox, ttk

from planner import goals

from .common import fill_listbox
from .dialogs import ask_form


class GoalsTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=14)
        self.app = app
        self.lists = {}
        self.ids = {"short": [], "long": []}

        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=(0, 10))
        for text, command in [("Add goal", self.add_goal), ("Mark completed", self.complete), ("Delete", self.delete)]:
            ttk.Button(bar, text=text, command=command).pack(side="left", padx=(0, 6))

        columns = ttk.Frame(self)
        columns.pack(fill="both", expand=True)
        columns.columnconfigure((0, 1), weight=1, uniform="goals")
        columns.rowconfigure(0, weight=1)
        for column, (kind, label) in enumerate([("short", "Short-term goals"), ("long", "Long-term goals")]):
            box = ttk.Frame(columns)
            box.grid(row=0, column=column, sticky="nsew", padx=4)
            ttk.Label(box, text=label, style="Title.TLabel").pack(anchor="w", pady=(0, 4))
            listbox = tk.Listbox(box, exportselection=False, activestyle="none")
            listbox.pack(fill="both", expand=True)
            listbox.bind("<<ListboxSelect>>", lambda event, k=kind: self.on_select(k))
            self.lists[kind] = listbox

    def on_select(self, kind):
        for k, listbox in self.lists.items():
            if k != kind:
                listbox.selection_clear(0, "end")

    def selected_id(self):
        for kind, listbox in self.lists.items():
            selection = listbox.curselection()
            if selection and selection[0] < len(self.ids[kind]):
                return self.ids[kind][selection[0]]
        return None

    def refresh(self):
        for kind, listbox in self.lists.items():
            items = goals.goals_by_type(self.app.data, kind)
            self.ids[kind] = [g["id"] for g in items]
            lines = []
            for g in items:
                mark = "[x]" if g["done"] else "[ ]"
                when = f"  - by {g['deadline']}" if g["deadline"] else ""
                lines.append(f"{mark} {g['title']}{when}")
            fill_listbox(listbox, lines)

    def add_goal(self):
        fields = [
            ("title", "Goal", "text", None, ""),
            ("kind", "Type", "combo", ["short", "long"], "short"),
            ("deadline", "Target date (optional)", "text", None, ""),
        ]
        result = ask_form(self, "Add goal", fields)
        if not result:
            return
        try:
            goals.add_goal(self.app.data, result["title"], result["kind"], result["deadline"])
        except ValueError as error:
            self.app.error(str(error))
            return
        self.app.commit()

    def complete(self):
        goal_id = self.selected_id()
        if goal_id is None:
            self.app.error("Select a goal first.")
            return
        goals.complete_goal(self.app.data, goal_id)
        self.app.commit()

    def delete(self):
        goal_id = self.selected_id()
        if goal_id is None:
            self.app.error("Select a goal first.")
            return
        if messagebox.askyesno("Delete goal", "Delete the selected goal?", parent=self.app):
            goals.delete_goal(self.app.data, goal_id)
            self.app.commit()
