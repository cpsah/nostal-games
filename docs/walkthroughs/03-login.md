# 3. Login and Registration

**The login window checks your username and password against the `users` table. Passwords are compared as SHA-256 hashes, never as plain text. It returns `(username, role)`, which decides whether you get the player window or the admin window.**

## How it works, step by step

**1. Build the window:** [login.py:10-22](../../login.py#L10-L22)
```python
super().__init__("NOSTALgames - Login", "420x380")
self.db, self.user = db, None
...
self.username = self.field(box, "Username")
self.password = self.field(box, "Password", show="*")
ttk.Button(box, text="LOGIN", style="Login.TButton", command=self.login)...
ttk.Button(box, text="REGISTER", style="Nav.TButton", command=self.register)...
self.bind("<Return>", lambda e: self.login())
```
- `field()` [login.py:24-28](../../login.py#L24-L28) makes a label and a text box and returns its `StringVar`.
- `show="*"` hides the password.
- Pressing **Enter** logs in.

**2. Register:** [login.py:42-49](../../login.py#L42-L49)
```python
username, password = self.credentials()
if not (username.replace("_", "").isalnum() and len(username) <= 30) or len(password) < 4:
    messagebox.showerror("Register", "Username: letters, digits or _ (max 30).\nPassword: at least 4 characters.")
elif self.db.users.register(username, password):
    messagebox.showinfo("Register", "Account created. You can log in now.")
else:
    messagebox.showerror("Register", "That username is taken.")
```

**3. Save the new user:** [db.py:100-105](../../db.py#L100-L105)
```python
def register(self, username, password):
    try:
        self.db.run(("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hash_password(password))))
        return True
    except mysql.connector.IntegrityError:      # username already exists (PRIMARY KEY)
        return False
```
`hash_password` [db.py:29-30](../../db.py#L29-L30) is `hashlib.sha256(password.encode()).hexdigest()`. The new row gets `role = 'user'` and `wallet = 10000` from the column defaults.

**4. Log in:** [login.py:33-40](../../login.py#L33-L40)
```python
username, password = self.credentials()
role = self.db.users.login(username, password)
if not role:
    messagebox.showerror("Login failed", "Wrong username or password.")
    return
self.user = (username, role)
self.destroy()
```

**5. Check the password in MySQL:** [db.py:95-98](../../db.py#L95-L98)
```python
row = self.db.fetchone("SELECT role FROM users WHERE username = %s AND password = %s",
                       (username, hash_password(password)))
return row[0] if row else None
```
`%s` placeholders let the connector insert the values safely, which blocks SQL injection.

**6. Open the right window:** [login.py:51-53](../../login.py#L51-L53) and [nostalgames.py:253-256](../../nostalgames.py#L253-L256)
```python
def run(self):
    self.mainloop()          # waits until login() closes the window
    return self.user         # (username, role), or None if the window was closed
```
```python
user = LoginWindow(db).run() if db else None
if user:
    username, role = user
    (NGadmin if role == "admin" else NGext)(db, username).mainloop()
```

**Example:** registering `rahul` / `pass123` and then logging in:
```sql
INSERT INTO users (username, password) VALUES ('rahul', '9b8769a4a742959a2d0298c36fb70623f2dfacda8436237df08d8dfd5b37374c');
SELECT role FROM users WHERE username = 'rahul' AND password = '9b8769a4...';   -- returns 'user'
```
→ the store opens for `rahul`.

## What changed

| Where | Original code | Now |
|---|---|---|
| Login | none: the app opened straight into the store | `LoginWindow` [login.py:7](../../login.py#L7) |
| Accounts | one shared wallet in a text file | one row per user in `users` |
| Passwords | n/a | SHA-256 hash [db.py:29](../../db.py#L29) |
| Roles | n/a | `user` → `NGext`, `admin` → `NGadmin` [nostalgames.py:256](../../nostalgames.py#L256) |

**Why:** the project needed separate users and admins, each with their own wallet and library.

More detail: [features/login-and-registration.md](../features/login-and-registration.md).
