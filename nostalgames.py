import tkinter as tk
from tkinter import ttk, messagebox
import os
from turtle import*
from colorsys import*

# Theme Shorthand
B, DB, NAV, LB, TXT, WALT, PRCHS, RED = "#661B49", "#171a21", "#2a475e", "#11F521", "#c7d5e0", "#ffcc00", "#118A1A", "#a32a2a"

def load_screen():
    title("NOSTALgames loading.....")
    bgcolor("black")
    speed(0)
    h=0
    for i in range(50):
        h+=0.0015
        color("red")
        goto(0,0)
        fd(i)
        circle(100,50)
        rt(10)
        hideturtle()
    bye()

class NG(tk.Tk):
    load_screen()
    def __init__(self):
        super().__init__()
        self.title("NOSTALgames"); self.geometry("1000x700"); self.configure(bg=B)
        self.file, self.cart, self.games = "user_data.txt", [], {"Cyberpunk 2077": 2999, "Elden Ring": 3500, "Stardew Valley": 479, "Hollow Knight": 600, "Doom Eternal": 1799, "Forza Horizon 5": 3499, "Forza Horizon 6": 4599, "Counter Strike 2": 1399, "Subnautica 2":1799, "NBA 2K26":3999, "Red Dead Redemption 2":4999, "FC™ 26": 1625}
        self.load_data()
       
        # Styles
        s = ttk.Style(); s.theme_use('clam')
        s.configure("TNotebook", background=DB, borderwidth=0)
        s.configure("TNotebook.Tab", background=NAV, foreground=TXT, padding=[20, 10], font=("Arial", 11, "bold"))
        s.map("TNotebook.Tab", background=[("selected", B)], foreground=[("selected", "white")])
       
        # Header
        h = tk.Frame(self, bg=DB, height=60); h.pack(fill="x"); h.pack_propagate(0)
        tk.Label(h, text="  NOSTALgames", font=("Arial", 18, "bold"), bg=DB, fg="white").pack(side="left")
        self.w_lbl = tk.Label(h, text="", font=("Arial", 11, "bold"), bg=DB, fg=WALT); self.w_lbl.pack(side="right")

        self.nb = ttk.Notebook(self); self.nb.pack(fill="both", expand=1)
        self.tabs = {n: ttk.Frame(self.nb) for n in ["STORE", "LIBRARY", "SETTINGS"]}
        for n, f in self.tabs.items(): self.nb.add(f, text=f" {n} ")

        # Store UI
        sc = tk.Frame(self.tabs["STORE"], bg=B); sc.pack(side="left", fill="both", expand=1, padx=20, pady=20)
        self.canv = tk.Canvas(sc, bg=B, highlightthickness=0); self.canv.pack(side="left", fill="both", expand=1)
        self.list_f = tk.Frame(self.canv, bg=B); self.canv.create_window((0,0), window=self.list_f, anchor="nw", width=600)
        self.list_f.bind("<Configure>", lambda e: self.canv.configure(scrollregion=self.canv.bbox("all")))
       
        cf = tk.Frame(self.tabs["STORE"], bg=DB, width=300, padx=20, pady=20); cf.pack(side="right", fill="y"); cf.pack_propagate(0)
        tk.Label(cf, text="SHOPPING CART", bg=DB, fg=TXT, font=("Arial", 12, "bold")).pack(pady=10)
        self.lbx = tk.Listbox(cf, bg=B, fg=TXT, bd=0, font=("Arial", 10), selectbackground=NAV); self.lbx.pack(fill="both", expand=1)
       
        tk.Button(cf, text="REMOVE SELECTED", bg="#2a2a2a", fg=TXT, font=("Arial", 9, "bold"), relief="flat", pady=5, activebackground=RED, command=self.rem).pack(fill="x", pady=5)
        tk.Button(cf, text="PURCHASE", bg=PRCHS, fg="white", font=("Arial", 12, "bold"), relief="flat", pady=10, command=self.pay).pack(fill="x")

        # Settings UI
        dz = tk.LabelFrame(self.tabs["SETTINGS"], text=" Danger Zone ", bg=B, fg=RED, font=("Arial", 10, "bold"), padx=20, pady=20); dz.pack(fill="x", padx=50, pady=50)
        tk.Button(dz, text="RESET DATA", bg=RED, fg="white", font=("Arial", 10, "bold"), relief="flat", padx=20, command=self.reset).pack(side="right")
       
        self.refresh()

    def load_data(self):
        self.wallet, self.library = 10000.0, []
        if os.path.exists(self.file):
            with open(self.file, "r") as f:
                for line in f:
                    k, v = line.strip().split(":", 1)
                    if k == "wallet": self.wallet = float(v)
                    elif k == "library": self.library = [x.strip() for x in v.split(",") if x.strip()]

    def save_data(self):
        with open(self.file, "w") as f: f.write(f"wallet:{self.wallet}\nlibrary:{','.join(self.library)}")

    def refresh(self):
        self.w_lbl.config(text=f"WALLET: ₹{self.wallet}  ")
        for f in [self.list_f, self.tabs["LIBRARY"]]:
            for w in f.winfo_children(): w.destroy()
       
        for g, p in self.games.items():
            row = tk.Frame(self.list_f, bg=DB, pady=15, padx=20); row.pack(fill="x", pady=5)
            tk.Label(row, text=g, bg=DB, fg="white", font=("Arial", 13, "bold")).pack(side="left")
            if g in self.library: tk.Label(row, text="IN LIBRARY", bg=NAV, fg=TXT, font=("Arial", 9), padx=10).pack(side="right")
            else: tk.Button(row, text=f"₹{p}", bg=NAV, fg=LB, font=("Arial", 10, "bold"), relief="flat", width=12, command=lambda x=g: self.add(x)).pack(side="right")
       
        for g in self.library:
            r = tk.Frame(self.tabs["LIBRARY"], bg=DB, pady=10, padx=20); r.pack(fill="x", pady=2, padx=40)
            tk.Label(r, text=f"🎮 {g}", bg=DB, fg="white", font=("Arial", 12, "bold")).pack(side="left")

    def add(self, g):
        if g not in self.cart: self.cart.append(g); self.lbx.insert("end", f" {g}")

    def rem(self):
        s = self.lbx.curselection()
        if s: self.cart.pop(s[0]); self.lbx.delete(s[0])

    def pay(self):
        cost = sum(self.games[g] for g in self.cart)
        if self.cart and self.wallet >= cost:
            self.library.extend([g for g in self.cart if g not in self.library])
            self.wallet -= cost; self.save_data(); self.cart = []; self.lbx.delete(0, "end"); self.refresh(); messagebox.showinfo("OK", "Purchased!")
        elif self.cart: messagebox.showerror("Error", "Check funds or cart.")

    def reset(self):
        if messagebox.askyesno("Reset", "Wipe all data?"):
            if os.path.exists(self.file): os.remove(self.file)
            self.load_data(); self.cart = []; self.lbx.delete(0, "end"); self.refresh()

