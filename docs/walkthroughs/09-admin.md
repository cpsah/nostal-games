# 9. Admin Panel

**An admin gets the normal store window plus three extra tabs: USERS, GAMES and PURCHASES. `NGadmin` inherits the whole store and plugs in an `AdminTabs` object that builds the tabs and talks to MySQL.**

## How it works, step by step

**1. Pick the window by role:** [nostalgames.py:256](../../nostalgames.py#L256)
```python
(NGadmin if role == "admin" else NGext)(db, username).mainloop()
```

**2. Store plus admin tabs:** [nostalgames.py:227-232](../../nostalgames.py#L227-L232)
```python
class NGadmin(NGext):
    def __init__(self, db, username):
        super().__init__(db, username)        # full store, library, settings, wallet
        self.admin = AdminTabs(self, self.nb, db, on_games_changed=self.reload_games)
```
`AdminTabs` is given the store's notebook (`self.nb`) to add tabs to, and a function to call when the game list changes.

**3. Build the tabs:** [admin.py:10-23](../../admin.py#L10-L23)
```python
self.tabs = {n: tk.Frame(notebook, bg=B) for n in ["USERS", "GAMES", "PURCHASES"]}
for n, f in self.tabs.items(): notebook.add(f, text=f" {n} ")
notebook.bind("<<NotebookTabChanged>>", lambda e: self.refresh(), add="+")
self.build_users(); self.build_games(); self.build_purchases()
self.refresh()
```
- Each tab is a table (`ttk.Treeview`) made by `table()` [admin.py:25-29](../../admin.py#L25-L29), with a row of buttons made by `toolbar()`.
- Switching tabs re-reads everything from MySQL, so a purchase made in the STORE shows up in PURCHASES.

**4. Fill the tables:** [admin.py:103-106](../../admin.py#L103-L106)
```python
self.fill(self.users_tree, self.db.users.all())
self.fill(self.games_tree, self.db.games.all().items())
self.fill(self.purchases_tree, self.db.purchases.all())
```
The USERS query [db.py:120-123](../../db.py#L120-L123) counts each user's games with `LEFT JOIN purchases ... GROUP BY`, so users with no games show 0.

**5. USERS: reset or delete:** [admin.py:51-66](../../admin.py#L51-L66)
```python
def selected_user(self):
    row = self.selected(self.users_tree)
    if not row or row[1] != "user":
        messagebox.showerror("Users", "Select a non-admin user first.")
        return None
    return row[0]

def delete_user(self):
    u = self.selected_user()
    if u and messagebox.askyesno("Delete", f"Delete user {u} and all their purchases?"):
        self.db.users.delete(u); self.refresh()
```
- `delete` runs `DELETE FROM users WHERE username = %s AND role = 'user'` [db.py:117-118](../../db.py#L117-L118); their purchases go too via `ON DELETE CASCADE`.
- Admins are protected twice: by the check above, and by `AND role = 'user'` in the SQL.

**6. GAMES: add, update, remove:** [admin.py:80-97](../../admin.py#L80-L97)
```python
def load_game_form(self, _event):                      # clicking a row fills the boxes
    row = self.selected(self.games_tree)
    if row: self.game_name.set(row[0]); self.game_price.set(row[1])

def save_game(self):
    name, price = self.game_name.get().strip(), self.game_price.get().strip()
    if not name or len(name) > 60 or not price.isdigit(): ...error...; return
    self.db.games.save(name, int(price)); self.games_changed()

def games_changed(self):
    self.refresh(); self.on_games_changed()            # admin tables, then the store
```
`games.save` [db.py:140-141](../../db.py#L140-L141) is one statement that adds or updates:
```sql
INSERT INTO games (name, price) VALUES (%s, %s) ON DUPLICATE KEY UPDATE price = %s
```

**7. Update the store straight away:** [nostalgames.py:234-238](../../nostalgames.py#L234-L238)
```python
def reload_games(self):
    self.games = self.db.games.all()
    for i in reversed(range(len(self.cart))):
        if self.cart[i] not in self.games: self.cart.pop(i); self.lbx.delete(i)
    self.refresh()
```
The cart is walked backwards so removing one item doesn't shift the positions of items not yet checked.

**Example:** add "Hades" for ₹999, change it to ₹1099, then remove it:
```sql
INSERT INTO games (name, price) VALUES ('Hades', 999)  ON DUPLICATE KEY UPDATE price = 999;    -- new row
INSERT INTO games (name, price) VALUES ('Hades', 1099) ON DUPLICATE KEY UPDATE price = 1099;   -- price updated
DELETE FROM games WHERE name = 'Hades';
```
After each step the STORE tab redraws: Hades appears after the 12 originals, its price changes, then it disappears (and leaves the cart if it was there). Anyone who bought it keeps it in their LIBRARY.

## What changed

| Where | Original code | Now |
|---|---|---|
| Admin role | none | `NGadmin` [nostalgames.py:227](../../nostalgames.py#L227) |
| Admin tabs | none | `AdminTabs` [admin.py:7](../../admin.py#L7): USERS, GAMES, PURCHASES |
| Game list | fixed in code | editable in the GAMES tab, stored in MySQL |
| Store update | n/a | `reload_games()` redraws the admin's store immediately |

**Why:** the login portal needed an admin role that can manage users and games and see all purchases, while still using the store like a normal player.

More detail: [features/admin-panel.md](../features/admin-panel.md).
