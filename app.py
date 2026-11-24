import os
import sqlite3
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cricket-kit-secret-key-2026")

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cricket_kit.db")

# PostgreSQL configuration
PG_HOST = os.environ.get("PGHOST", "localhost")
PG_PORT = int(os.environ.get("PGPORT", 5432))
PG_USER = os.environ.get("PGUSER", "postgres")
PG_PASSWORD = os.environ.get("PGPASSWORD", "")
PG_DBNAME = os.environ.get("PGDATABASE", "cricket_db")
DATABASE_URL = os.environ.get("DATABASE_URL")

USE_POSTGRES = False

def check_postgres_availability():
    global USE_POSTGRES
    try:
        import psycopg2
        if DATABASE_URL:
            conn = psycopg2.connect(DATABASE_URL, connect_timeout=3)
            conn.close()
            USE_POSTGRES = True
            print("Connected to PostgreSQL via DATABASE_URL.")
            return True
        elif PG_PASSWORD:
            conn = psycopg2.connect(
                host=PG_HOST,
                port=PG_PORT,
                user=PG_USER,
                password=PG_PASSWORD,
                dbname=PG_DBNAME,
                connect_timeout=3
            )
            conn.close()
            USE_POSTGRES = True
            print(f"Connected to PostgreSQL database '{PG_DBNAME}' on {PG_HOST}:{PG_PORT}.")
            return True
    except Exception as e:
        print(f"PostgreSQL connection note: {e}")
        print("Using local SQLite database (cricket_kit.db) as active storage.")
    
    USE_POSTGRES = False
    return False

check_postgres_availability()

def get_db_connection():
    if USE_POSTGRES:
        import psycopg2
        if DATABASE_URL:
            return psycopg2.connect(DATABASE_URL)
        else:
            return psycopg2.connect(
                host=PG_HOST,
                port=PG_PORT,
                user=PG_USER,
                password=PG_PASSWORD,
                dbname=PG_DBNAME
            )
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    if USE_POSTGRES:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(15)
            );
            CREATE TABLE IF NOT EXISTS equipment (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                quantity INT NOT NULL,
                available INT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS borrowing (
                id SERIAL PRIMARY KEY,
                player_id INT REFERENCES players(id) ON DELETE CASCADE,
                equipment_id INT REFERENCES equipment(id) ON DELETE CASCADE,
                quantity INT NOT NULL,
                issue_date DATE DEFAULT CURRENT_DATE,
                status VARCHAR(20) DEFAULT 'Borrowed'
            );
        """)
        cursor.execute("SELECT COUNT(*) FROM equipment;")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute("""
                INSERT INTO equipment (name, quantity, available) VALUES
                ('Cricket Bat', 15, 15),
                ('Helmet', 20, 20),
                ('Pads', 12, 12),
                ('Practice Balls', 30, 30),
                ('Gloves', 15, 15);
            """)
        cursor.execute("SELECT COUNT(*) FROM players;")
        pcount = cursor.fetchone()[0]
        if pcount == 0:
            cursor.execute("""
                INSERT INTO players (name, phone) VALUES
                ('Virat Kohli', '9876543210'),
                ('Rohit Sharma', '9876543211'),
                ('MS Dhoni', '9876543212');
            """)
        conn.commit()
    else:
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT
            );
            CREATE TABLE IF NOT EXISTS equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                available INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS borrowing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER REFERENCES players(id) ON DELETE CASCADE,
                equipment_id INTEGER REFERENCES equipment(id) ON DELETE CASCADE,
                quantity INTEGER NOT NULL,
                issue_date TEXT DEFAULT (DATE('now')),
                status TEXT DEFAULT 'Borrowed'
            );
        """)
        cursor.execute("SELECT COUNT(*) FROM equipment;")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.executemany(
                "INSERT INTO equipment (name, quantity, available) VALUES (?, ?, ?);",
                [
                    ("Cricket Bat", 15, 15),
                    ("Helmet", 20, 20),
                    ("Pads", 12, 12),
                    ("Practice Balls", 30, 30),
                    ("Gloves", 15, 15),
                ]
            )
            cursor.execute("SELECT COUNT(*) FROM players;")
            player_count = cursor.fetchone()[0]
            if player_count == 0:
                cursor.executemany(
                    "INSERT INTO players (name, phone) VALUES (?, ?);",
                    [
                        ("Virat Kohli", "9876543210"),
                        ("Rohit Sharma", "9876543211"),
                        ("MS Dhoni", "9876543212"),
                    ]
                )
        conn.commit()

    conn.close()


