from tkinter import ttk

THEMES = {
    "light": {
        "bg": "#F5F6FA", "card": "#FFFFFF", "fg": "#2C3E50", "muted": "#7F8C8D",
        "accent": "#3498DB", "border": "#DADDE3", "danger": "#C0392B",
    },
    "dark": {
        "bg": "#1E1F26", "card": "#2A2C36", "fg": "#ECEFF4", "muted": "#9AA0AE",
        "accent": "#4C8DFF", "border": "#3A3D4A", "danger": "#FF6B6B",
    },
}

QUADRANT_COLORS = {1: "#E74C3C", 2: "#3498DB", 3: "#F39C12", 4: "#7F8C8D"}


def apply_theme(root, name):
    t = THEMES.get(name, THEMES["light"])
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".", background=t["bg"], foreground=t["fg"], fieldbackground=t["card"],
                    bordercolor=t["border"], lightcolor=t["bg"], darkcolor=t["bg"],
                    troughcolor=t["border"])
    style.configure("TFrame", background=t["bg"])
    style.configure("TLabel", background=t["bg"], foreground=t["fg"])
    style.configure("Muted.TLabel", foreground=t["muted"])
    style.configure("Warn.TLabel", foreground=t["danger"])
    style.configure("Title.TLabel", font=("Helvetica", 16, "bold"))
    style.configure("Big.TLabel", font=("Helvetica", 44, "bold"))
    style.configure("TButton", background=t["card"], foreground=t["fg"], padding=6)
    style.map("TButton", background=[("active", t["accent"])], foreground=[("active", "white")])
    style.configure("TNotebook", background=t["bg"], borderwidth=0)
    style.configure("TNotebook.Tab", background=t["card"], foreground=t["fg"], padding=(12, 6))
    style.map("TNotebook.Tab", background=[("selected", t["accent"])], foreground=[("selected", "white")])
    style.configure("TCheckbutton", background=t["bg"], foreground=t["fg"])
    style.configure("TCombobox", fieldbackground=t["card"], background=t["card"],
                    foreground=t["fg"], arrowcolor=t["fg"])
    style.map("TCombobox",
              fieldbackground=[("readonly", t["card"])],
              foreground=[("readonly", t["fg"])],
              selectbackground=[("readonly", t["card"])],
              selectforeground=[("readonly", t["fg"])])
    style.configure("TEntry", fieldbackground=t["card"], foreground=t["fg"])
    style.configure("TSpinbox", fieldbackground=t["card"], foreground=t["fg"], arrowcolor=t["fg"])
    style.configure("Horizontal.TProgressbar", background=t["accent"], troughcolor=t["border"])

    root.configure(bg=t["bg"])
    root.option_add("*TCombobox*Listbox.background", t["card"])
    root.option_add("*TCombobox*Listbox.foreground", t["fg"])
    root.option_add("*TCombobox*Listbox.selectBackground", t["accent"])
    restyle(root, t)
    return t


def restyle(widget, t):
    for child in widget.winfo_children():
        kind = child.winfo_class()
        if getattr(child, "keep_color", False):
            pass
        elif kind in ("Listbox", "Text"):
            child.configure(bg=t["card"], fg=t["fg"], selectbackground=t["accent"],
                            selectforeground="white", highlightthickness=1,
                            highlightbackground=t["border"], relief="flat")
        elif kind in ("Frame", "Toplevel"):
            child.configure(bg=t["bg"])
        restyle(child, t)
