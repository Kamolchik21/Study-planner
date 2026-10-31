import tkinter as tk
from tkinter import messagebox, ttk

from planner import pomodoro, stats, tasks
from planner.pomodoro import PomodoroTimer


class PomodoroTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=14)
        self.app = app
        settings = app.data["settings"]
        self.timer = PomodoroTimer(settings["pomodoro_work"], settings["pomodoro_break"])
        self.label_to_id = {"No specific task": None}

        ttk.Label(self, text="Pomodoro timer", style="Title.TLabel").pack(anchor="w")
        ttk.Label(self, style="Muted.TLabel",
                  text="Work in focused blocks, then rest. Finished work blocks are saved to your progress."
                  ).pack(anchor="w", pady=(2, 10))

        row = ttk.Frame(self)
        row.pack(anchor="w")
        ttk.Label(row, text="Working on:").pack(side="left", padx=(0, 8))
        self.task_choice = tk.StringVar(value="No specific task")
        self.task_combo = ttk.Combobox(row, textvariable=self.task_choice, state="readonly", width=50)
        self.task_combo.pack(side="left")

        self.mode_label = ttk.Label(self, text="WORK", style="Title.TLabel")
        self.mode_label.pack(pady=(26, 0))
        self.time_label = ttk.Label(self, text=self.timer.display(), style="Big.TLabel")
        self.time_label.pack()

        controls = ttk.Frame(self)
        controls.pack(pady=12)
        ttk.Button(controls, text="Start", command=self.start).pack(side="left", padx=4)
        ttk.Button(controls, text="Pause", command=self.pause).pack(side="left", padx=4)
        ttk.Button(controls, text="Reset", command=self.reset).pack(side="left", padx=4)

        durations = ttk.Frame(self)
        durations.pack(pady=(4, 0))
        self.work_var = tk.StringVar(value=str(settings["pomodoro_work"]))
        self.break_var = tk.StringVar(value=str(settings["pomodoro_break"]))
        ttk.Label(durations, text="Work (min):").pack(side="left")
        work_spin = ttk.Spinbox(durations, from_=1, to=120, width=5, textvariable=self.work_var,
                                command=self.change_durations)
        work_spin.pack(side="left", padx=(4, 14))
        ttk.Label(durations, text="Break (min):").pack(side="left")
        break_spin = ttk.Spinbox(durations, from_=1, to=60, width=5, textvariable=self.break_var,
                                 command=self.change_durations)
        break_spin.pack(side="left", padx=4)
        for spin in (work_spin, break_spin):
            spin.bind("<Return>", lambda event: self.change_durations())
            spin.bind("<FocusOut>", lambda event: self.change_durations())

        self.today_label = ttk.Label(self, style="Muted.TLabel")
        self.today_label.pack(pady=(20, 0))

        self.after(1000, self.tick)

    def refresh(self):
        self.label_to_id = {"No specific task": None}
        for task in tasks.pending_tasks(self.app.data):
            self.label_to_id[f"#{task['id']} {task['title']} [{task['subject']}]"] = task["id"]
        self.task_combo.configure(values=list(self.label_to_id.keys()))
        if self.task_choice.get() not in self.label_to_id:
            self.task_choice.set("No specific task")
        self.today_label.configure(text=f"Focused time today: {stats.minutes_today(self.app.data)} min")
        self.update_display()

    def update_display(self):
        self.time_label.configure(text=self.timer.display())
        self.mode_label.configure(text="WORK" if self.timer.mode == "work" else "BREAK")

    def change_durations(self):
        try:
            work = int(self.work_var.get())
            rest = int(self.break_var.get())
        except ValueError:
            return
        if not (1 <= work <= 120 and 1 <= rest <= 60):
            return
        settings = self.app.data["settings"]
        if (work, rest) == (settings["pomodoro_work"], settings["pomodoro_break"]):
            return
        settings["pomodoro_work"] = work
        settings["pomodoro_break"] = rest
        self.timer.set_durations(work, rest)
        self.app.save()
        self.update_display()

    def start(self):
        self.timer.start()

    def pause(self):
        self.timer.pause()

    def reset(self):
        self.timer.reset()
        self.update_display()

    def tick(self):
        finished = self.timer.tick()
        self.update_display()
        if finished == "work":
            task_id = self.label_to_id.get(self.task_choice.get())
            pomodoro.log_session(self.app.data, task_id, self.timer.work_min)
            self.app.commit()
            self.bell()
            messagebox.showinfo("Pomodoro", f"Work block finished ({self.timer.work_min} min). Take a break!",
                                parent=self.app)
        elif finished == "break":
            self.bell()
            messagebox.showinfo("Pomodoro", "Break is over. Ready for the next block?", parent=self.app)
        self.after(1000, self.tick)