@app.route("/")
def index():
    conn = get_db_connection()
    cursor = conn.cursor()

    if USE_POSTGRES:
        cursor.execute("SELECT id, name, quantity, available FROM equipment ORDER BY id ASC;")
        equipment_cols = [desc[0] for desc in cursor.description]
        equipment = [dict(zip(equipment_cols, row)) for row in cursor.fetchall()]

        cursor.execute("SELECT id, name, phone FROM players ORDER BY name ASC;")
        players_cols = [desc[0] for desc in cursor.description]
        players = [dict(zip(players_cols, row)) for row in cursor.fetchall()]

        cursor.execute("""
            SELECT b.id, p.name AS player_name, e.name AS equipment_name, 
                   b.quantity, b.issue_date, b.status, b.equipment_id
            FROM borrowing b
            JOIN players p ON b.player_id = p.id
            JOIN equipment e ON b.equipment_id = e.id
            ORDER BY b.id DESC;
        """)
        borrowing_cols = [desc[0] for desc in cursor.description]
        borrowings = [dict(zip(borrowing_cols, row)) for row in cursor.fetchall()]
    else:
        cursor.execute("SELECT id, name, quantity, available FROM equipment ORDER BY id ASC;")
        equipment = [dict(row) for row in cursor.fetchall()]

        cursor.execute("SELECT id, name, phone FROM players ORDER BY name ASC;")
        players = [dict(row) for row in cursor.fetchall()]

        cursor.execute("""
            SELECT b.id, p.name AS player_name, e.name AS equipment_name, 
                   b.quantity, b.issue_date, b.status, b.equipment_id
            FROM borrowing b
            JOIN players p ON b.player_id = p.id
            JOIN equipment e ON b.equipment_id = e.id
            ORDER BY b.id DESC;
        """)
        borrowings = [dict(row) for row in cursor.fetchall()]

    conn.close()

    total_items = sum(item["quantity"] for item in equipment)
    available_items = sum(item["available"] for item in equipment)
    borrowed_items = sum(b["quantity"] for b in borrowings if b["status"] == "Borrowed")

    stats = {
        "total_types": len(equipment),
        "total_items": total_items,
        "available_items": available_items,
        "borrowed_items": borrowed_items,
        "total_players": len(players),
    }

    return render_template(
        "index.html",
        equipment=equipment,
        players=players,
        borrowings=borrowings,
        stats=stats
    )


@app.route("/add_player", methods=["POST"])
def add_player():
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()

    if not name:
        flash("Player name is required!", "danger")
        return redirect(url_for("index"))

    conn = get_db_connection()
    cursor = conn.cursor()

    if USE_POSTGRES:
        cursor.execute("INSERT INTO players (name, phone) VALUES (%s, %s);", (name, phone))
    else:
        cursor.execute("INSERT INTO players (name, phone) VALUES (?, ?);", (name, phone))

    conn.commit()
    conn.close()
    flash(f"Player '{name}' added successfully!", "success")
    return redirect(url_for("index"))


@app.route("/add_equipment", methods=["POST"])
def add_equipment():
    name = request.form.get("name", "").strip()
    try:
        quantity = int(request.form.get("quantity", 0))
    except ValueError:
        quantity = 0

    if not name or quantity <= 0:
        flash("Please provide a valid equipment name and quantity greater than zero!", "danger")
        return redirect(url_for("index"))

    conn = get_db_connection()
    cursor = conn.cursor()

    if USE_POSTGRES:
        cursor.execute(
            "INSERT INTO equipment (name, quantity, available) VALUES (%s, %s, %s);",
            (name, quantity, quantity)
        )
    else:
        cursor.execute(
            "INSERT INTO equipment (name, quantity, available) VALUES (?, ?, ?);",
            (name, quantity, quantity)
        )

    conn.commit()
    conn.close()
    flash(f"Equipment '{name}' ({quantity} items) added successfully!", "success")
    return redirect(url_for("index"))


