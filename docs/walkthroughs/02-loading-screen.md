# 2. Loading Screen

**A red turtle animation plays in a centred 800×600 window before anything else. It runs while Python is still reading `nostalgames.py`, because it is called from inside the `NG` class body.**

## How it works, step by step

**1. It runs when the class is defined:** [nostalgames.py:71-72](../../nostalgames.py#L71-L72)
```python
class NG(tk.Tk):
    load_screen()
```
Python runs a class body once, as soon as it reads the class, so the animation plays before `__main__` connects to MySQL.

**2. Make a centred window with the drawing origin in the middle:** [nostalgames.py:17-20](../../nostalgames.py#L17-L20)
```python
setup(800, 600)  # window centred on the screen
getcanvas().update()
screensize(getcanvas().winfo_width(), getcanvas().winfo_height())
```
- `setup(800, 600)` sizes the window; with no position given, turtle centres it on the screen.
- `update()` lets Tk lay the window out so its real canvas size is known.
- `screensize(...)` makes turtle's drawing area exactly that size, so the point `(0,0)` is in the middle of the window.

**3. Draw the rosette:** [nostalgames.py:21-32](../../nostalgames.py#L21-L32)
```python
title("NOSTALgames loading.....")
bgcolor("black")
speed(0)
for i in range(50):
    color("red")
    goto(0,0)          # back to the centre
    fd(i)              # a line 1 px longer each time
    circle(100,50)     # 50° arc, radius 100, curving left
    rt(10)             # turn right 10°
    hideturtle()
```
Each stroke starts 40° further round than the last (50° left from the arc, 10° back right), building a spinning pattern around the centre. `speed(0)` is the fastest drawing speed.

**4. Close it:** [nostalgames.py:33](../../nostalgames.py#L33)
```python
bye()
```
The turtle window is destroyed before the login window opens, so the two never overlap.

**Example:** on a 1728×1117 display the loader opens at `800x600+464+258`: 464 px from the left and right edges, 258 px from the top. The animation's centre lands within 5 px of the window's middle.

## What changed

| Where | Original code | Now |
|---|---|---|
| Window size and position | turtle default (about 864×837), centred | `setup(800, 600)`, centred [nostalgames.py:17](../../nostalgames.py#L17) |
| Drawing area | default 400×300 region, pinned to the window's top-left, so the animation sat in the top-left | `screensize(...)` matches the window, so the animation is centred [nostalgames.py:20](../../nostalgames.py#L20) |
| Animation | unchanged | unchanged |

**Why:** with a 400×300 drawing area inside a bigger window, Tk shows the area from the top-left corner, so `(0,0)` appeared about 205×155 px from the corner instead of in the middle.

More detail: [features/loading-screen.md](../features/loading-screen.md).
