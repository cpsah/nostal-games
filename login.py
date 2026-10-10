import tkinter as tk
from tkinter import ttk, messagebox

from theme import ThemedWindow, B, DB, TXT, PRCHS


class LoginWindow(ThemedWindow):
    """Login / sign-up portal. run() returns (username, role) or None if the window was closed."""

    def __init__(self, db):
        super().__init__("NOSTALgames - Login", "420x380")
        self.db, self.user = db, None
        self.button_style("Login", PRCHS, "white", "#14a01f", 12, 8)

        box = tk.Frame(self, bg=DB, padx=30, pady=30); box.pack(expand=1)
        tk.Label(box, text="NOSTALgames", font=("Arial", 20, "bold"), bg=DB, fg="white").pack(pady=(0, 20))
        self.username = self.field(box, "Username")
        self.password = self.field(box, "Password", show="*")

        ttk.Button(box, text="LOGIN", style="Login.TButton", command=self.login).pack(fill="x", pady=(15, 5))
        ttk.Button(box, text="REGISTER", style="Nav.TButton", command=self.register).pack(fill="x")
        self.bind("<Return>", lambda e: self.login())

    def field(self, parent, label, show=""):
        tk.Label(parent, text=label, bg=DB, fg=TXT, font=("Arial", 10)).pack(anchor="w")
        var = tk.StringVar()
        tk.Entry(parent, textvariable=var, show=show, font=("Arial", 12), width=24, bg=B, fg="white", insertbackground="white").pack(pady=(0, 10))
        return var

    def credentials(self):
        return self.username.get().strip(), self.password.get()

    def login(self):
        username, password = self.credentials()
        role = self.db.users.login(username, password)
        if not role:
            messagebox.showerror("Login failed", "Wrong username or password.")
            return
        self.user = (username, role)
        self.destroy()

    def register(self):
        username, password = self.credentials()
        if not (username.replace("_", "").isalnum() and len(username) <= 30) or len(password) < 4:
            messagebox.showerror("Register", "Username: letters, digits or _ (max 30).\nPassword: at least 4 characters.")
        elif self.db.users.register(username, password):
            messagebox.showinfo("Register", "Account created. You can log in now.")
        else:
            messagebox.showerror("Register", "That username is taken.")

    def run(self):
        self.mainloop()
        return self.user
