import tkinter as tk
from tkinter import ttk, messagebox
import os
from turtle import*
from colorsys import*
import mysql.connector

from theme import button_style
from db import Database
from login import LoginWindow
from admin import AdminTabs

# Theme Shorthand
B, DB, NAV, LB, TXT, WALT, PRCHS, RED = "#661B49", "#171a21", "#2a475e", "#11F521", "#c7d5e0", "#ffcc00", "#118A1A", "#a32a2a"

def load_screen():
    setup(800, 600)  # window centred on the screen
    getcanvas().update()
    # make the drawing area the same size as the window so (0,0) sits in the middle, not the top-left
    screensize(getcanvas().winfo_width(), getcanvas().winfo_height())
    title("NOSTALgames loading.....")
    bgcolor("black")
    speed(0)
    h=0
    for i in range(50):
        h+=0.0015
        color("red")
        goto(0,0)
        fd(i)
        circle(100,50)
        rt(10)
        hideturtle()
    bye()

class DragToCart:
    """Drag a game row and drop it on the cart area to add it to the cart."""

    def __init__(self, root, drop_zone, on_drop):
        self.root, self.zone, self.on_drop = root, drop_zone, on_drop
        self.zone_bg = drop_zone.cget("bg")
        self.game = self.ghost = None

    def attach(self, game, *widgets):
        for w in widgets:
            w.configure(cursor="hand2")
            w.bind("<ButtonPress-1>", lambda e, g=game: self.start(g))
            w.bind("<B1-Motion>", self.move)
            w.bind("<ButtonRelease-1>", self.drop)

    def start(self, game):
        self.game = game

    def move(self, e):
        if not self.game: return
        if not self.ghost:
            self.ghost = tk.Label(self.root, text=f"🎮 {self.game}", bg=WALT, fg="black", font=("Arial", 11, "bold"), padx=8, pady=4)
        self.ghost.place(x=e.x_root - self.root.winfo_rootx() + 12, y=e.y_root - self.root.winfo_rooty() + 12)
        self.ghost.lift()
        self.zone.configure(bg=NAV if self.over_zone(e) else self.zone_bg)

    def over_zone(self, e):
        x, y = e.x_root - self.zone.winfo_rootx(), e.y_root - self.zone.winfo_rooty()
        return 0 <= x < self.zone.winfo_width() and 0 <= y < self.zone.winfo_height()

    def drop(self, e):
        if self.game and self.ghost and self.over_zone(e): self.on_drop(self.game)
        if self.ghost: self.ghost.destroy()
        self.zone.configure(bg=self.zone_bg)
        self.game = self.ghost = None

