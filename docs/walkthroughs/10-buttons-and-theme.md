# 10. Buttons and Theme

**Every button is a `ttk.Button` with a named style created by one shared function, `button_style()`. That is what makes the custom colours and white text show up on macOS, where `tk.Button` ignores background colours.**

## How it works, step by step

**1. Shared colours:** [theme.py:5](../../theme.py#L5) (the same line is kept at [nostalgames.py:14](../../nostalgames.py#L14), as in the original code)
```python
B, DB, NAV, LB, TXT, WALT, PRCHS, RED = "#661B49", "#171a21", "#2a475e", "#11F521", "#c7d5e0", "#ffcc00", "#118A1A", "#a32a2a"
```

**2. One function defines a button style:** [theme.py:8-12](../../theme.py#L8-L12)
```python
def button_style(root, name, bg, fg, active_bg, size, padding):
    s = ttk.Style(root)
    s.configure(f"{name}.TButton", background=bg, foreground=fg, font=("Arial", size, "bold"), borderwidth=0, padding=padding)
    s.map(f"{name}.TButton", background=[("pressed", active_bg), ("active", active_bg)], foreground=[("pressed", fg), ("active", fg)])
```
- `configure` sets the normal look.
- `map` sets the look while pressed and while hovered (`active`). The text colour is mapped to itself, so it never changes to a default and disappears.

**3. Use the `clam` theme, which respects custom colours:** [nostalgames.py:80](../../nostalgames.py#L80)
```python
s = ttk.Style(self); s.theme_use('clam')
```

**4. Register styles, then use them by name:** [nostalgames.py:84-87](../../nostalgames.py#L84-L87) and [nostalgames.py:113-114](../../nostalgames.py#L113-L114)
```python
button_style(self, "Remove", "#2a2a2a", TXT, RED, 9, 5)
button_style(self, "Buy", PRCHS, "white", "#14a01f", 12, 10)
button_style(self, "Reset", RED, "white", "#c43a3a", 10, (20, 5))
button_style(self, "Price", NAV, LB, "#3a6a8a", 10, 5)
```
```python
ttk.Button(cf, text="REMOVE SELECTED", style="Remove.TButton", command=self.rem)
ttk.Button(cf, text="PURCHASE", style="Buy.TButton", command=self.pay)
```
The other screens do the same: `Add`/`Reduce` in `NGext`, `Nav`/`Danger` in `AdminTabs` and `ThemedWindow`, `Login` in `LoginWindow`.

**5. Visible cart selection:** [nostalgames.py:111](../../nostalgames.py#L111)
```python
tk.Listbox(cf, ..., selectbackground=WALT, selectforeground="black", activestyle="none", highlightthickness=0, exportselection=False)
```
Yellow with black text, and `exportselection=False` keeps the selection when you click into another box.

**Example:** the PURCHASE button:

| State | Background | Text |
|---|---|---|
| normal | `#118A1A` (`PRCHS`) | white |
| hover | `#14a01f` | white |
| pressed | `#14a01f` | white |

With the original `tk.Button(bg=PRCHS, fg="white")` on macOS, the background was ignored and white text was drawn on a light system button, so the label vanished.

## What changed

| Where | Original code | Now |
|---|---|---|
| Buttons | `tk.Button(bg=..., fg=..., relief="flat")` | `ttk.Button(style="<Name>.TButton")` everywhere |
| Styles | none | `button_style()` [theme.py:8](../../theme.py#L8), shared by every window |
| Cart selection | `selectbackground=NAV` (dark blue on dark purple) | `selectbackground=WALT`, black text, `exportselection=False` |
| Colours for other files | only in `nostalgames.py` | also in `theme.py`, imported by `login.py` and `admin.py` |

**Why:** you reported that button text disappeared after clicking and that the cart selection couldn't be seen.

More detail: [features/theme-and-buttons.md](../features/theme-and-buttons.md).
