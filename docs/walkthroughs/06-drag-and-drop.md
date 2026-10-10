# 6. Drag and Drop

**Press on a game row, drag, and release over the SHOPPING CART to add the game. A small `DragToCart` object handles the mouse events; when you drop on the cart it calls the same `add()` the price button uses.**

## How it works, step by step

**1. Create the helper with the cart as the drop zone:** [nostalgames.py:110](../../nostalgames.py#L110)
```python
self.drag = DragToCart(self, cf, self.add)     # window, drop zone (the cart panel), what to call on drop
```
[nostalgames.py:38-41](../../nostalgames.py#L38-L41) stores these, remembers the cart's normal colour, and starts with no game and no ghost label.

**2. Make each unowned game draggable:** [nostalgames.py:151](../../nostalgames.py#L151) → [nostalgames.py:43-48](../../nostalgames.py#L43-L48)
```python
self.drag.attach(g, row, name)          # in refresh(), for games you don't own
```
```python
def attach(self, game, *widgets):
    for w in widgets:
        w.configure(cursor="hand2")
        w.bind("<ButtonPress-1>", lambda e, g=game: self.start(g))
        w.bind("<B1-Motion>", self.move)
        w.bind("<ButtonRelease-1>", self.drop)
```
Both the row and the game-name label respond. Once you press on a widget, Tk sends all further motion and release events to that same widget, even when the pointer leaves it, which is what lets the drag be tracked across the window.

**3. Press: remember the game:** [nostalgames.py:50-51](../../nostalgames.py#L50-L51)
```python
def start(self, game):
    self.game = game
```

**4. Move: show the ghost label and highlight the cart:** [nostalgames.py:53-59](../../nostalgames.py#L53-L59)
```python
if not self.game: return
if not self.ghost:
    self.ghost = tk.Label(self.root, text=f"🎮 {self.game}", bg=WALT, fg="black", ...)
self.ghost.place(x=e.x_root - self.root.winfo_rootx() + 12, y=e.y_root - self.root.winfo_rooty() + 12)
self.ghost.lift()
self.zone.configure(bg=NAV if self.over_zone(e) else self.zone_bg)
```
- The yellow label is created on the first movement and follows the pointer, offset 12 px down and right.
- `e.x_root` is a screen position; subtracting the window's screen position gives the position inside the window.
- The cart panel turns blue while the pointer is over it.

**5. Is the pointer over the cart?** [nostalgames.py:61-63](../../nostalgames.py#L61-L63)
```python
x, y = e.x_root - self.zone.winfo_rootx(), e.y_root - self.zone.winfo_rooty()
return 0 <= x < self.zone.winfo_width() and 0 <= y < self.zone.winfo_height()
```

**6. Release: add if over the cart, then clean up:** [nostalgames.py:65-69](../../nostalgames.py#L65-L69)
```python
if self.game and self.ghost and self.over_zone(e): self.on_drop(self.game)   # on_drop = NG.add
if self.ghost: self.ghost.destroy()
self.zone.configure(bg=self.zone_bg)
self.game = self.ghost = None
```
A click without moving never creates a ghost, so it adds nothing.

**Example:** drag "Hollow Knight" from the list:

| Mouse | What happens |
|---|---|
| press on the row | `self.game = "Hollow Knight"` |
| move | yellow "🎮 Hollow Knight" follows the pointer |
| move over the cart | cart panel turns blue |
| release over the cart | `add("Hollow Knight")` → appears in the cart; label removed |
| (release elsewhere instead) | label removed, nothing added |

## What changed

| Where | Original code | Now |
|---|---|---|
| `DragToCart` [nostalgames.py:35-69](../../nostalgames.py#L35-L69) | did not exist | new class |
| `NG.__init__` [nostalgames.py:109-110](../../nostalgames.py#L109-L110) | cart title only | "drag games here" hint and `self.drag = DragToCart(...)` |
| `refresh()` [nostalgames.py:151](../../nostalgames.py#L151) | price button only | also `self.drag.attach(g, row, name)` for unowned games |

**Why:** you asked for the store to support dragging games into the checkout area. No earlier commit had drag and drop.

More detail: [features/drag-and-drop.md](../features/drag-and-drop.md).
