# User Guide

How to use NOSTALgames as a player and as an admin. For installation see the [README](../README.md).

## Starting the app

```bash
.venv/bin/python nostalgames.py
```

A red turtle animation plays in the middle of the screen, then the login window opens.

## Creating an account

1. Type a **username** using letters, digits or `_` (up to 30 characters).
2. Type a **password** of at least 4 characters.
3. Click **REGISTER**. You'll see *"Account created. You can log in now."*
   - *"That username is taken"*: choose another name.
4. Click **LOGIN**, or press **Enter**.

Every new account starts with **₹10,000** in its wallet.

## The store window

The header shows **NOSTALgames** on the left and your **WALLET** balance (yellow) on the right. Below it are three tabs.

### STORE

- The left side lists every game with its price.
- The right side is the **SHOPPING CART**.

To add a game to the cart, either:

- click its **price button**, or
- **drag** the game's row onto the cart. A yellow label follows the pointer and the cart turns blue when you're over it; let go to drop.

A game can only be in the cart once. Games you already own show **IN LIBRARY** and can't be added.

In the cart:

- Click a game to select it (it turns yellow), then **REMOVE SELECTED** to take it out.
- **PURCHASE** buys everything in the cart.
  - *"Purchased!"*: the price is taken from your wallet and the games move to your library.
  - *"Check funds or cart."*: your wallet doesn't cover the total. Nothing is charged.

### LIBRARY

Every game you own, in the order you bought them.

### SETTINGS

- **Wallet Management**
  - **Amount (₹)** is how much to add or remove. It starts at `1000.0`; this box is *not* your balance.
  - **ADD** puts that amount into your wallet (up to ₹50,000 at a time).
  - **REDUCE** takes it out. The wallet never goes below ₹0.
- **Danger Zone**
  - **RESET DATA** removes all your games and sets your wallet back to ₹10,000, after you confirm.

Everything is saved to MySQL straight away, so your wallet and library are there next time you log in.

## Logging out

Close the window. To log in as someone else, start the app again.

## Admin

Log in as `admin` (default password `admin123`, set in `db_config.ini`). An admin has the same STORE, LIBRARY and SETTINGS tabs as a player, with their own wallet, plus three more tabs.

### USERS

A table of every account: username, role, wallet and number of games owned.

- **RESET USER**: clears the selected user's library and resets their wallet to ₹10,000.
- **DELETE USER**: deletes the selected user and all their purchases.

Both ask for confirmation, and neither works on admin accounts.

### GAMES

A table of every game in the store.

- Click a row to load its name and price into the boxes below.
- **ADD / UPDATE**: type a name and a whole-number price.
  - A new name adds a game to the store.
  - An existing name changes its price.
- **REMOVE GAME**: removes the selected game from the store. People who already bought it keep it in their library.

Changes show up in the STORE tab immediately. A removed game is also taken out of the admin's cart.

### PURCHASES

Every purchase, newest first: who bought which game, the price they paid, and when. It refreshes each time you open the tab.

## Common questions

**I have ₹1000 but bought a ₹2999 game?**
Check the yellow **WALLET** in the header, not the **Amount (₹)** box on the SETTINGS tab. The database refuses any purchase the stored wallet can't cover.

**I changed my wallet in MySQL Workbench. Will the app notice?**
A purchase always checks the current value in MySQL, and the header updates after a purchase attempt or RESET DATA. ADD / REDUCE, however, work from the balance shown in the app and save that result, so they can overwrite a change made in Workbench. Log in again after editing a wallet by hand.

**I forgot the admin password.**
Set a new one in MySQL Workbench:

```sql
UPDATE nostalgames.users SET password = SHA2('new_password', 256) WHERE username = 'admin';
```
