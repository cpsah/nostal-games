# Changelog

## Unreleased

### Added

- **Login portal** (`login.py`): log in or self-register. Passwords are stored as SHA-256 hashes.
- **User and admin roles.** Users get the store. Admins get the store plus USERS, GAMES and PURCHASES tabs (`admin.py`, `NGadmin`).
- **MySQL storage** (`db.py`): users, wallets, libraries and the game catalogue are stored per user in the `nostalgames` database. The database, tables, default games and `admin` account are created on first run.
- **Drag and drop to cart** (`DragToCart`): drag a game row onto the shopping cart to add it.
- **Config file:** `db_config.example.ini` template. The real `db_config.ini` is git-ignored.
- **Documentation:** README, plus [architecture](architecture.md), [flows](flows.md), [use cases](use-cases.md), [database](database.md), [user guide](user-guide.md) per-feature code docs in [features/](features/README.md), and step-by-step [walkthroughs/](walkthroughs/README.md).

### Changed

- **Data storage:** the store reads and writes MySQL instead of `user_data.txt`, which is no longer used or migrated.
- **Purchase check:** a purchase now runs as one transaction and is refused by MySQL if the stored wallet can't cover it. Purchases can no longer overdraw a wallet that was changed in MySQL Workbench while the app was open.
- **Loading screen:** the turtle animation now draws in the centre of an 800×600 window that is itself centred on the screen. Before, it appeared in the window's top-left area.
- **Code organisation:** colours and button styles are shared through `theme.py`.

### Removed

- **Duplicate code:** the unused module-level copy of `reset()` was deleted.

## e600749: Better visual change

### Fixed

- **Invisible button text on macOS:** every button is now a `ttk.Button` with a custom style. `tk.Button` ignores background colours on macOS, so its white or light text disappeared, especially when clicked.
- **Cart selection:** the selected cart item is now a clear yellow highlight with black text, and stays selected when you click REMOVE SELECTED.

## 39031c5: Initial code

- Tkinter game store with STORE, LIBRARY and SETTINGS tabs.
- Shopping cart with REMOVE SELECTED and PURCHASE.
- Wallet with ADD / REDUCE (max ₹50,000 per add) and RESET DATA.
- Turtle loading animation.
- Wallet and library saved to `user_data.txt`.

## 659fde2: Initial commit

- Repository created.
