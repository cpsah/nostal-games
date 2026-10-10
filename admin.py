import tkinter as tk
from tkinter import ttk, messagebox

from theme import button_style, B, DB, NAV, TXT, RED


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
