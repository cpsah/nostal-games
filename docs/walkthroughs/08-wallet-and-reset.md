# 8. Wallet and Reset

**The SETTINGS tab changes the wallet with ADD and REDUCE, and RESET DATA wipes your library. ADD and REDUCE compute the new balance in Python and save it with one `UPDATE`; RESET runs two statements as one transaction.**

## How it works, step by step

**1. Add the Wallet Management box above the Danger Zone:** [nostalgames.py:181-202](../../nostalgames.py#L181-L202)
```python
class NGext(NG):
    def __init__(self, db, username):
        super().__init__(db, username)
        self.add_wallet_controls()
```
```python
wm_frame.pack(fill="x", padx=50, pady=(20, 0), before=self.tabs["SETTINGS"].winfo_children()[0])
self.amount_var = tk.DoubleVar(value=1000.0)
tk.Entry(wm_frame, textvariable=self.amount_var, ...)
ttk.Button(wm_frame, text="ADD", style="Add.TButton", command=self.add_money)
ttk.Button(wm_frame, text="REDUCE", style="Reduce.TButton", command=self.reduce_money)
```
- `before=` puts the box above the Danger Zone, which `NG` built first.
- The **Amount** box starts at `1000.0`. It is the amount to add or remove, not your balance.

**2. ADD:** [nostalgames.py:204-215](../../nostalgames.py#L204-L215)
```python
addamount=abs(self.amount_var.get())       # TclError if the box isn't a number
if addamount>50000.0:
    messagebox.showerror("Limit Exceeded!"," You can only add upto ₹50000 at a time.")
    return
self.wallet += addamount
self.save_data()
self.refresh()
```

**3. REDUCE:** [nostalgames.py:217-224](../../nostalgames.py#L217-L224)
```python
self.wallet = max(0.0, self.wallet - abs(self.amount_var.get()))
self.save_data()
self.refresh()
```
`max(0.0, ...)` stops the wallet going below zero.

**4. Save the wallet:** [nostalgames.py:139-140](../../nostalgames.py#L139-L140) → [db.py:110-111](../../db.py#L110-L111)
```python
def save_data(self):
    self.db.users.set_wallet(self.username, self.wallet)
```
```python
self.db.run(("UPDATE users SET wallet = %s WHERE username = %s", (amount, username)))
```

**5. RESET DATA:** [nostalgames.py:169-172](../../nostalgames.py#L169-L172) → [db.py:113-115](../../db.py#L113-L115)
```python
if messagebox.askyesno("Reset", "Wipe all data?"):
    self.db.users.reset(self.username)
    self.load_data(); self.cart = []; self.lbx.delete(0, "end"); self.refresh()
```
```python
self.db.run(("DELETE FROM purchases WHERE username = %s", (username,)),
            ("UPDATE users SET wallet = %s WHERE username = %s", (START_WALLET, username)))
```
Both statements run in one transaction. Afterwards every game is back in the store with a price button.

**Example:** wallet ₹9522, Amount `3000`:

| Click | SQL | Header |
|---|---|---|
| ADD | `UPDATE users SET wallet = 12522.0 WHERE username = 'admin'` | WALLET: ₹12522.0 |
| REDUCE | `UPDATE users SET wallet = 9522.0 ...` | WALLET: ₹9522.0 |
| Amount `60000`, ADD | none | "Limit Exceeded!" |
| Amount `abc`, ADD | none | "Please enter a valid number." |
| RESET DATA → Yes | `DELETE FROM purchases ...` + `UPDATE users SET wallet = 10000.0 ...` | WALLET: ₹10000.0, library empty |

## What changed

| Where | Original code | Now |
|---|---|---|
| `save_data()` [nostalgames.py:139](../../nostalgames.py#L139) | wrote `wallet:` and `library:` to `user_data.txt` | `UPDATE users SET wallet` for this user |
| `reset()` [nostalgames.py:169](../../nostalgames.py#L169) | deleted `user_data.txt` | `db.users.reset()`: deletes this user's purchases and restores ₹10,000 in one transaction |
| ADD / REDUCE buttons [nostalgames.py:199-202](../../nostalgames.py#L199-L202) | `tk.Button` | `ttk.Button` with `Add` / `Reduce` styles |
| `add_money()` / `reduce_money()` | unchanged | unchanged |

**Known limitation:** ADD and REDUCE start from `self.wallet`, the balance the app last loaded. If the wallet was changed in MySQL Workbench while the app was open, ADD or REDUCE overwrites that change. Purchases are not affected (see [05-purchase.md](05-purchase.md)).

More detail: [features/wallet-and-reset.md](../features/wallet-and-reset.md).
