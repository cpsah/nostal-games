# Flows

Step-by-step flowcharts of the main paths through NOSTALgames. For the module and class structure see [architecture.md](architecture.md); for actors and rules see [use-cases.md](use-cases.md).

## Application start-up

```mermaid
flowchart TD
    A[Run nostalgames.py] --> B[load_screen:<br/>turtle animation, centred]
    B --> C{db_config.ini found<br/>and MySQL reachable?}
    C -- no --> E[Popup: Database error] --> Z([Exit])
    C -- yes --> D[CREATE DATABASE / TABLES IF NOT EXISTS<br/>seed games and admin if missing]
    D --> F[LoginWindow]
    F --> G{Logged in?}
    G -- window closed --> Y[db.close] --> Z
    G -- yes --> H{role}
    H -- user --> I[NGext: store window]
    H -- admin --> J[NGadmin: store + admin tabs]
    I --> K[Window closed] --> Y
    J --> K
```

## Login and registration

```mermaid
flowchart TD
    A[Login window] --> B{Button}
    B -- REGISTER --> C{Username: letters, digits, _<br/>max 30 chars?<br/>Password at least 4 chars?}
    C -- no --> C1[Error: rules] --> A
    C -- yes --> D[INSERT INTO users<br/>password = SHA-256]
    D --> E{Duplicate username?}
    E -- yes --> E1[Error: That username is taken] --> A
    E -- no --> E2[Account created] --> A
    B -- LOGIN / Enter --> F[SELECT role FROM users<br/>WHERE username AND password hash match]
    F --> G{Row found?}
    G -- no --> G1[Error: Wrong username or password] --> A
    G -- yes --> H[Return username, role<br/>close login window]
```

## Adding to the cart

```mermaid
flowchart TD
    A[Game row in STORE] --> B{Owned?}
    B -- yes --> B1[Shows IN LIBRARY<br/>not clickable, not draggable]
    B -- no --> C{Action}
    C -- click price --> F[NG.add game]
    C -- press on row --> D[DragToCart.start]
    D --> D1[Mouse moves:<br/>yellow label follows pointer<br/>cart turns blue when over it]
    D1 --> E{Released over cart?}
    E -- no --> E1[Cancel: label removed]
    E -- yes --> F
    F --> G{Already in cart?}
    G -- yes --> G1[Ignore]
    G -- no --> H[Append to cart list and listbox]
```

## Purchase

```mermaid
flowchart TD
    A[Click PURCHASE] --> B{Cart empty?}
    B -- yes --> B1[Nothing happens]
    B -- no --> C[START TRANSACTION]
    C --> D["UPDATE users SET wallet = wallet - total<br/>WHERE username = me AND wallet >= total"]
    D --> E{Row updated?}
    E -- no --> F[ROLLBACK] --> F1[Reload wallet from MySQL<br/>Error: Check funds or cart.]
    E -- yes --> G[INSERT one purchases row per game]
    G --> H{MySQL error?}
    H -- yes --> I[ROLLBACK, raise]
    H -- no --> J[COMMIT]
    J --> K[Reload wallet and library<br/>clear cart, redraw store<br/>Purchased!]
```

## Wallet management

```mermaid
flowchart TD
    A[SETTINGS: Amount box] --> B{Button}
    B -- ADD --> C{Valid number?}
    C -- no --> X[Error: Please enter a valid number]
    C -- yes --> D{Amount > 50,000?}
    D -- yes --> D1[Error: Limit Exceeded!]
    D -- no --> E[wallet = wallet + amount]
    B -- REDUCE --> F{Valid number?}
    F -- no --> X
    F -- yes --> G[wallet = max 0, wallet - amount]
    E --> H[UPDATE users SET wallet<br/>redraw header]
    G --> H
    B -- RESET DATA --> I{Confirm?}
    I -- no --> I1[Nothing happens]
    I -- yes --> J[Transaction:<br/>DELETE my purchases<br/>wallet = 10,000]
    J --> K[Reload, clear cart, redraw]
```

## Admin: managing games

```mermaid
flowchart TD
    A[GAMES tab] --> B{Action}
    B -- click row --> C[Fill Name and Price boxes]
    B -- ADD / UPDATE --> D{Name 1-60 chars and<br/>price a whole number?}
    D -- no --> D1[Error] --> A
    D -- yes --> E[INSERT ... ON DUPLICATE KEY UPDATE price]
    B -- REMOVE GAME --> F{Row selected and confirmed?}
    F -- no --> A
    F -- yes --> G[DELETE FROM games<br/>buyers keep it in library]
    E --> H[Refresh admin tables]
    G --> H
    H --> I[NGadmin.reload_games:<br/>reload catalogue, drop removed games from cart,<br/>redraw STORE]
```

## Admin: managing users

```mermaid
flowchart TD
    A[USERS tab] --> B[Select row]
    B --> C{Role = user?}
    C -- no / nothing selected --> C1[Error: Select a non-admin user first.]
    C -- yes --> D{Button}
    D -- RESET USER --> E{Confirm?} -- yes --> E1[Delete their purchases<br/>wallet = 10,000]
    D -- DELETE USER --> F{Confirm?} -- yes --> F1[DELETE user<br/>purchases removed by CASCADE]
    E1 --> G[Refresh tables]
    F1 --> G
```
