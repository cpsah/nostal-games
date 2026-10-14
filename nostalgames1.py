"""NOSTALgames - all-in-one single file version.

Combines theme.py, db.py, login.py, admin.py and nostalgames.py.
Run:  python3 nostalgames1.py   (needs db_config.ini next to this file, same as before)
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
import configparser
import hashlib
import mysql.connector


# ======================================================================
# ----- from theme.py -----
# ======================================================================
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


# ======================================================================
# ----- from db.py -----
# ======================================================================
CONFIG_FILE = "db_config.ini"
START_WALLET = 10000.0
DEFAULT_GAMES = {"Cyberpunk 2077": 2999, "Elden Ring": 3500, "Stardew Valley": 479, "Hollow Knight": 600, "Doom Eternal": 1799, "Forza Horizon 5": 3499, "Forza Horizon 6": 4599, "Counter Strike 2": 1399, "Subnautica 2": 1799, "NBA 2K26": 3999, "Red Dead Redemption 2": 4999, "FC™ 26": 1625}

TABLES = [
    """CREATE TABLE IF NOT EXISTS users (
        username VARCHAR(30) PRIMARY KEY,
        password CHAR(64) NOT NULL,
        role ENUM('user', 'admin') NOT NULL DEFAULT 'user',
        wallet DECIMAL(10, 2) NOT NULL DEFAULT 10000)""",
    """CREATE TABLE IF NOT EXISTS games (
        name VARCHAR(60) PRIMARY KEY,
        price INT NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS purchases (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(30) NOT NULL,
        game VARCHAR(60) NOT NULL,
        price INT NOT NULL,
        bought_on DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (username, game),
        FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE)""",
]


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


class Database:
    """Python-MySQL connectivity: connect(), cursor(), execute(), fetchall(), commit()."""

    def __init__(self, config_file=CONFIG_FILE):
        cfg = configparser.ConfigParser()
        if not cfg.read(config_file):
            raise FileNotFoundError(f"{config_file} not found. Copy db_config.example.ini to {config_file} and fill in your MySQL details.")
        m = cfg["mysql"]
        name = m.get("database", "nostalgames")
        if not name.isidentifier():
            raise ValueError(f"Invalid database name: {name}")

        # autocommit: every SELECT sees the latest data (e.g. edits made in MySQL Workbench); run() opens explicit transactions
        self.con = mysql.connector.connect(host=m.get("host", "localhost"), port=m.getint("port", 3306), user=m["user"], password=m.get("password", ""), autocommit=True)
        self.cur = self.con.cursor()
        self.cur.execute(f"CREATE DATABASE IF NOT EXISTS {name} CHARACTER SET utf8mb4")
        self.cur.execute(f"USE {name}")
        for sql in TABLES:
            self.cur.execute(sql)

        self.users, self.games, self.purchases = UserTable(self), GameTable(self), PurchaseTable(self)
        self.games.seed()
        self.users.seed_admin(cfg.get("app", "admin_password", fallback="admin123"))

    def fetchall(self, sql, params=()):
        self.cur.execute(sql, params)
        return self.cur.fetchall()

    def fetchone(self, sql, params=()):
        self.cur.execute(sql, params)
        return self.cur.fetchone()

    def run(self, *statements, guard=None):
        """Execute (sql, params) pairs as one transaction: all succeed or none do.
        If guard (sql, params) is given it runs first; when it changes no rows nothing is saved and False is returned."""
        try:
            self.con.start_transaction()
            if guard:
                self.cur.execute(*guard)
                if self.cur.rowcount == 0:
                    self.con.rollback()
                    return False
            for sql, params in statements:
                self.cur.execute(sql, params)
            self.con.commit()
            return True
        except mysql.connector.Error:
            self.con.rollback()
            raise

    def close(self):
        self.cur.close(); self.con.close()


class UserTable:
    def __init__(self, db):
        self.db = db

    def seed_admin(self, password):
        if not self.db.fetchone("SELECT username FROM users WHERE role = 'admin'"):
            self.db.run(("INSERT INTO users (username, password, role) VALUES (%s, %s, 'admin')", ("admin", hash_password(password))))

    def login(self, username, password):
        """Return the role ('user'/'admin') if the credentials match, else None."""
        row = self.db.fetchone("SELECT role FROM users WHERE username = %s AND password = %s", (username, hash_password(password)))
        return row[0] if row else None

    def register(self, username, password):
        try:
            self.db.run(("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hash_password(password))))
            return True
        except mysql.connector.IntegrityError:
            return False

    def wallet(self, username):
        return float(self.db.fetchone("SELECT wallet FROM users WHERE username = %s", (username,))[0])

    def set_wallet(self, username, amount):
        self.db.run(("UPDATE users SET wallet = %s WHERE username = %s", (amount, username)))

    def reset(self, username):
        self.db.run(("DELETE FROM purchases WHERE username = %s", (username,)),
                    ("UPDATE users SET wallet = %s WHERE username = %s", (START_WALLET, username)))

    def delete(self, username):
        self.db.run(("DELETE FROM users WHERE username = %s AND role = 'user'", (username,)))

    def all(self):
        return self.db.fetchall("""SELECT u.username, u.role, u.wallet, COUNT(p.id)
                                   FROM users u LEFT JOIN purchases p ON p.username = u.username
                                   GROUP BY u.username, u.role, u.wallet ORDER BY u.role, u.username""")


class GameTable:
    def __init__(self, db):
        self.db = db

    def seed(self):
        if not self.db.fetchone("SELECT COUNT(*) FROM games")[0]:
            self.db.run(*[("INSERT INTO games (name, price) VALUES (%s, %s)", (n, p)) for n, p in DEFAULT_GAMES.items()])

    def all(self):
        """Games in the original store order; any extra games added in MySQL come after, A-Z."""
        order = list(DEFAULT_GAMES)
        rows = sorted(self.db.fetchall("SELECT name, price FROM games"), key=lambda r: (order.index(r[0]) if r[0] in order else len(order), r[0]))
        return dict(rows)

    def save(self, name, price):
        self.db.run(("INSERT INTO games (name, price) VALUES (%s, %s) ON DUPLICATE KEY UPDATE price = %s", (name, price, price)))

    def delete(self, name):
        self.db.run(("DELETE FROM games WHERE name = %s", (name,)))


class PurchaseTable:
    def __init__(self, db):
        self.db = db

    def library(self, username):
        return [r[0] for r in self.db.fetchall("SELECT game FROM purchases WHERE username = %s ORDER BY bought_on", (username,))]

    def buy(self, username, items):
        """items: {game: price}. Charges the wallet and records every purchase in one transaction.
        Returns False (nothing saved) if the wallet stored in MySQL can't cover the total."""
        cost = sum(items.values())
        return self.db.run(*[("INSERT INTO purchases (username, game, price) VALUES (%s, %s, %s)", (username, g, p)) for g, p in items.items()],
                           guard=("UPDATE users SET wallet = wallet - %s WHERE username = %s AND wallet >= %s", (cost, username, cost)))

    def all(self):
        return self.db.fetchall("SELECT username, game, price, bought_on FROM purchases ORDER BY bought_on DESC")


# ======================================================================
# ----- from login.py -----
# ======================================================================
class LoginWindow(ThemedWindow):
    """Login / sign-up portal. run() returns (username, role) or None if the window was closed."""

    def __init__(self, db):
        super().__init__("NOSTALgames - Login", "420x380")
        self.db, self.user = db, None
        self.button_style("Login", PRCHS, "white", "#14a01f", 12, 8)

        box = tk.Frame(self, bg=DB, padx=30, pady=30); box.pack(expand=1)
        tk.Label(box, text="NOSTALgames", font=("Arial", 20, "bold"), bg=DB, fg="white").pack(pady=(0, 20))
        self.username = self.field(box, "Username")
        self.password = self.field(box, "Password", show="*")

        ttk.Button(box, text="LOGIN", style="Login.TButton", command=self.login).pack(fill="x", pady=(15, 5))
        ttk.Button(box, text="REGISTER", style="Nav.TButton", command=self.register).pack(fill="x")
        self.bind("<Return>", lambda e: self.login())

    def field(self, parent, label, show=""):
        tk.Label(parent, text=label, bg=DB, fg=TXT, font=("Arial", 10)).pack(anchor="w")
        var = tk.StringVar()
        tk.Entry(parent, textvariable=var, show=show, font=("Arial", 12), width=24, bg=B, fg="white", insertbackground="white").pack(pady=(0, 10))
        return var

    def credentials(self):
        return self.username.get().strip(), self.password.get()

    def login(self):
        username, password = self.credentials()
        role = self.db.users.login(username, password)
        if not role:
            messagebox.showerror("Login failed", "Wrong username or password.")
            return
        self.user = (username, role)
        self.destroy()

    def register(self):
        username, password = self.credentials()
        if not (username.replace("_", "").isalnum() and len(username) <= 30) or len(password) < 4:
            messagebox.showerror("Register", "Username: letters, digits or _ (max 30).\nPassword: at least 4 characters.")
        elif self.db.users.register(username, password):
            messagebox.showinfo("Register", "Account created. You can log in now.")
        else:
            messagebox.showerror("Register", "That username is taken.")

    def run(self):
        self.mainloop()
        return self.user


# ======================================================================
# ----- from admin.py -----
# ======================================================================
class AdminTabs:
    """Adds USERS, GAMES and PURCHASES tabs to an existing notebook (the admin's store window)."""

    def __init__(self, root, notebook, db, on_games_changed):
        self.db, self.on_games_changed = db, on_games_changed
        button_style(root, "Nav", NAV, TXT, "#3a6a8a", 10, (15, 5))
        button_style(root, "Danger", RED, "white", "#c43a3a", 10, (15, 5))
        s = ttk.Style(root)
        s.configure("Treeview", background=DB, fieldbackground=DB, foreground=TXT, rowheight=26, font=("Arial", 10))
        s.configure("Treeview.Heading", background=NAV, foreground="white", font=("Arial", 10, "bold"))

        self.tabs = {n: tk.Frame(notebook, bg=B) for n in ["USERS", "GAMES", "PURCHASES"]}
        for n, f in self.tabs.items(): notebook.add(f, text=f" {n} ")
        notebook.bind("<<NotebookTabChanged>>", lambda e: self.refresh(), add="+")

        self.build_users(); self.build_games(); self.build_purchases()
        self.refresh()

    def table(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show="headings", selectmode="browse")
        for c in columns: tree.heading(c, text=c.upper()); tree.column(c, anchor="w")
        tree.pack(fill="both", expand=1, padx=20, pady=(20, 10))
        return tree

    def toolbar(self, parent):
        bar = tk.Frame(parent, bg=B); bar.pack(fill="x", padx=20, pady=(0, 20))
        return bar

    def selected(self, tree):
        sel = tree.selection()
        return tree.item(sel[0], "values") if sel else None

    @staticmethod
    def fill(tree, rows):
        tree.delete(*tree.get_children())
        for r in rows: tree.insert("", "end", values=r)

    # --- Users ---
    def build_users(self):
        self.users_tree = self.table(self.tabs["USERS"], ("username", "role", "wallet", "games"))
        bar = self.toolbar(self.tabs["USERS"])
        ttk.Button(bar, text="RESET USER", style="Nav.TButton", command=self.reset_user).pack(side="left")
        ttk.Button(bar, text="DELETE USER", style="Danger.TButton", command=self.delete_user).pack(side="right")

    def selected_user(self):
        row = self.selected(self.users_tree)
        if not row or row[1] != "user":
            messagebox.showerror("Users", "Select a non-admin user first.")
            return None
        return row[0]

    def reset_user(self):
        u = self.selected_user()
        if u and messagebox.askyesno("Reset", f"Clear {u}'s library and reset wallet?"):
            self.db.users.reset(u); self.refresh()

    def delete_user(self):
        u = self.selected_user()
        if u and messagebox.askyesno("Delete", f"Delete user {u} and all their purchases?"):
            self.db.users.delete(u); self.refresh()

    # --- Games ---
    def build_games(self):
        self.games_tree = self.table(self.tabs["GAMES"], ("name", "price"))
        self.games_tree.bind("<<TreeviewSelect>>", self.load_game_form)
        bar = self.toolbar(self.tabs["GAMES"])
        self.game_name, self.game_price = tk.StringVar(), tk.StringVar()
        for label, var, width in (("Name", self.game_name, 28), ("Price (₹)", self.game_price, 10)):
            tk.Label(bar, text=label, bg=B, fg="white", font=("Arial", 10)).pack(side="left")
            tk.Entry(bar, textvariable=var, width=width, font=("Arial", 11)).pack(side="left", padx=(5, 15))
        ttk.Button(bar, text="ADD / UPDATE", style="Nav.TButton", command=self.save_game).pack(side="left")
        ttk.Button(bar, text="REMOVE GAME", style="Danger.TButton", command=self.delete_game).pack(side="right")

    def load_game_form(self, _event):
        row = self.selected(self.games_tree)
        if row: self.game_name.set(row[0]); self.game_price.set(row[1])

    def save_game(self):
        name, price = self.game_name.get().strip(), self.game_price.get().strip()
        if not name or len(name) > 60 or not price.isdigit():
            messagebox.showerror("Games", "Enter a name (max 60 chars) and a whole-number price.")
            return
        self.db.games.save(name, int(price)); self.games_changed()

    def delete_game(self):
        row = self.selected(self.games_tree)
        if row and messagebox.askyesno("Remove", f"Remove {row[0]} from the store? Owners keep it in their library."):
            self.db.games.delete(row[0]); self.games_changed()

    def games_changed(self):
        self.refresh(); self.on_games_changed()

    # --- Purchases ---
    def build_purchases(self):
        self.purchases_tree = self.table(self.tabs["PURCHASES"], ("username", "game", "price", "bought_on"))

    def refresh(self):
        self.fill(self.users_tree, self.db.users.all())
        self.fill(self.games_tree, self.db.games.all().items())
        self.fill(self.purchases_tree, self.db.purchases.all())


# ======================================================================
# ----- from nostalgames.py -----
# ======================================================================
from turtle import*
from colorsys import*


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
