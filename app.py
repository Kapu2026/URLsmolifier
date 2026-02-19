from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import string
import random
import os

app = Flask(__name__)
DATABASE = "urls.db"

# Create database if it doesn't exist
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_url TEXT NOT NULL,
                short_code TEXT NOT NULL UNIQUE
            )
        ''')
init_db()

def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def insert_url(original_url, short_code):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute(
            "INSERT INTO urls (original_url, short_code) VALUES (?, ?)",
            (original_url, short_code)
        )

def get_original_url(short_code):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute(
            "SELECT original_url FROM urls WHERE short_code=?",
            (short_code,)
        )
        result = cursor.fetchone()
        return result[0] if result else None

@app.route("/", methods=["GET", "POST"])
def index():
    short_url = None

    if request.method == "POST":
        original_url = request.form.get("url")

        if original_url:
            short_code = generate_short_code()

            # Ensure unique short code
            while get_original_url(short_code):
                short_code = generate_short_code()

            insert_url(original_url, short_code)
            short_url = request.host_url + short_code

    return render_template("index.html", short_url=short_url)

@app.route("/<short_code>")
def redirect_url(short_code):
    original_url = get_original_url(short_code)
    if original_url:
        return redirect(original_url)
    return "URL not found", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)