import configparser
import hashlib
import mysql.connector

CONFIG_FILE = "db_config.ini"
START_WALLET = 10000.0
DEFAULT_GAMES = {"Cyberpunk 2077": 2999, "Elden Ring": 3500, "Stardew Valley": 479, "Hollow Knight": 600, "Doom Eternal": 1799, "Forza Horizon 5": 3499, "Forza Horizon 6": 4599, "Counter Strike 2": 1399, "Subnautica 2": 1799, "NBA 2K26": 3999, "Red Dead Redemption 2": 4999, "FC™ 26": 1625}

TABLES = [
    """CREATE TABLE IF NOT EXISTS users (
        username VARCHAR(30) PRIMARY KEY,
        password CHAR(64) NOT NULL,
        role ENUM('user', 'admin') NOT NULL DEFAULT 'user',
        wallet DECIMAL(10, 2) NOT NULL DEFAULT 10000)""",
    """CREATE TABLE IF NOT EXISTS games (
        name VARCHAR(60) PRIMARY KEY,
        price INT NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS purchases (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(30) NOT NULL,
        game VARCHAR(60) NOT NULL,
        price INT NOT NULL,
        bought_on DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (username, game),
        FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE)""",
]


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


class Database:
    """Python-MySQL connectivity: connect(), cursor(), execute(), fetchall(), commit()."""

    def __init__(self, config_file=CONFIG_FILE):
        cfg = configparser.ConfigParser()
        if not cfg.read(config_file):
            raise FileNotFoundError(f"{config_file} not found. Copy db_config.example.ini to {config_file} and fill in your MySQL details.")
        m = cfg["mysql"]
        name = m.get("database", "nostalgames")
        if not name.isidentifier():
            raise ValueError(f"Invalid database name: {name}")

        self.con = mysql.connector.connect(host=m.get("host", "localhost"), port=m.getint("port", 3306), user=m["user"], password=m.get("password", ""))
        self.cur = self.con.cursor()
        self.cur.execute(f"CREATE DATABASE IF NOT EXISTS {name} CHARACTER SET utf8mb4")
        self.cur.execute(f"USE {name}")
        for sql in TABLES:
            self.cur.execute(sql)

        self.users, self.games, self.purchases = UserTable(self), GameTable(self), PurchaseTable(self)
        self.games.seed()
        self.users.seed_admin(cfg.get("app", "admin_password", fallback="admin123"))

    def fetchall(self, sql, params=()):
        self.cur.execute(sql, params)
        return self.cur.fetchall()

    def fetchone(self, sql, params=()):
        self.cur.execute(sql, params)
        return self.cur.fetchone()

    def run(self, *statements):
        """Execute (sql, params) pairs as one transaction: all succeed or none do."""
        try:
            for sql, params in statements:
                self.cur.execute(sql, params)
            self.con.commit()
        except mysql.connector.Error:
            self.con.rollback()
            raise

    def close(self):
        self.cur.close(); self.con.close()


class UserTable:
    def __init__(self, db):
        self.db = db

    def seed_admin(self, password):
        if not self.db.fetchone("SELECT username FROM users WHERE role = 'admin'"):
            self.db.run(("INSERT INTO users (username, password, role) VALUES (%s, %s, 'admin')", ("admin", hash_password(password))))

    def login(self, username, password):
        """Return the role ('user'/'admin') if the credentials match, else None."""
        row = self.db.fetchone("SELECT role FROM users WHERE username = %s AND password = %s", (username, hash_password(password)))
        return row[0] if row else None

    def register(self, username, password):
        try:
            self.db.run(("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hash_password(password))))
            return True
        except mysql.connector.IntegrityError:
            return False

    def wallet(self, username):
        return float(self.db.fetchone("SELECT wallet FROM users WHERE username = %s", (username,))[0])

    def set_wallet(self, username, amount):
        self.db.run(("UPDATE users SET wallet = %s WHERE username = %s", (amount, username)))

    def reset(self, username):
        self.db.run(("DELETE FROM purchases WHERE username = %s", (username,)),
                    ("UPDATE users SET wallet = %s WHERE username = %s", (START_WALLET, username)))

    def delete(self, username):
        self.db.run(("DELETE FROM users WHERE username = %s AND role = 'user'", (username,)))

    def all(self):
        return self.db.fetchall("""SELECT u.username, u.role, u.wallet, COUNT(p.id)
                                   FROM users u LEFT JOIN purchases p ON p.username = u.username
                                   GROUP BY u.username, u.role, u.wallet ORDER BY u.role, u.username""")


class GameTable:
    def __init__(self, db):
        self.db = db

    def seed(self):
        if not self.db.fetchone("SELECT COUNT(*) FROM games")[0]:
            self.db.run(*[("INSERT INTO games (name, price) VALUES (%s, %s)", (n, p)) for n, p in DEFAULT_GAMES.items()])

    def all(self):
        """Games in the original store order; any extra games added in MySQL come after, A-Z."""
        order = list(DEFAULT_GAMES)
        rows = sorted(self.db.fetchall("SELECT name, price FROM games"), key=lambda r: (order.index(r[0]) if r[0] in order else len(order), r[0]))
        return dict(rows)

    def save(self, name, price):
        self.db.run(("INSERT INTO games (name, price) VALUES (%s, %s) ON DUPLICATE KEY UPDATE price = %s", (name, price, price)))

    def delete(self, name):
        self.db.run(("DELETE FROM games WHERE name = %s", (name,)))


class PurchaseTable:
    def __init__(self, db):
        self.db = db

    def library(self, username):
        return [r[0] for r in self.db.fetchall("SELECT game FROM purchases WHERE username = %s ORDER BY bought_on", (username,))]

    def buy(self, username, items, new_wallet):
        """items: {game: price}. Records every purchase and the new wallet in one transaction."""
        self.db.run(*[("INSERT INTO purchases (username, game, price) VALUES (%s, %s, %s)", (username, g, p)) for g, p in items.items()],
                    ("UPDATE users SET wallet = %s WHERE username = %s", (new_wallet, username)))

    def all(self):
        return self.db.fetchall("SELECT username, game, price, bought_on FROM purchases ORDER BY bought_on DESC")
