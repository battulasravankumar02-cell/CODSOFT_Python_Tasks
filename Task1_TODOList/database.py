"""
Database Module for CODSOFT Task 1 — To-Do List Application
Handles all SQLite database connections, initialization, and CRUD operations.
"""

import sqlite3
import os
from datetime import datetime

# Define database file path in the 'instance' folder
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
DB_PATH = os.path.join(INSTANCE_DIR, 'tasks.db')


def get_db_connection():
    """
    Establish and return a connection to the SQLite database.
    sqlite3.Row allows accessing columns both by name (dictionary style) and index.
    """
    # Ensure the instance directory exists
    if not os.path.exists(INSTANCE_DIR):
        os.makedirs(INSTANCE_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initialize the database table if it doesn't exist already.
    Creates the 'tasks' table with appropriate columns and constraints.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            priority TEXT DEFAULT 'MEDIUM',
            due_date TEXT DEFAULT '',
            completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


def get_all_tasks(filter_status='ALL', search_query=''):
    """
    Retrieve tasks from database with optional status filtering and search query.
    
    Args:
        filter_status (str): 'ALL', 'PENDING', or 'COMPLETED'
        search_query (str): Optional search string to match title or description
        
    Returns:
        list[dict]: List of task records converted to dictionaries
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    # Filter by completion status
    if filter_status == 'PENDING':
        query += " AND completed = 0"
    elif filter_status == 'COMPLETED':
        query += " AND completed = 1"

    # Search filter (case-insensitive in SQLite for ASCII LIKE)
    if search_query and search_query.strip():
        query += " AND (title LIKE ? OR description LIKE ?)"
        like_pattern = f"%{search_query.strip()}%"
        params.extend([like_pattern, like_pattern])

    # Ordering: Pending tasks first, then by priority (HIGH > MEDIUM > LOW), then by id DESC
    query += """
        ORDER BY 
            completed ASC,
            CASE priority 
                WHEN 'HIGH' THEN 1 
                WHEN 'MEDIUM' THEN 2 
                WHEN 'LOW' THEN 3 
                ELSE 4 
            END ASC,
            id DESC
    """

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_task_by_id(task_id):
    """
    Fetch a single task by its primary key ID.
    
    Args:
        task_id (int): Primary key ID of the task
        
    Returns:
        dict or None: Task data if found, None otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def add_task(title, description='', priority='MEDIUM', due_date=''):
    """
    Insert a new task into the database.
    
    Args:
        title (str): Title of the task (Required)
        description (str): Optional details
        priority (str): 'LOW', 'MEDIUM', or 'HIGH'
        due_date (str): Date string in YYYY-MM-DD format
        
    Returns:
        int: The ID of the newly created task
    """
    # Clean and sanitize input
    title = title.strip()
    description = description.strip() if description else ''
    priority = priority.upper().strip() if priority else 'MEDIUM'
    if priority not in ('LOW', 'MEDIUM', 'HIGH'):
        priority = 'MEDIUM'
    due_date = due_date.strip() if due_date else ''

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO tasks (title, description, priority, due_date, completed)
        VALUES (?, ?, ?, ?, 0)
        ''',
        (title, description, priority, due_date)
    )
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return task_id


def update_task(task_id, title, description='', priority='MEDIUM', due_date=''):
    """
    Update an existing task in the database.
    
    Args:
        task_id (int): ID of the task to update
        title (str): New title
        description (str): New description
        priority (str): New priority
        due_date (str): New due date
        
    Returns:
        bool: True if updated, False if task not found
    """
    title = title.strip()
    description = description.strip() if description else ''
    priority = priority.upper().strip() if priority else 'MEDIUM'
    if priority not in ('LOW', 'MEDIUM', 'HIGH'):
        priority = 'MEDIUM'
    due_date = due_date.strip() if due_date else ''

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        UPDATE tasks
        SET title = ?, description = ?, priority = ?, due_date = ?
        WHERE id = ?
        ''',
        (title, description, priority, due_date, task_id)
    )
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()

    return rows_affected > 0


def toggle_task_completion(task_id):
    """
    Toggle the completed status (0 -> 1 or 1 -> 0) of a task.
    Updates completed_at timestamp when marked complete.
    
    Args:
        task_id (int): ID of the task
        
    Returns:
        dict or None: Updated task dictionary if found, None otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT completed FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    current_status = row['completed']
    new_status = 1 if current_status == 0 else 0
    completed_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S') if new_status == 1 else None

    cursor.execute(
        '''
        UPDATE tasks
        SET completed = ?, completed_at = ?
        WHERE id = ?
        ''',
        (new_status, completed_at, task_id)
    )
    conn.commit()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    updated_row = cursor.fetchone()
    conn.close()

    return dict(updated_row) if updated_row else None


def delete_task(task_id):
    """
    Delete a task by ID.
    
    Args:
        task_id (int): Primary key ID of the task
        
    Returns:
        bool: True if task was deleted, False if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()

    return rows_affected > 0


def get_task_statistics():
    """
    Calculate and return overall task statistics (total, completed, pending, completion percentage).
    
    Returns:
        dict: Statistics summary
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM tasks")
    total = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as completed FROM tasks WHERE completed = 1")
    completed = cursor.fetchone()['completed']

    pending = total - completed
    percent = round((completed / total * 100), 1) if total > 0 else 0

    conn.close()

    return {
        'total': total,
        'completed': completed,
        'pending': pending,
        'percent': percent
    }
