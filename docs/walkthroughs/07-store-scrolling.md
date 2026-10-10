# 7. Store Scrolling

**The game list sits inside a `Canvas`, which can scroll. A scrollbar is linked to it, and app-wide mouse-wheel and trackpad handlers scroll it only when the pointer is over the list.**

## How it works, step by step

**1. Canvas, scrollbar and the frame of rows:** [nostalgames.py:100-105](../../nostalgames.py#L100-L105)
```python
self.canv = tk.Canvas(sc, bg=B, highlightthickness=0, yscrollincrement=1)
sb = ttk.Scrollbar(sc, orient="vertical", command=self.canv.yview); sb.pack(side="right", fill="y")
self.canv.configure(yscrollcommand=sb.set); self.canv.pack(side="left", fill="both", expand=1)
self.bind_scroll()
self.list_f = tk.Frame(self.canv, bg=B); self.canv.create_window((0,0), window=self.list_f, anchor="nw", width=600)
self.list_f.bind("<Configure>", lambda e: self.canv.configure(scrollregion=self.canv.bbox("all")))
```
- The rows go in `list_f`, which is placed inside the canvas with `create_window`.
- Whenever `list_f` changes size, its `<Configure>` handler sets `scrollregion` to the size of the content.
- `command=canv.yview` means dragging the bar scrolls the canvas; `yscrollcommand=sb.set` means scrolling the canvas moves the bar.
- `yscrollincrement=1` makes one scroll "unit" equal one pixel.

**2. Catch wheel and trackpad events:** [nostalgames.py:122-128](../../nostalgames.py#L122-L128)
```python
self.bind_all("<MouseWheel>", lambda e: self.scroll_store(e, -40 if e.delta > 0 else 40))   # macOS / Windows wheel
self.bind_all("<Button-4>", lambda e: self.scroll_store(e, -40))                            # Linux wheel up
self.bind_all("<Button-5>", lambda e: self.scroll_store(e, 40))                             # Linux wheel down
try: self.bind_all("<TouchpadScroll>", lambda e: self.scroll_store(e,
        -int(self.tk.splitlist(self.tk.call("tk::PreciseScrollDeltas", e.delta))[1])))     # Tk 9 trackpad
except tk.TclError: pass                                                                    # Tk 8.6 doesn't have it
```
- A mouse wheel moves 40 px per notch.
- A trackpad on Tk 9 reports exact pixel distances, which Tk's `tk::PreciseScrollDeltas` decodes into `(dx, dy)`; only `dy` is used.

**3. Scroll only over the store list:** [nostalgames.py:130-133](../../nostalgames.py#L130-L133)
```python
w = self.winfo_containing(e.x_root, e.y_root)
if w and str(w).startswith(str(self.canv)): self.canv.yview_scroll(pixels, "units")
```
`winfo_containing` finds the widget under the pointer. Every widget inside the canvas has a Tk path that starts with the canvas's path, so this matches the list and its rows but not the cart or the admin tables.

**Example:** at the default size the list is 804 px tall in a 555 px view, so it can move 249 px:

| Action | Scroll position |
|---|---|
| start | 0 |
| wheel down | 40 |
| wheel down | 80 |
| wheel up | 40 |
| wheel over the cart | 40 (unchanged) |
| trackpad 25 px down | 65 |
| keep scrolling down | stops at 249: last game (FC™ 26) fully visible |

## What changed

| Where | Original code | Now |
|---|---|---|
| Canvas [nostalgames.py:100](../../nostalgames.py#L100) | plain canvas | `yscrollincrement=1` |
| Scrollbar [nostalgames.py:101-102](../../nostalgames.py#L101-L102) | none | `ttk.Scrollbar` linked both ways |
| `bind_scroll()` [nostalgames.py:122](../../nostalgames.py#L122) | did not exist | wheel, Linux buttons and trackpad handlers |
| `scroll_store()` [nostalgames.py:130](../../nostalgames.py#L130) | did not exist | scrolls only when the pointer is over the list |

**Why:** the original code set a `scrollregion` but never connected anything that scrolls it, so the last games were cut off and couldn't be reached.

More detail: [features/store-scrolling.md](../features/store-scrolling.md).
