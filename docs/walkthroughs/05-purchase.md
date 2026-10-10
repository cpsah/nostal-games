# 5. Purchase

**The cart lives in memory in the store window. PURCHASE hands the whole cart to MySQL, which checks the wallet, charges it and records the games in one transaction: either everything is saved or nothing is.**

## How it works, step by step

**1. Clicking PURCHASE:** [nostalgames.py:164-167](../../nostalgames.py#L164-L167)
```python
def pay(self):
    if self.cart and self.db.purchases.buy(self.username, {g: self.games[g] for g in self.cart}):
        self.load_data(); self.cart = []; self.lbx.delete(0, "end"); self.refresh(); messagebox.showinfo("OK", "Purchased!")
    elif self.cart: self.load_data(); self.refresh(); messagebox.showerror("Error", "Check funds or cart.")
```
- It builds `{game: price}` from the cart, e.g. `{"Stardew Valley": 479}`, and asks the database to buy it.
- **`True`:** reload the wallet and library, empty the cart, redraw the store, show "Purchased!".
- **`False`:** reload the wallet so the header shows the real balance, redraw, show "Check funds or cart.". The cart is kept.
- **Empty cart:** nothing happens.

**2. Building the SQL:** [db.py:154-159](../../db.py#L154-L159)
```python
def buy(self, username, items):
    cost = sum(items.values())
    return self.db.run(
        *[("INSERT INTO purchases (username, game, price) VALUES (%s, %s, %s)", (username, g, p)) for g, p in items.items()],
        guard=("UPDATE users SET wallet = wallet - %s WHERE username = %s AND wallet >= %s", (cost, username, cost)))
```
- The **guard** checks and charges the wallet in one statement. MySQL subtracts only if the stored wallet is at least the cost.
- Then there's one `INSERT` per game into `purchases`.

**3. Running it as one transaction:** [db.py:65-81](../../db.py#L65-L81)
```python
self.con.start_transaction()
if guard:
    self.cur.execute(*guard)
    if self.cur.rowcount == 0:      # wallet too low → nothing updated
        self.con.rollback()
        return False
for sql, params in statements:      # the INSERTs
    self.cur.execute(sql, params)
self.con.commit()
return True
```
If any step fails, `rollback()` undoes everything, so you are never charged without getting the games, or given the games without being charged.

**Example:** wallet ₹1000, cart = Stardew Valley + Hollow Knight (₹1079):
```sql
START TRANSACTION;
UPDATE users SET wallet = wallet - 1079 WHERE username='rahul' AND wallet >= 1079;  -- 0 rows → ROLLBACK
```
→ "Check funds or cart.", wallet still ₹1000.

Remove Hollow Knight (₹479):
```sql
START TRANSACTION;
UPDATE users SET wallet = wallet - 479 WHERE username='rahul' AND wallet >= 479;    -- 1 row
INSERT INTO purchases (username, game, price) VALUES ('rahul', 'Stardew Valley', 479);
COMMIT;
```
→ "Purchased!", wallet ₹521.0, Stardew Valley shows IN LIBRARY.

## What changed

| Where | Original code | Now |
|---|---|---|
| `pay()` [nostalgames.py:164](../../nostalgames.py#L164) | checked `self.wallet >= cost` in Python, appended to `self.library`, wrote the new wallet to `user_data.txt` | asks MySQL via `buy()` and acts on its `True`/`False` |
| `buy()` [db.py:154](../../db.py#L154) | did not exist | guarded wallet `UPDATE` plus one `INSERT` per game |
| `run()` [db.py:65](../../db.py#L65) | did not exist | transaction with commit/rollback and the `guard` option |
| connection [db.py:46](../../db.py#L46) | did not exist | `autocommit=True`, so the app always reads the current wallet |

**Why the check moved into MySQL:** the first MySQL version still checked `self.wallet` in Python, which was the value loaded at login, and the connection kept reading old data. A wallet lowered in Workbench while the app was open was ignored, so a ₹2999 game could be bought with ₹1000. Now MySQL checks the real stored value at the moment of purchase.

More detail: [features/purchase.md](../features/purchase.md).
