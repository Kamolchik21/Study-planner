import tkinter as tk
from tkinter import ttk

from planner import subjects


class FormDialog(tk.Toplevel):
    def __init__(self, parent, title, fields):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=ttk.Style().lookup("TFrame", "background"))
        self.transient(parent)
        self.result = None
        self.vars = {}

        body = ttk.Frame(self, padding=14)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)

        first_widget = None
        for row, (key, label, kind, options, default) in enumerate(fields):
            ttk.Label(body, text=label).grid(row=row, column=0, sticky="w", pady=5, padx=(0, 10))
            if kind == "combo":
                var = tk.StringVar(value=default)
                widget = ttk.Combobox(body, textvariable=var, values=options or [], state="readonly", width=28)
            elif kind == "check":
                var = tk.BooleanVar(value=bool(default))
                widget = ttk.Checkbutton(body, variable=var)
            else:
                var = tk.StringVar(value=str(default))
                widget = ttk.Entry(body, textvariable=var, width=32)
            widget.grid(row=row, column=1, sticky="ew", pady=5)
            self.vars[key] = var
            if first_widget is None:
                first_widget = widget

        buttons = ttk.Frame(body)
        buttons.grid(row=len(fields), column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="right", padx=(6, 0))
        ttk.Button(buttons, text="OK", command=self._ok).pack(side="right")

        self.bind("<Return>", lambda event: self._ok())
        self.bind("<Escape>", lambda event: self.destroy())
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + 80
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        self.grab_set()
        if first_widget is not None:
            first_widget.focus_set()
        self.wait_window()

    def _ok(self):
        self.result = {key: var.get() for key, var in self.vars.items()}
        self.destroy()


def ask_form(parent, title, fields):
    return FormDialog(parent, title, fields).result


class SubjectsDialog(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.title("Subjects")
        self.configure(bg=ttk.Style().lookup("TFrame", "background"))
        self.transient(parent)

        body = ttk.Frame(self, padding=14)
        body.pack(fill="both", expand=True)
        self.listbox = tk.Listbox(body, height=10, exportselection=False)
        self.listbox.pack(fill="both", expand=True)

        row = ttk.Frame(body)
        row.pack(fill="x", pady=(10, 0))
        self.name_var = tk.StringVar()
        entry = ttk.Entry(row, textvariable=self.name_var)
        entry.pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Add", command=self.add).pack(side="left", padx=(6, 0))

        bottom = ttk.Frame(body)
        bottom.pack(fill="x", pady=(10, 0))
        ttk.Button(bottom, text="Remove selected", command=self.remove).pack(side="left")
        ttk.Button(bottom, text="Close", command=self.destroy).pack(side="right")

        entry.bind("<Return>", lambda event: self.add())
        self.refresh()
        app.restyle_window(self)
        self.grab_set()
        entry.focus_set()

    def refresh(self):
        self.listbox.delete(0, "end")
        for name in self.app.data["subjects"]:
            self.listbox.insert("end", name)

    def add(self):
        try:
            subjects.add_subject(self.app.data, self.name_var.get())
        except ValueError as error:
            self.app.error(str(error), parent=self)
            return
        self.name_var.set("")
        self.app.commit()
        self.refresh()

    def remove(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        name = self.app.data["subjects"][selection[0]]
        try:
            subjects.remove_subject(self.app.data, name)
        except ValueError as error:
            self.app.error(str(error), parent=self)
            return
        self.app.commit()
        self.refresh()
