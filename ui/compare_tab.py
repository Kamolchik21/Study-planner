import tkinter as tk
from tkinter import ttk

from planner import attempts

from .common import set_text
from .theme import THEMES

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    HAS_CHART = True
except Exception:
    HAS_CHART = False


class CompareTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=14)
        self.app = app
        self.label_to_id = {}
        self.selected_id = None

        ttk.Label(self, text="Repeat the same task and compare your results over time",
                  style="Title.TLabel").pack(anchor="w")

        row = ttk.Frame(self)
        row.pack(fill="x", pady=(10, 8))
        self.choice = tk.StringVar()
        self.combo = ttk.Combobox(row, textvariable=self.choice, state="readonly", width=60)
        self.combo.pack(side="left", fill="x", expand=True)
        self.combo.bind("<<ComboboxSelected>>", lambda event: self.on_choose())
        ttk.Button(row, text="Log attempt", command=self.log_attempt).pack(side="left", padx=(8, 0))

        self.summary = tk.Text(self, height=9, wrap="word", state="disabled")
        self.summary.pack(fill="x")

        if HAS_CHART:
            self.figure = Figure(figsize=(6, 2.6), dpi=100)
            self.axes = self.figure.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.figure, master=self)
            self.canvas.get_tk_widget().pack(fill="both", expand=True, pady=(8, 0))
        else:
            ttk.Label(self, style="Muted.TLabel",
                      text="Install matplotlib (pip install matplotlib) to see the progress chart.").pack(anchor="w", pady=8)

    def current_task(self):
        for task in self.app.data["tasks"]:
            if task["id"] == self.selected_id:
                return task
        return None

    def on_choose(self):
        self.selected_id = self.label_to_id.get(self.choice.get())
        self.show()

    def log_attempt(self):
        if self.selected_id is None:
            self.app.error("Choose a task first.")
            return
        self.app.log_attempt(self.selected_id)

    def refresh(self):
        self.label_to_id = {}
        for task in self.app.data["tasks"]:
            count = len(task["attempts"])
            label = f"#{task['id']} {task['title']} [{task['subject']}] - {count} attempt(s)"
            self.label_to_id[label] = task["id"]
        self.combo.configure(values=list(self.label_to_id.keys()))
        current = self.current_task()
        if current is None:
            self.selected_id = None
            self.choice.set("")
        else:
            for label, task_id in self.label_to_id.items():
                if task_id == self.selected_id:
                    self.choice.set(label)
        self.show()

    def show(self):
        task = self.current_task()
        if task is None:
            set_text(self.summary, "Choose a task above, then log an attempt with your score (0-100) and a short note "
                                   "about how you answered. Do the same task again later and log it again to see "
                                   "how much you improved.")
            self.draw_chart(None)
            return
        result = attempts.compare_attempts(task)
        if result is None:
            count = len(task["attempts"])
            set_text(self.summary, f"{count} attempt(s) logged. Log at least 2 attempts to compare them.")
        else:
            first, last = result["first"], result["last"]
            sign = "+" if result["change"] > 0 else ""
            verdict = {"improved": "You improved!", "declined": "Your score dropped. Review the weak spots.",
                       "same": "No change yet."}[result["trend"]]
            lines = [
                f"First attempt ({first['date']}): {first['score']:g}%",
                f"Latest attempt ({last['date']}): {last['score']:g}%",
                f"Change: {sign}{result['change']:g} points over {result['days']} day(s)  -  {verdict}",
                f"Attempts: {result['count']}   Best: {result['best']:g}%   Average: {result['average']:g}%",
                "",
                f"Then: {first['note'] or '(no note)'}",
                f"Now:  {last['note'] or '(no note)'}",
            ]
            set_text(self.summary, "\n".join(lines))
        self.draw_chart(task)

    def draw_chart(self, task):
        if not HAS_CHART:
            return
        theme = THEMES[self.app.data["settings"]["theme"]]
        self.figure.set_facecolor(theme["bg"])
        self.axes.clear()
        self.axes.set_facecolor(theme["card"])
        for spine in self.axes.spines.values():
            spine.set_color(theme["border"])
        self.axes.tick_params(colors=theme["fg"], labelsize=8)
        if task is not None and task["attempts"]:
            dates = [a["date"] for a in task["attempts"]]
            scores = [a["score"] for a in task["attempts"]]
            self.axes.plot(range(len(scores)), scores, marker="o", color=theme["accent"])
            self.axes.set_xticks(range(len(dates)))
            self.axes.set_xticklabels(dates, rotation=20, ha="right")
            self.axes.set_ylim(0, 100)
            self.axes.set_ylabel("Score %", color=theme["fg"])
            self.axes.grid(True, color=theme["border"], alpha=0.6)
        self.figure.tight_layout()
        self.canvas.draw_idle()