def reset(self):
        if messagebox.askyesno("Reset", "Wipe all data?"):
            if os.path.exists(self.file): os.remove(self.file)
            self.load_data(); self.cart = []; self.lbx.delete(0, "end"); self.refresh()

# --- PASTE EVERYTHING BELOW THIS LINE AT THE BOTTOM OF YOUR FILE ---

class NGext(NG):
    def __init__(self):
        super().__init__()
        self.add_wallet_controls()

    def add_wallet_controls(self):
        # Create a new frame in the Settings tab
        wm_frame = tk.LabelFrame(self.tabs["SETTINGS"], text=" Wallet Management ", bg="#1b2838", fg="#66c0f4", font=("Arial", 10, "bold"), padx=20, pady=20)
        # Pack it above the Danger Zone by placing it at the top
        wm_frame.pack(fill="x", padx=50, pady=(20, 0), before=self.tabs["SETTINGS"].winfo_children()[0])

        # Input variable for the amount
        self.amount_var = tk.DoubleVar(value=1000.0)
       
        # UI Elements
        tk.Label(wm_frame, text="Amount (₹):", bg="#1b2838", fg="white", font=("Arial", 10)).pack(side="left")
        tk.Entry(wm_frame, textvariable=self.amount_var, font=("Arial", 11), width=10).pack(side="left", padx=10)
       
        tk.Button(wm_frame, text="ADD", bg="#4c6b22", fg="white", font=("Arial", 9, "bold"), relief="flat", padx=10, command=self.add_money).pack(side="left", padx=5)
        tk.Button(wm_frame, text="REDUCE", bg="#a32a2a", fg="white", font=("Arial", 9, "bold"), relief="flat", padx=10, command=self.reduce_money).pack(side="left", padx=5)

    def add_money(self):
        try:
            addamount=abs(self.amount_var.get())
            if addamount>50000.0:
                messagebox.showerror("Limit Exceeded!"," You can only add upto ₹50000 at a time.")
                return
           
            self.wallet += addamount
            self.save_data()
            self.refresh()
        except tk.TclError:
            messagebox.showerror("Error", "Please enter a valid number.")

    def reduce_money(self):
        try:
            # Prevent wallet from going into negative numbers
            self.wallet = max(0.0, self.wallet - abs(self.amount_var.get()))
            self.save_data()
            self.refresh()
        except tk.TclError:
            messagebox.showerror("Error", "Please enter a valid number.")


if __name__ == "__main__":
    NGext().mainloop()
