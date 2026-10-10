# Code Walkthroughs

Short, step-by-step explanations of how each feature works in the code. Every step links to the exact lines, shows the code, and ends with a table of what changed compared with the original single-file version (commit `39031c5`).

Read them in order for a full tour of the app, or jump to one feature. For deeper reference material (edge cases, design notes, more diagrams) see [features/](../features/README.md).

| # | Walkthrough | Files |
|---|---|---|
| 1 | [Database setup](01-database-setup.md): connect, create tables, add starting data | `db.py`, `nostalgames.py` |
| 2 | [Loading screen](02-loading-screen.md): turtle animation, centred | `nostalgames.py` |
| 3 | [Login and registration](03-login.md) | `login.py`, `db.py` |
| 4 | [Store and cart](04-cart.md): game list, add, remove | `nostalgames.py` |
| 5 | [Purchase](05-purchase.md): charge the wallet, save the games | `nostalgames.py`, `db.py` |
| 6 | [Drag and drop](06-drag-and-drop.md) | `nostalgames.py` |
| 7 | [Store scrolling](07-store-scrolling.md) | `nostalgames.py` |
| 8 | [Wallet and reset](08-wallet-and-reset.md) | `nostalgames.py`, `db.py` |
| 9 | [Admin panel](09-admin.md) | `nostalgames.py`, `admin.py`, `db.py` |
| 10 | [Buttons and theme](10-buttons-and-theme.md) | `theme.py`, `nostalgames.py` |

Line numbers match the code at the time of writing. If a link lands a few lines off after later edits, search for the function name.
