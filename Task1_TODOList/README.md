# To-Do List

A modern, ultra-premium, full-stack Python To-Do List web application built with **Python**, **Flask**, and **SQLite**. Designed for high productivity and task management with real-time statistics, search, filtering, and responsive UI.

---

## CODSOFT Internship
**Task 1 — To-Do List Application**  
*CODSOFT Python Programming Internship*

> "A To-Do List application is a useful project that helps users manage and organize their tasks efficiently. This project aims to create a command-line or GUI-based application using Python, allowing users to create, update, and track their to-do lists."

---

## Project Description

This project provides an intuitive and luxurious dashboard to create, update, organize, and track daily tasks. Built with Python as the primary backend engine, it uses a lightweight SQLite database for persistence, and a sleek, modern glassmorphic dark interface optimized for desktop, tablet, and mobile viewports.

---

## Key Features

- 📝 **Create Tasks**: Add new tasks with title (required), detailed description, priority levels (Low, Medium, High), and due dates.
- ✏️ **Update Tasks**: Edit any existing task details seamlessly with a modal editor.
- 🎯 **Track Tasks & Completion**: Toggle completion with custom checkmarks, visual strikethrough, and completion timestamps.
- 🗑️ **Delete Tasks with Confirmation**: Protect against accidental deletion with a clean confirmation modal.
- 📊 **Dynamic Statistics Dashboard**: Real-time counters for **Total**, **Completed**, and **Pending** tasks along with a live progress percentage bar.
- 🔍 **Instant Search & Filters**: Search tasks in real-time and filter by **All**, **Pending**, or **Completed**.
- 💾 **SQLite Persistence**: Automatically saves data locally in `instance/tasks.db` so tasks remain saved even after refreshing or restarting the application.
- 📱 **Fully Responsive Design**: Fluid layout tailored for mobile devices (360px–430px), tablets (768px), and desktops (960px–1920px).
- 🎨 **Ultra-Premium UI**: Glassmorphism, subtle gradients, smooth animations, and clear visual hierarchy.

---

## Technologies Used

| Technology | Purpose |
| :--- | :--- |
| **Python 3.x** | Core backend logic, routing, validation, and database operations |
| **Flask** | Lightweight and extensible Python Web Framework |
| **SQLite3** | Embedded relational database for zero-configuration data persistence |
| **HTML5 & CSS3** | Semantic structure, CSS variables, glassmorphism, responsive grid & flexbox |
| **JavaScript (Vanilla)** | Dynamic UI interactions, modal controls, real-time search, and asynchronous requests |
| **RemixIcon** | Crisp, professional icons |

---

## Python Concepts Demonstrated

1. **Functions & Modular Architecture**: Separation of concerns across `app.py` (routing/HTTP) and `database.py` (data access/SQL).
2. **Database Management with SQLite**:
   - Connection management and `sqlite3.Row` row-factory for dictionary-style data mapping.
   - Parameterized queries (`?`) to prevent SQL injection vulnerabilities.
   - Table initialization, schema constraints, and primary keys.
3. **Data Structures**: Lists, Dictionaries, and Tuples used for task transformation and statistical calculations.
4. **Input Validation & Sanitization**: Handling required fields, sanitizing strings, setting default priorities, and preventing empty submissions.
5. **Conditional Logic & Loops**: Dynamic SQL query construction, status checks, and template rendering.
6. **Exception & Error Handling**: `try...except` blocks around database operations, returning informative user notifications and safe status codes.
7. **RESTful Routing & HTTP Methods**: Utilizing `GET` and `POST` request handling with both HTML and JSON responses.

---

## Project Structure

```text
todo_list/
│
├── app.py                  # Main Flask application and route handlers
├── database.py             # SQLite helper functions and CRUD database layer
├── requirements.txt        # Python package dependencies
├── .gitignore              # Files and directories ignored by Git
├── README.md               # Project documentation
│
├── instance/
│   └── tasks.db            # Local SQLite database file (auto-generated)
│
├── templates/
│   ├── base.html           # Base layout, meta tags, fonts, ambient glow
│   └── index.html          # Main dashboard, stats, filters, task list, modals
│
└── static/
    ├── css/
    │   └── style.css       # Ultra-premium dark theme styling & responsive rules
    └── js/
        └── script.js       # Asynchronous API fetch, modal controls, live search
```

---

## How to Install

### Prerequisites
- Python 3.8 or higher installed on your system.

### Step-by-step Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd todo_list
   ```

2. **(Optional) Create and activate a virtual environment**:
   - On Windows:
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## How to Run

1. **Start the Flask server**:
   ```bash
   python app.py
   ```

2. **Open in your browser**:
   Navigate to:
   ```text
   http://127.0.0.1:5000
   ```

---

## How It Works

1. **Initialization**: When `app.py` runs, `database.init_db()` ensures the `tasks` table exists in `instance/tasks.db`.
2. **Displaying Tasks**: The home route (`/`) queries SQLite via `database.get_all_tasks()` and renders `templates/index.html` with active filters and calculated progress metrics.
3. **Adding a Task**: Submitting the "+ Add Task" modal sends a `POST` request to `/add`. Python validates the title and inserts the record into SQLite.
4. **Updating a Task**: Clicking "Edit" retrieves current task details from `/api/tasks/<id>` and populates the edit modal. Submitting sends a `POST` request to `/update/<id>`.
5. **Tracking & Completing**: Clicking the checkmark sends a `POST` request to `/toggle/<id>`. Python switches the `completed` status between `0` and `1`, and updates statistics immediately.
6. **Deleting a Task**: Clicking "Delete" opens a confirmation dialog. Upon confirmation, a `POST` request to `/delete/<id>` removes the record from the database.

---

## Future Improvements

- User authentication (multi-user support with hashed passwords).
- Task category tagging and subtasks checklist.
- Due date reminder notifications.
- Export task history as PDF / CSV.

---

## Author & Acknowledgments

- **Internship**: CODSOFT Python Programming Internship
- **Task**: Task 1 — To-Do List Application
