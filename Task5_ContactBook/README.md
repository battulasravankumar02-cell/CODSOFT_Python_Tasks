# Contact Book

A premium, modern **Python/Flask** contact management application with persistent SQLite storage, dark/light mode, live search, and a responsive design that works beautifully on mobile, tablet, and desktop.

---

## Features

| Feature | Details |
|---|---|
| ➕ Add Contact | Name, phone, email, address, company, notes |
| 👁️ View Contacts | Card-based responsive grid layout |
| 🔍 Search Contacts | Live search by name, phone, or email |
| ✏️ Edit Contact | Pre-filled form, updates existing record |
| 🗑️ Delete Contact | Confirmation dialog before permanent removal |
| ⭐ Favourites | Toggle favourite flag per contact |
| 💾 Persistent Storage | SQLite database — data survives restarts |
| 🌙 Dark Mode | Premium dark aesthetic (default) |
| ☀️ Light Mode | Clean professional light theme |
| 📱 Responsive | Works on 360 px phones, tablets, and desktops |
| ✅ Validation | Server-side + friendly error messages |

---

## Technology Stack

- **Python 3.10+**
- **Flask 3.x**
- **SQLite** (via Python's built-in `sqlite3`)
- **HTML5 + CSS3** (Vanilla CSS, Glassmorphism, Custom Properties)
- **Vanilla JavaScript** (No framework dependencies)
- **Google Fonts** — Inter

---

## Project Structure

```
contact book/
│
├── app.py              ← Flask application (routes, validation, DB)
├── requirements.txt    ← Python dependencies
├── contacts.db         ← SQLite database (auto-created on first run)
├── README.md
│
├── templates/
│   └── index.html      ← Main HTML template (Jinja2)
│
└── static/
    ├── style.css       ← Premium stylesheet
    └── script.js       ← Frontend logic (search, modals, theme)
```

---

## Getting Started

### 1 — Prerequisites

Make sure you have **Python 3.10 or newer** installed.

```
python --version
```

### 2 — Navigate to the project folder

```
cd "contact book"
```

### 3 — (Optional) Create a virtual environment

```
python -m venv venv
venv\Scripts\activate      # Windows
# or
source venv/bin/activate   # macOS / Linux
```

### 4 — Install dependencies

```
pip install -r requirements.txt
```

### 5 — Run the application

```
python app.py
```

### 6 — Open in browser

```
http://127.0.0.1:5000
```

The **SQLite database** (`contacts.db`) is created automatically on first launch. No setup required.

---

## Usage

1. Click **Add Contact** to open the form.
2. Fill in Name and Phone (required), then optionally Email, Address, Company, Notes.
3. Click **Save Contact**.
4. Use the **Search** box to find contacts by name, phone, or email.
5. Click **Edit** on any card to modify a contact.
6. Click **Delete** and confirm to remove a contact.
7. Click the ⭐ star on any card to mark it as a favourite.
8. Click the moon/sun icon in the header to switch between Dark and Light mode.

---

## Notes

- No mock/sample data is inserted at startup. The app starts empty.
- The database file `contacts.db` is created automatically in the project folder.
- Theme preference is saved in `localStorage` and persists across sessions.
- The application uses parameterized SQL queries to prevent SQL injection.
