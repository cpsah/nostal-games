# Theme and Buttons

Shared colours, the `ttk` button styling that makes buttons readable on macOS, and the visible cart selection.

## Code

`theme.py`:

```python
B, DB, NAV, LB, TXT, WALT, PRCHS, RED = "#661B49", "#171a21", "#2a475e", "#11F521", "#c7d5e0", "#ffcc00", "#118A1A", "#a32a2a"

def button_style(root, name, bg, fg, active_bg, size, padding):
    s = ttk.Style(root)
    s.configure(f"{name}.TButton", background=bg, foreground=fg, font=("Arial", size, "bold"),
                borderwidth=0, padding=padding)
    s.map(f"{name}.TButton", background=[("pressed", active_bg), ("active", active_bg)],
                             foreground=[("pressed", fg), ("active", fg)])

class ThemedWindow(tk.Tk):           # used by LoginWindow
    def __init__(self, title, size): ...     # title, size, background B, 'clam' theme, Nav style
    def button_style(self, name, ...): button_style(self, name, ...)
```

`nostalgames.py` keeps the same colour line at the top (as in the original code). `login.py` and `admin.py` import the colours from `theme.py`.

## Colours

| Name | Hex | Used for |
|---|---|---|
| `B` | `#661B49` | Page background, selected tab, cart listbox |
| `DB` | `#171a21` | Header, game rows, cart panel |
| `NAV` | `#2a475e` | Tabs, price buttons, IN LIBRARY badge, drop-zone highlight |
| `LB` | `#11F521` | Price text |
| `TXT` | `#c7d5e0` | Secondary text |
| `WALT` | `#ffcc00` | Wallet label, cart selection, drag ghost |
| `PRCHS` | `#118A1A` | PURCHASE and LOGIN buttons |
| `RED` | `#a32a2a` | Danger buttons, REMOVE hover |

## Why `ttk.Button` instead of `tk.Button`

On macOS, `tk.Button` is drawn by the native system button. It ignores `bg`, so the original white or light-grey text (`fg="white"`, `fg=TXT`) was drawn on a light native button and disappeared, especially while pressed.

`ttk.Button` under the `clam` theme draws the button itself and honours `background` and `foreground` from a style. Each button gets a named style:

| Style | Defined in | Button |
|---|---|---|
| `Price.TButton` | `NG.__init__` | game price |
| `Remove.TButton` | `NG.__init__` | REMOVE SELECTED (turns red on hover) |
| `Buy.TButton` | `NG.__init__` | PURCHASE |
| `Reset.TButton` | `NG.__init__` | RESET DATA |
| `Add.TButton`, `Reduce.TButton` | `NGext.add_wallet_controls` | ADD, REDUCE |
| `Nav.TButton`, `Danger.TButton` | `ThemedWindow`, `AdminTabs` | REGISTER, admin buttons |
| `Login.TButton` | `LoginWindow` | LOGIN |

`s.map(...)` sets the colours for the `pressed` and `active` (hover) states. Foreground is mapped to the same colour so the text never switches to a theme default.

### Styles are per window

`ttk.Style(root)` binds the style to that window's Tcl interpreter. The app creates several `Tk` windows one after another (turtle loader, login, store), each with its own interpreter, so every window registers the styles it uses.

## Cart selection visibility

```python
self.lbx = tk.Listbox(cf, bg=B, fg=TXT, bd=0, font=("Arial", 10),
                      selectbackground=WALT, selectforeground="black",
                      activestyle="none", highlightthickness=0, exportselection=False)
```

| Option | Why |
|---|---|
| `selectbackground=WALT`, `selectforeground="black"` | Yellow with black text. The original dark blue on dark purple was nearly invisible. |
| `exportselection=False` | Selecting text elsewhere (e.g. the amount box) doesn't clear the cart selection. |
| `activestyle="none"`, `highlightthickness=0` | No underline on the active row, no focus border. |

## Notebook tabs

```python
s.configure("TNotebook", background=DB, borderwidth=0)
s.configure("TNotebook.Tab", background=NAV, foreground=TXT, padding=[20, 10], font=("Arial", 11, "bold"))
s.map("TNotebook.Tab", background=[("selected", B)], foreground=[("selected", "white")])
```

The selected tab takes the page colour `B`, so it looks joined to its content.
