"""
Contact Book - Flask Application
A premium contact management web application using Python, Flask, and SQLite.
"""

import sqlite3
import re
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ──────────────────────────────────────────────
# DATABASE SETUP
# ──────────────────────────────────────────────
DATABASE = "contacts.db"


def get_db():
    """Open a database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they do not exist."""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                name    TEXT    NOT NULL,
                phone   TEXT    NOT NULL,
                email   TEXT    DEFAULT '',
                address TEXT    DEFAULT '',
                company TEXT    DEFAULT '',
                notes   TEXT    DEFAULT '',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                favorite   INTEGER  DEFAULT 0
            )
        """)
        conn.commit()


# ──────────────────────────────────────────────
# VALIDATION HELPERS
# ──────────────────────────────────────────────
def validate_contact(name, phone, email):
    """Return a list of validation error strings, empty if valid."""
    errors = []

    # Name
    if not name or not name.strip():
        errors.append("Full name is required.")
    elif len(name.strip()) < 2:
        errors.append("Full name must be at least 2 characters.")

    # Phone
    if not phone or not phone.strip():
        errors.append("Phone number is required.")
    else:
        digits = re.sub(r"[\s\-\(\)\+]", "", phone)
        if not digits.isdigit():
            errors.append("Phone number must contain only digits, spaces, dashes, or parentheses.")
        elif len(digits) < 7 or len(digits) > 15:
            errors.append("Phone number must be between 7 and 15 digits.")

    # Email (optional but validated if provided)
    if email and email.strip():
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, email.strip()):
            errors.append("Please enter a valid email address.")

    return errors


# ──────────────────────────────────────────────
# ROUTES
# ──────────────────────────────────────────────

@app.route("/")
def index():
    """Home page — shows all contacts and summary statistics."""
    query = request.args.get("q", "").strip()
    conn = get_db()

    if query:
        contacts = conn.execute(
            """SELECT * FROM contacts
               WHERE name    LIKE ?
                  OR phone   LIKE ?
                  OR email   LIKE ?
               ORDER BY name COLLATE NOCASE""",
            (f"%{query}%", f"%{query}%", f"%{query}%")
        ).fetchall()
    else:
        contacts = conn.execute(
            "SELECT * FROM contacts ORDER BY name COLLATE NOCASE"
        ).fetchall()

    total     = conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
    favorites = conn.execute("SELECT COUNT(*) FROM contacts WHERE favorite=1").fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        contacts=contacts,
        query=query,
        total=total,
        favorites=favorites,
    )


@app.route("/add", methods=["GET", "POST"])
def add_contact():
    """Add a new contact."""
    if request.method == "POST":
        name    = request.form.get("name", "").strip()
        phone   = request.form.get("phone", "").strip()
        email   = request.form.get("email", "").strip()
        address = request.form.get("address", "").strip()
        company = request.form.get("company", "").strip()
        notes   = request.form.get("notes", "").strip()

        errors = validate_contact(name, phone, email)
        if errors:
            return jsonify({"success": False, "errors": errors}), 400

        with get_db() as conn:
            conn.execute(
                """INSERT INTO contacts (name, phone, email, address, company, notes)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (name, phone, email, address, company, notes)
            )
            conn.commit()

        return jsonify({"success": True, "message": "Contact added successfully!"})

    return render_template("index.html")


@app.route("/edit/<int:contact_id>", methods=["GET", "POST"])
def edit_contact(contact_id):
    """Edit an existing contact."""
    conn = get_db()
    contact = conn.execute(
        "SELECT * FROM contacts WHERE id = ?", (contact_id,)
    ).fetchone()
    conn.close()

    if not contact:
        return jsonify({"success": False, "errors": ["Contact not found."]}), 404

    if request.method == "GET":
        return jsonify({
            "id":      contact["id"],
            "name":    contact["name"],
            "phone":   contact["phone"],
            "email":   contact["email"],
            "address": contact["address"],
            "company": contact["company"],
            "notes":   contact["notes"],
        })

    if request.method == "POST":
        name    = request.form.get("name", "").strip()
        phone   = request.form.get("phone", "").strip()
        email   = request.form.get("email", "").strip()
        address = request.form.get("address", "").strip()
        company = request.form.get("company", "").strip()
        notes   = request.form.get("notes", "").strip()

        errors = validate_contact(name, phone, email)
        if errors:
            return jsonify({"success": False, "errors": errors}), 400

        with get_db() as conn:
            conn.execute(
                """UPDATE contacts
                   SET name=?, phone=?, email=?, address=?, company=?, notes=?
                   WHERE id=?""",
                (name, phone, email, address, company, notes, contact_id)
            )
            conn.commit()

        return jsonify({"success": True, "message": "Contact updated successfully!"})


@app.route("/delete/<int:contact_id>", methods=["POST"])
def delete_contact(contact_id):
    """Delete a single contact by ID."""
    conn = get_db()
    contact = conn.execute(
        "SELECT id FROM contacts WHERE id = ?", (contact_id,)
    ).fetchone()
    conn.close()

    if not contact:
        return jsonify({"success": False, "errors": ["Contact not found."]}), 404

    with get_db() as conn:
        conn.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        conn.commit()

    return jsonify({"success": True, "message": "Contact deleted successfully!"})


@app.route("/toggle_favorite/<int:contact_id>", methods=["POST"])
def toggle_favorite(contact_id):
    """Toggle the favorite flag for a contact."""
    conn = get_db()
    contact = conn.execute(
        "SELECT id, favorite FROM contacts WHERE id = ?", (contact_id,)
    ).fetchone()
    conn.close()

    if not contact:
        return jsonify({"success": False}), 404

    new_val = 0 if contact["favorite"] else 1
    with get_db() as conn:
        conn.execute(
            "UPDATE contacts SET favorite=? WHERE id=?", (new_val, contact_id)
        )
        conn.commit()

    return jsonify({"success": True, "favorite": new_val})


@app.route("/contacts/json")
def contacts_json():
    """Return contacts as JSON for live search/refresh."""
    query = request.args.get("q", "").strip()
    conn = get_db()

    if query:
        rows = conn.execute(
            """SELECT * FROM contacts
               WHERE name  LIKE ?
                  OR phone LIKE ?
                  OR email LIKE ?
               ORDER BY name COLLATE NOCASE""",
            (f"%{query}%", f"%{query}%", f"%{query}%")
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM contacts ORDER BY name COLLATE NOCASE"
        ).fetchall()

    conn.close()
    contacts = [dict(r) for r in rows]
    return jsonify(contacts)


# ──────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="127.0.0.1", port=5000)
