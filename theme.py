import tkinter as tk
from tkinter import ttk

# Theme Shorthand
B, DB, NAV, LB, TXT, WALT, PRCHS, RED = "#661B49", "#171a21", "#2a475e", "#11F521", "#c7d5e0", "#ffcc00", "#118A1A", "#a32a2a"


def button_style(root, name, bg, fg, active_bg, size, padding):
    # ttk buttons honour custom colours on macOS; tk.Button ignores bg there and hides the text
    s = ttk.Style(root)
    s.configure(f"{name}.TButton", background=bg, foreground=fg, font=("Arial", size, "bold"), borderwidth=0, padding=padding)
    s.map(f"{name}.TButton", background=[("pressed", active_bg), ("active", active_bg)], foreground=[("pressed", fg), ("active", fg)])


class ThemedWindow(tk.Tk):
    """Themed top-level window (used by the login screen)."""

    def __init__(self, title, size):
        super().__init__()
        self.title(title); self.geometry(size); self.configure(bg=B)
        ttk.Style(self).theme_use('clam')
        self.button_style("Nav", NAV, TXT, "#3a6a8a", 10, (15, 5))

    def button_style(self, name, bg, fg, active_bg, size, padding):
        button_style(self, name, bg, fg, active_bg, size, padding)
