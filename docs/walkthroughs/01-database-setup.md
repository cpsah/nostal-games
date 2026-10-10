# 1. Database Setup

**When the app starts, it connects to MySQL with the details in `db_config.ini`, creates the `nostalgames` database and its tables if they don't exist, adds the 12 games and an `admin` account the first time, and then hands one shared `Database` object to every screen.**

## How it works, step by step

**1. The app asks for a database:** [nostalgames.py:241-248](../../nostalgames.py#L241-L248)
```python
def open_database():
    try:
        return Database()
    except (FileNotFoundError, ValueError, KeyError, mysql.connector.Error) as e:
        root = tk.Tk(); root.withdraw()
        messagebox.showerror("Database error", f"Could not connect to MySQL:\n{e}")
        root.destroy()
        return None
```
- Any problem (missing config file, wrong password, MySQL not running) becomes a popup instead of a crash.
- `root.withdraw()` creates an invisible window, because a `messagebox` needs a Tk window to belong to.

**2. Read the config file:** [db.py:37-43](../../db.py#L37-L43)
```python
cfg = configparser.ConfigParser()
if not cfg.read(config_file):
    raise FileNotFoundError(f"{config_file} not found. Copy db_config.example.ini to {config_file} ...")
m = cfg["mysql"]
name = m.get("database", "nostalgames")
if not name.isidentifier():
    raise ValueError(f"Invalid database name: {name}")
```
The database name is pasted into SQL in the next step, so it is checked first; only names like `nostalgames` or `my_store` are allowed.

**3. Connect:** [db.py:46-47](../../db.py#L46-L47)
```python
self.con = mysql.connector.connect(host=..., port=..., user=m["user"], password=..., autocommit=True)
self.cur = self.con.cursor()
```
This is the Class 12 pattern: `connect()` and then `cursor()`. `autocommit=True` means every `SELECT` sees the latest data, including changes made in MySQL Workbench.

**4. Create the database and tables:** [db.py:48-51](../../db.py#L48-L51), using the table definitions in [db.py:9-26](../../db.py#L9-L26)
```python
self.cur.execute(f"CREATE DATABASE IF NOT EXISTS {name} CHARACTER SET utf8mb4")
self.cur.execute(f"USE {name}")
for sql in TABLES:
    self.cur.execute(sql)        # CREATE TABLE IF NOT EXISTS users / games / purchases
```
`IF NOT EXISTS` makes this safe to run every time; existing data is never touched. `utf8mb4` lets names like `FC™ 26` be stored.

**5. Add the starting data, only if missing:** [db.py:53-55](../../db.py#L53-L55)
```python
self.users, self.games, self.purchases = UserTable(self), GameTable(self), PurchaseTable(self)
self.games.seed()                                   # 12 games, only if the table is empty
self.users.seed_admin(cfg.get("app", "admin_password", fallback="admin123"))   # only if no admin exists
```
The three table objects hold all the SQL for their table, and the screens call them, e.g. `db.purchases.buy(...)`.

**6. Share it, then close it:** [nostalgames.py:251-257](../../nostalgames.py#L251-L257)
```python
db = open_database()
user = LoginWindow(db).run() if db else None
if user:
    username, role = user
    (NGadmin if role == "admin" else NGext)(db, username).mainloop()
if db: db.close()
```
One connection serves the whole run: login, then the store, then closing.

**7. The three helpers every query goes through:** [db.py:57-81](../../db.py#L57-L81)

| Helper | Used for | Class 12 calls |
|---|---|---|
| `fetchone(sql, params)` | one row (login, wallet) | `execute()` + `fetchone()` |
| `fetchall(sql, params)` | many rows (games, library, admin tables) | `execute()` + `fetchall()` |
| `run(*statements, guard=None)` | every write, as one transaction | `start_transaction()`, `execute()`, `commit()` / `rollback()` |

**Example:** the first run on a fresh MySQL server executes:
```sql
CREATE DATABASE IF NOT EXISTS nostalgames CHARACTER SET utf8mb4;
USE nostalgames;
CREATE TABLE IF NOT EXISTS users (...);
CREATE TABLE IF NOT EXISTS games (...);
CREATE TABLE IF NOT EXISTS purchases (...);
INSERT INTO games (name, price) VALUES ('Cyberpunk 2077', 2999);   -- ×12
INSERT INTO users (username, password, role) VALUES ('admin', '<sha256 of admin123>', 'admin');
```
Every later run executes the same `CREATE ... IF NOT EXISTS` lines, which change nothing, and skips the inserts.

## What changed

| Where | Original code | Now |
|---|---|---|
| Storage | `user_data.txt` with one shared `wallet:` and `library:` line | MySQL database `nostalgames` with `users`, `games`, `purchases` |
| Game list | hard-coded dict in `NG.__init__` | `games` table, seeded from `DEFAULT_GAMES` [db.py:7](../../db.py#L7) |
| Settings | file name in code | `db_config.ini` (git-ignored) |
| Start-up | `NGext().mainloop()` | `open_database()` → login → store [nostalgames.py:251](../../nostalgames.py#L251) |

**Why:** a text file can hold one wallet for everyone. A login portal needs a wallet and library per user, and the project uses the Class 12 MySQL connectivity chapter.

More detail: [database.md](../database.md).
