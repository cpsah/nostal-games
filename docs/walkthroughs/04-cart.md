# 4. Store and Cart

**The store loads the game list, your wallet and your library from MySQL, then draws one row per game. The cart is a plain Python list kept in memory; it is never saved until you purchase.**

## How it works, step by step

**1. Load data when the window opens:** [nostalgames.py:76-77](../../nostalgames.py#L76-L77) and [nostalgames.py:135-137](../../nostalgames.py#L135-L137)
```python
self.db, self.username, self.cart, self.games = db, username, [], db.games.all()
self.load_data()
```
```python
def load_data(self):
    self.wallet = self.db.users.wallet(self.username)
    self.library = self.db.purchases.library(self.username)
```
- `self.games` is `{name: price}` in the original store order [db.py:134-138](../../db.py#L134-L138).
- `self.library` is the list of games you own.
- `self.cart` starts empty.

**2. Build the cart panel:** [nostalgames.py:107-114](../../nostalgames.py#L107-L114)
```python
cf = tk.Frame(self.tabs["STORE"], bg=DB, width=300, ...)
tk.Label(cf, text="SHOPPING CART", ...)
tk.Label(cf, text="drag games here", ...)
self.drag = DragToCart(self, cf, self.add)
self.lbx = tk.Listbox(cf, ..., selectbackground=WALT, selectforeground="black", exportselection=False)
ttk.Button(cf, text="REMOVE SELECTED", style="Remove.TButton", command=self.rem)
ttk.Button(cf, text="PURCHASE", style="Buy.TButton", command=self.pay)
```
`self.lbx` is the list you see. `self.cart` is the data behind it; the two always hold the same games in the same order.

**3. Draw the game rows:** [nostalgames.py:142-155](../../nostalgames.py#L142-L155)
```python
self.w_lbl.config(text=f"WALLET: ₹{self.wallet}  ")
for f in [self.list_f, self.tabs["LIBRARY"]]:
    for w in f.winfo_children(): w.destroy()          # clear old rows

for g, p in self.games.items():
    row = tk.Frame(self.list_f, ...); row.pack(fill="x", pady=5)
    name = tk.Label(row, text=g, ...); name.pack(side="left")
    if g in self.library: tk.Label(row, text="IN LIBRARY", ...).pack(side="right")
    else: ttk.Button(row, text=f"₹{p}", style="Price.TButton", width=12,
                     command=lambda x=g: self.add(x)).pack(side="right"); self.drag.attach(g, row, name)

for g in self.library:
    ... tk.Label(r, text=f"🎮 {g}", ...)               # LIBRARY tab
```
- Games you own get an **IN LIBRARY** badge. Games you don't own get a price button and can be dragged.
- `lambda x=g:` captures the current game; without `x=g`, every button would add the last game.
- `refresh()` rebuilds everything from scratch after any change, so the screen always matches the data.

**4. Add to the cart:** [nostalgames.py:157-158](../../nostalgames.py#L157-L158)
```python
def add(self, g):
    if g not in self.cart: self.cart.append(g); self.lbx.insert("end", f" {g}")
```
Both the price button and drag and drop call this, so the "no duplicates" rule is in one place.

**5. Remove from the cart:** [nostalgames.py:160-162](../../nostalgames.py#L160-L162)
```python
def rem(self):
    s = self.lbx.curselection()
    if s: self.cart.pop(s[0]); self.lbx.delete(s[0])
```
The selected row number in the listbox is the same index in `self.cart`, so both are removed together.

**Example:** you own Elden Ring and click ₹2999 (Cyberpunk 2077), then ₹479 (Stardew Valley), then ₹2999 again:
```
self.cart = ['Cyberpunk 2077', 'Stardew Valley']     # second Cyberpunk click ignored
Elden Ring row shows IN LIBRARY (no button)
```
Select Cyberpunk and click REMOVE SELECTED → `self.cart = ['Stardew Valley']`.

## What changed

| Where | Original code | Now |
|---|---|---|
| Game list | hard-coded dict | `db.games.all()` from MySQL [nostalgames.py:76](../../nostalgames.py#L76) |
| Wallet and library | read from `user_data.txt` | `load_data()` reads from MySQL for the logged-in user [nostalgames.py:135](../../nostalgames.py#L135) |
| Cart panel | title, listbox, two `tk.Button`s | also a "drag games here" hint and the drop zone; `ttk.Button`s [nostalgames.py:108-114](../../nostalgames.py#L108-L114) |
| Cart selection | dark blue on dark purple, nearly invisible | yellow with black text, kept when clicking elsewhere [nostalgames.py:111](../../nostalgames.py#L111) |
| Game rows | price `tk.Button` | price `ttk.Button`, plus drag support [nostalgames.py:151](../../nostalgames.py#L151) |
| `add()` / `rem()` | unchanged | unchanged |

More detail: [features/store-and-cart.md](../features/store-and-cart.md).
