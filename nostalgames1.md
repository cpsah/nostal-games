# nostalgames1.py — single-file version

`nostalgames1.py` contains the whole NOSTALgames app in one file. It combines, in this order:

1. `theme.py` — colours and button styles
2. `db.py` — MySQL connection and tables
3. `login.py` — login / register window
4. `admin.py` — admin tabs (users, games, purchases)
5. `nostalgames.py` — loading screen, store, cart, library, settings, wallet

Each section starts with a header comment naming the file it came from. The original files are unchanged and still work on their own.

## What changed compared to the separate files

- The imports between project files (`from theme import ...`, `from db import ...`, `from login import ...`, `from admin import ...`) are removed, because everything is now in one file.
- Standard imports (`tkinter`, `ttk`, `messagebox`, `os`, `configparser`, `hashlib`, `mysql.connector`) are listed once at the top.
- `from turtle import*` and `from colorsys import*` stay at the start of the `nostalgames.py` section, where they were originally.
- Everything else is kept exactly as it was, including the extra module-level `def reset(self)` and the `# --- PASTE EVERYTHING ...` comment.

## Requirements

- Python 3 with tkinter (included in the standard python.org installers)
- A running MySQL server
- The MySQL connector package:

  ```
  pip install mysql-connector-python
  ```

## Setup

1. Copy the example config:

   ```
   cp db_config.example.ini db_config.ini
   ```

2. Open `db_config.ini` and fill in your MySQL details:

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

   The database and tables are created automatically on the first run.

## Run

From the project folder (the one that contains `db_config.ini`):

```
python3 nostalgames1.py
```

1. The turtle loading animation plays, then closes.
2. The login window opens. Register a new account, or log in.
3. A normal user gets the store. The `admin` account (password from `admin_password`) also gets the USERS, GAMES and PURCHASES tabs.

## Troubleshooting

- **"db_config.ini not found"**: run the script from the folder that contains `db_config.ini`, or create the file as shown in Setup.
- **"Could not connect to MySQL"**: check that MySQL is running and that the user and password in `db_config.ini` are correct.
- **`ModuleNotFoundError: No module named 'mysql'`**: run `pip install mysql-connector-python`.