class NG(tk.Tk):
    load_screen()
    def __init__(self, db, username):
        super().__init__()
        self.title("NOSTALgames"); self.geometry("1000x700"); self.configure(bg=B)
        self.db, self.username, self.cart, self.games = db, username, [], db.games.all()
        self.load_data()

        # Styles
        s = ttk.Style(self); s.theme_use('clam')
        s.configure("TNotebook", background=DB, borderwidth=0)
        s.configure("TNotebook.Tab", background=NAV, foreground=TXT, padding=[20, 10], font=("Arial", 11, "bold"))
        s.map("TNotebook.Tab", background=[("selected", B)], foreground=[("selected", "white")])
        button_style(self, "Remove", "#2a2a2a", TXT, RED, 9, 5)
        button_style(self, "Buy", PRCHS, "white", "#14a01f", 12, 10)
        button_style(self, "Reset", RED, "white", "#c43a3a", 10, (20, 5))
        button_style(self, "Price", NAV, LB, "#3a6a8a", 10, 5)

        # Header
        h = tk.Frame(self, bg=DB, height=60); h.pack(fill="x"); h.pack_propagate(0)
        tk.Label(h, text="  NOSTALgames", font=("Arial", 18, "bold"), bg=DB, fg="white").pack(side="left")
        self.w_lbl = tk.Label(h, text="", font=("Arial", 11, "bold"), bg=DB, fg=WALT); self.w_lbl.pack(side="right")

        self.nb = ttk.Notebook(self); self.nb.pack(fill="both", expand=1)
        self.tabs = {n: ttk.Frame(self.nb) for n in ["STORE", "LIBRARY", "SETTINGS"]}
        for n, f in self.tabs.items(): self.nb.add(f, text=f" {n} ")

        # Store UI
        sc = tk.Frame(self.tabs["STORE"], bg=B); sc.pack(side="left", fill="both", expand=1, padx=20, pady=20)
        self.canv = tk.Canvas(sc, bg=B, highlightthickness=0, yscrollincrement=1)
        sb = ttk.Scrollbar(sc, orient="vertical", command=self.canv.yview); sb.pack(side="right", fill="y")
        self.canv.configure(yscrollcommand=sb.set); self.canv.pack(side="left", fill="both", expand=1)
        self.bind_scroll()
        self.list_f = tk.Frame(self.canv, bg=B); self.canv.create_window((0,0), window=self.list_f, anchor="nw", width=600)
        self.list_f.bind("<Configure>", lambda e: self.canv.configure(scrollregion=self.canv.bbox("all")))

        cf = tk.Frame(self.tabs["STORE"], bg=DB, width=300, padx=20, pady=20); cf.pack(side="right", fill="y"); cf.pack_propagate(0)
        tk.Label(cf, text="SHOPPING CART", bg=DB, fg=TXT, font=("Arial", 12, "bold")).pack(pady=(10, 0))
        tk.Label(cf, text="drag games here", bg=DB, fg=TXT, font=("Arial", 9)).pack(pady=(0, 10))
        self.drag = DragToCart(self, cf, self.add)
        self.lbx = tk.Listbox(cf, bg=B, fg=TXT, bd=0, font=("Arial", 10), selectbackground=WALT, selectforeground="black", activestyle="none", highlightthickness=0, exportselection=False); self.lbx.pack(fill="both", expand=1)

        ttk.Button(cf, text="REMOVE SELECTED", style="Remove.TButton", command=self.rem).pack(fill="x", pady=5)
        ttk.Button(cf, text="PURCHASE", style="Buy.TButton", command=self.pay).pack(fill="x")

        # Settings UI
        dz = tk.LabelFrame(self.tabs["SETTINGS"], text=" Danger Zone ", bg=B, fg=RED, font=("Arial", 10, "bold"), padx=20, pady=20); dz.pack(fill="x", padx=50, pady=50)
        ttk.Button(dz, text="RESET DATA", style="Reset.TButton", command=self.reset).pack(side="right")

        self.refresh()

    def bind_scroll(self):
        # mouse wheel (macOS/Windows), mouse wheel (Linux), and trackpad (Tk 9 sends <TouchpadScroll>)
        self.bind_all("<MouseWheel>", lambda e: self.scroll_store(e, -40 if e.delta > 0 else 40))
        self.bind_all("<Button-4>", lambda e: self.scroll_store(e, -40))
        self.bind_all("<Button-5>", lambda e: self.scroll_store(e, 40))
        try: self.bind_all("<TouchpadScroll>", lambda e: self.scroll_store(e, -int(self.tk.splitlist(self.tk.call("tk::PreciseScrollDeltas", e.delta))[1])))
        except tk.TclError: pass  # Tk 8.6 has no <TouchpadScroll>; trackpads send <MouseWheel> there

    def scroll_store(self, e, pixels):
        # only scroll when the pointer is over the store list
        w = self.winfo_containing(e.x_root, e.y_root)
        if w and str(w).startswith(str(self.canv)): self.canv.yview_scroll(pixels, "units")

    def load_data(self):
        self.wallet = self.db.users.wallet(self.username)
        self.library = self.db.purchases.library(self.username)

    def save_data(self):
        self.db.users.set_wallet(self.username, self.wallet)

    def refresh(self):
        self.w_lbl.config(text=f"WALLET: ₹{self.wallet}  ")
        for f in [self.list_f, self.tabs["LIBRARY"]]:
            for w in f.winfo_children(): w.destroy()

        for g, p in self.games.items():
            row = tk.Frame(self.list_f, bg=DB, pady=15, padx=20); row.pack(fill="x", pady=5)
            name = tk.Label(row, text=g, bg=DB, fg="white", font=("Arial", 13, "bold")); name.pack(side="left")
            if g in self.library: tk.Label(row, text="IN LIBRARY", bg=NAV, fg=TXT, font=("Arial", 9), padx=10).pack(side="right")
            else: ttk.Button(row, text=f"₹{p}", style="Price.TButton", width=12, command=lambda x=g: self.add(x)).pack(side="right"); self.drag.attach(g, row, name)

        for g in self.library:
            r = tk.Frame(self.tabs["LIBRARY"], bg=DB, pady=10, padx=20); r.pack(fill="x", pady=2, padx=40)
            tk.Label(r, text=f"🎮 {g}", bg=DB, fg="white", font=("Arial", 12, "bold")).pack(side="left")

    def add(self, g):
        if g not in self.cart: self.cart.append(g); self.lbx.insert("end", f" {g}")

    def rem(self):
        s = self.lbx.curselection()
        if s: self.cart.pop(s[0]); self.lbx.delete(s[0])

    def pay(self):
        if self.cart and self.db.purchases.buy(self.username, {g: self.games[g] for g in self.cart}):
            self.load_data(); self.cart = []; self.lbx.delete(0, "end"); self.refresh(); messagebox.showinfo("OK", "Purchased!")
        elif self.cart: self.load_data(); self.refresh(); messagebox.showerror("Error", "Check funds or cart.")

    def reset(self):
        if messagebox.askyesno("Reset", "Wipe all data?"):
            self.db.users.reset(self.username)
            self.load_data(); self.cart = []; self.lbx.delete(0, "end"); self.refresh()