@app.route("/borrow", methods=["POST"])
def borrow():
    try:
        player_id = int(request.form.get("player_id", 0))
        equipment_id = int(request.form.get("equipment_id", 0))
        quantity = int(request.form.get("quantity", 0))
    except ValueError:
        flash("Invalid input values for borrowing!", "danger")
        return redirect(url_for("index"))

    if player_id <= 0 or equipment_id <= 0 or quantity <= 0:
        flash("Please select a player, equipment, and a valid quantity!", "danger")
        return redirect(url_for("index"))

    conn = get_db_connection()
    cursor = conn.cursor()

    if USE_POSTGRES:
        cursor.execute("SELECT id, name, available FROM equipment WHERE id = %s;", (equipment_id,))
        eq_row = cursor.fetchone()
        if not eq_row:
            conn.close()
            flash("Selected equipment not found!", "danger")
            return redirect(url_for("index"))
        eq_name = eq_row[1]
        available = eq_row[2]

        if available < quantity:
            conn.close()
            flash(f"Not enough '{eq_name}' in stock! Only {available} available.", "danger")
            return redirect(url_for("index"))

        cursor.execute(
            "INSERT INTO borrowing (player_id, equipment_id, quantity, status) VALUES (%s, %s, %s, 'Borrowed');",
            (player_id, equipment_id, quantity)
        )
        cursor.execute(
            "UPDATE equipment SET available = available - %s WHERE id = %s;",
            (quantity, equipment_id)
        )
    else:
        cursor.execute("SELECT id, name, available FROM equipment WHERE id = ?;", (equipment_id,))
        eq_row = cursor.fetchone()
        if not eq_row:
            conn.close()
            flash("Selected equipment not found!", "danger")
            return redirect(url_for("index"))
        eq_name = eq_row["name"]
        available = eq_row["available"]

        if available < quantity:
            conn.close()
            flash(f"Not enough '{eq_name}' in stock! Only {available} available.", "danger")
            return redirect(url_for("index"))

        cursor.execute(
            "INSERT INTO borrowing (player_id, equipment_id, quantity, status) VALUES (?, ?, ?, 'Borrowed');",
            (player_id, equipment_id, quantity)
        )
        cursor.execute(
            "UPDATE equipment SET available = available - ? WHERE id = ?;",
            (quantity, equipment_id)
        )

    conn.commit()
    conn.close()
    flash(f"Successfully issued {quantity}x {eq_name}!", "success")
    return redirect(url_for("index"))


@app.route("/return_kit/<int:borrow_id>", methods=["POST"])
def return_kit(borrow_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if USE_POSTGRES:
        cursor.execute("SELECT id, equipment_id, quantity, status FROM borrowing WHERE id = %s;", (borrow_id,))
        row = cursor.fetchone()
        if not row or row[3] != "Borrowed":
            conn.close()
            flash("Record not found or already returned!", "danger")
            return redirect(url_for("index"))

        equipment_id = row[1]
        quantity = row[2]

        cursor.execute("UPDATE borrowing SET status = 'Returned' WHERE id = %s;", (borrow_id,))
        cursor.execute("UPDATE equipment SET available = available + %s WHERE id = %s;", (quantity, equipment_id))
    else:
        cursor.execute("SELECT id, equipment_id, quantity, status FROM borrowing WHERE id = ?;", (borrow_id,))
        row = cursor.fetchone()
        if not row or row["status"] != "Borrowed":
            conn.close()
            flash("Record not found or already returned!", "danger")
            return redirect(url_for("index"))

        equipment_id = row["equipment_id"]
        quantity = row["quantity"]

        cursor.execute("UPDATE borrowing SET status = 'Returned' WHERE id = ?;", (borrow_id,))
        cursor.execute("UPDATE equipment SET available = available + ? WHERE id = ?;", (quantity, equipment_id))

    conn.commit()
    conn.close()
    flash(f"Equipment returned successfully ({quantity} item(s) restored to inventory)!", "success")
    return redirect(url_for("index"))


init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Cricket Kit Management System on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
