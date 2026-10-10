# NOSTALgames

A desktop game store built with Python **Tkinter** and **MySQL**. Users log in, browse the store, add games to a cart (click or drag and drop), buy them with a wallet, and see them in their library. Admins get the same store plus tabs to manage users and games and to view all purchases.

It is built around the Class 12 Python–MySQL connectivity chapter: `mysql.connector.connect()`, `cursor()`, `execute()` with `%s` placeholders, `fetchone()` / `fetchall()` and `commit()`.

## Documentation

| Document | Contents |
|---|---|
| [User guide](docs/user-guide.md) | Using the store as a player and as an admin |
| [Architecture](docs/architecture.md) | Modules, class diagram, runtime and purchase flow |
| [Flows](docs/flows.md) | Flowcharts: start-up, login, cart, purchase, wallet, admin |
| [Use cases](docs/use-cases.md) | Actors, use case diagram, use case details, business rules |
| [Database](docs/database.md) | Schema, ER diagram, queries, transactions, Class 12 connectivity mapping |
| [Code walkthroughs](docs/walkthroughs/README.md) | Step-by-step tour of each feature with links to the exact code lines, examples, and what changed from the original |
| [Feature internals](docs/features/README.md) | Code-level walkthrough of each feature: loading screen, login, store and cart, drag and drop, scrolling, purchase, wallet, admin panel, theme |
| [Changelog](docs/changelog.md) | What changed in each version |

## Features

- **Loading screen**: turtle animation, centred on the screen.
- **Login portal**: log in or self-register. Passwords are stored as SHA-256 hashes.
- **Store**: 12 games; add to the cart by clicking the price or dragging the game onto the cart; remove from the cart; purchase.
- **Library**: games you own.
- **Settings**: add money to (max ₹50,000 at a time) or take money from your wallet; reset your data.
- **Admin** (`admin` role), in addition to the store:
  - **Users**: list users with wallet and number of games; reset or delete a user.
  - **Games**: add a game, change its price, remove it.
  - **Purchases**: who bought which game, and when.
- All data (users, wallets, libraries, games) is stored in MySQL per user.
- MySQL itself checks a purchase: it is refused if the wallet stored in the database can't cover it, even if the wallet was changed elsewhere (e.g. in MySQL Workbench) while the app was open.

## Requirements

- **Python 3.11+** with Tkinter. On macOS 14 or later use a Tk version of 8.6.13 or newer; older Tk builds (such as the one bundled with Python 3.11.4 from python.org) can drop or delay mouse clicks.
- **MySQL Server 8.x**, running locally or reachable over the network.
- Python package: `mysql-connector-python`.

Check your Tk version:

```bash
python3 -c "import tkinter; print(tkinter.Tcl().eval('info patchlevel'))"
```

## Setup

1. **Create a virtual environment and install the MySQL connector**

   ```bash
   python3 -m venv .venv
   .venv/bin/pip install mysql-connector-python
   ```

   On macOS with Homebrew Python, install Tkinter first: `brew install python-tk@3.12`, then use `/opt/homebrew/bin/python3.12 -m venv .venv`.

2. **Configure the database connection**

   ```bash
   cp db_config.example.ini db_config.ini
   ```

   Edit `db_config.ini` and fill in your MySQL details:

   ```ini
   [mysql]
   host = localhost
   port = 3306
   user = root
   password = your_mysql_password
   database = nostalgames

   [app]
   admin_password = admin123
   ```

   `db_config.ini` is git-ignored so your password is never committed.

3. **Run**

   ```bash
   .venv/bin/python nostalgames.py
   ```

   On the first run the app creates the `nostalgames` database, its three tables, the 12 default games and an `admin` account. Later runs keep existing data.

## Logging in

| Account | How |
|---|---|
| Admin | Username `admin`, password from `admin_password` in `db_config.ini` (default `admin123`). Change it before the first run. |
| User | Type a new username (letters, digits, `_`, max 30) and password (min 4 characters), click **REGISTER**, then **LOGIN**. |

To add a user directly in MySQL, hash the password with `SHA2`:

```sql
USE nostalgames;
INSERT INTO users (username, password) VALUES ('rahul', SHA2('pass123', 256));
INSERT INTO users (username, password, role) VALUES ('teacher', SHA2('admin456', 256), 'admin');
```

## Database

| Table | Columns |
|---|---|
| `users` | `username` (PK), `password` (SHA-256 hex), `role` (`user` / `admin`), `wallet` (starts at ₹10,000) |
| `games` | `name` (PK), `price` |
| `purchases` | `id` (PK, auto-increment), `username` (FK to `users`, cascade delete), `game`, `price`, `bought_on`; one row per user per game |

A purchase charges the wallet and records the games in one transaction, so either everything is saved or nothing is. Removing a game from the store does not remove it from the libraries of people who already bought it.

## Project structure

| File | Purpose |
|---|---|
| `nostalgames.py` | Entry point: loading screen, store window (`NG`, `NGext`), admin window (`NGadmin`), drag and drop (`DragToCart`) |
| `login.py` | Login and registration window |
| `admin.py` | Admin tabs: users, games, purchases (`AdminTabs`) |
| `db.py` | MySQL connection, table creation, starting data, and all queries (`Database`, `UserTable`, `GameTable`, `PurchaseTable`) |
| `theme.py` | Shared colours and `ttk` button styles |
| `db_config.example.ini` | Template for `db_config.ini` |

## Troubleshooting

- **"Could not connect to MySQL: Access denied"**: wrong `user` / `password` in `db_config.ini`. Use the same credentials as in MySQL Workbench.
- **"db_config.ini not found"**: copy `db_config.example.ini` to `db_config.ini` (step 2).
- **`ModuleNotFoundError: No module named 'mysql'`**: run with `.venv/bin/python`, not the system `python3`.
- **`No module named '_tkinter'`**: your Python has no Tk; on Homebrew run `brew install python-tk@3.12`.
- **Tables not visible in MySQL Workbench**: click the refresh icon in the **Schemas** panel, then open `nostalgames` → Tables.
- **Clicks are slow or ignored on macOS**: your Tk is older than 8.6.13; use a newer Python (see Requirements).