def reset(self):
        if messagebox.askyesno("Reset", "Wipe all data?"):
            self.db.users.reset(self.username)
            self.load_data(); self.cart = []; self.lbx.delete(0, "end"); self.refresh()

# --- PASTE EVERYTHING BELOW THIS LINE AT THE BOTTOM OF YOUR FILE ---

class NGext(NG):
    def __init__(self, db, username):
        super().__init__(db, username)
        self.add_wallet_controls()

    def add_wallet_controls(self):
        # Create a new frame in the Settings tab
        wm_frame = tk.LabelFrame(self.tabs["SETTINGS"], text=" Wallet Management ", bg="#1b2838", fg="#66c0f4", font=("Arial", 10, "bold"), padx=20, pady=20)
        # Pack it above the Danger Zone by placing it at the top
        wm_frame.pack(fill="x", padx=50, pady=(20, 0), before=self.tabs["SETTINGS"].winfo_children()[0])

        # Input variable for the amount
        self.amount_var = tk.DoubleVar(value=1000.0)

        # UI Elements
        tk.Label(wm_frame, text="Amount (₹):", bg="#1b2838", fg="white", font=("Arial", 10)).pack(side="left")
        tk.Entry(wm_frame, textvariable=self.amount_var, font=("Arial", 11), width=10).pack(side="left", padx=10)

        button_style(self, "Add", "#4c6b22", "white", "#5e8429", 9, (10, 5))
        button_style(self, "Reduce", "#a32a2a", "white", "#c43a3a", 9, (10, 5))
        ttk.Button(wm_frame, text="ADD", style="Add.TButton", command=self.add_money).pack(side="left", padx=5)
        ttk.Button(wm_frame, text="REDUCE", style="Reduce.TButton", command=self.reduce_money).pack(side="left", padx=5)

    def add_money(self):
        try:
            addamount=abs(self.amount_var.get())
            if addamount>50000.0:
                messagebox.showerror("Limit Exceeded!"," You can only add upto ₹50000 at a time.")
                return

            self.wallet += addamount
            self.save_data()
            self.refresh()
        except tk.TclError:
            messagebox.showerror("Error", "Please enter a valid number.")

    def reduce_money(self):
        try:
            # Prevent wallet from going into negative numbers
            self.wallet = max(0.0, self.wallet - abs(self.amount_var.get()))
            self.save_data()
            self.refresh()
        except tk.TclError:
            messagebox.showerror("Error", "Please enter a valid number.")


class NGadmin(NGext):
    """Admin gets the full store plus USERS, GAMES and PURCHASES tabs."""

    def __init__(self, db, username):
        super().__init__(db, username)
        self.admin = AdminTabs(self, self.nb, db, on_games_changed=self.reload_games)

    def reload_games(self):
        self.games = self.db.games.all()
        for i in reversed(range(len(self.cart))):
            if self.cart[i] not in self.games: self.cart.pop(i); self.lbx.delete(i)
        self.refresh()


def open_database():
    try:
        return Database()
    except (FileNotFoundError, ValueError, KeyError, mysql.connector.Error) as e:
        root = tk.Tk(); root.withdraw()
        messagebox.showerror("Database error", f"Could not connect to MySQL:\n{e}")
        root.destroy()
        return None


if __name__ == "__main__":
    db = open_database()
    user = LoginWindow(db).run() if db else None
    if user:
        username, role = user
        (NGadmin if role == "admin" else NGext)(db, username).mainloop()
    if db: db.close()
