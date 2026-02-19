import os
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import string
import random

app = Flask(__name__)

# PostgreSQL database URL from Render
DATABASE_URL = os.environ.get("DATABASE_URL")

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Database model for URLs
class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(2048), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)


# Initialize database tables
with app.app_context():
    db.create_all()


# Generate random short code
def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


@app.route("/", methods=["GET", "POST"])
def index():
    short_url = None

    if request.method == "POST":
        original_url = request.form.get("url")
        if original_url:
            short_code = generate_short_code()

            # Ensure unique short code
            while URL.query.filter_by(short_code=short_code).first():
                short_code = generate_short_code()

            new_entry = URL(original_url=original_url, short_code=short_code)
            db.session.add(new_entry)
            db.session.commit()

            short_url = request.host_url + short_code

    return render_template("index.html", short_url=short_url)


@app.route("/<short_code>")
def redirect_url(short_code):
    url_entry = URL.query.filter_by(short_code=short_code).first()
    if url_entry:
        return redirect(url_entry.original_url)
    else:
        return "URL not found", 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
