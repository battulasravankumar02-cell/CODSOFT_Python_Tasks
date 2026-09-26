"""
Flask Application for CODSOFT Task 1 — To-Do List Application
Handles routes, validation, templates, and RESTful API endpoints.
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import database

# Initialize Flask App
app = Flask(__name__)
# Secret key for secure session handling and flash messages
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'codsoft-todo-super-secret-key-2026')

# Initialize SQLite database tables on startup
with app.app_context():
    database.init_db()


@app.route('/', methods=['GET'])
def index():
    """
    Home page dashboard route.
    Fetches filtered tasks, search query, and task statistics.
    """
    filter_status = request.args.get('filter', 'ALL').upper()
    if filter_status not in ('ALL', 'PENDING', 'COMPLETED'):
        filter_status = 'ALL'

    search_query = request.args.get('search', '').strip()

    tasks = database.get_all_tasks(filter_status=filter_status, search_query=search_query)
    stats = database.get_task_statistics()

    return render_template(
        'index.html',
        tasks=tasks,
        stats=stats,
        current_filter=filter_status,
        search_query=search_query
    )


@app.route('/add', methods=['POST'])
def add_task_route():
    """
    Add a new task route.
    Supports both traditional Form POST and AJAX/JSON requests.
    """
    is_json = request.is_json
    data = request.get_json() if is_json else request.form

    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    priority = data.get('priority', 'MEDIUM').upper().strip()
    due_date = data.get('due_date', '').strip()

    # Input Validation
    if not title:
        error_msg = "Please enter a task title."
        if is_json:
            return jsonify({'success': False, 'message': error_msg}), 400
        flash(error_msg, 'danger')
        return redirect(url_for('index'))

    if priority not in ('LOW', 'MEDIUM', 'HIGH'):
        priority = 'MEDIUM'

    try:
        task_id = database.add_task(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date
        )
        success_msg = f'Task "{title}" created successfully!'
        stats = database.get_task_statistics()
        new_task = database.get_task_by_id(task_id)

        if is_json:
            return jsonify({
                'success': True,
                'message': success_msg,
                'task': new_task,
                'stats': stats
            }), 201

        flash(success_msg, 'success')
        return redirect(url_for('index'))

    except Exception as e:
        error_msg = "A database error occurred while saving the task."
        if is_json:
            return jsonify({'success': False, 'message': error_msg}), 500
        flash(error_msg, 'danger')
        return redirect(url_for('index'))


@app.route('/update/<int:task_id>', methods=['POST'])
def update_task_route(task_id):
    """
    Update an existing task route.
    """
    is_json = request.is_json
    data = request.get_json() if is_json else request.form

    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    priority = data.get('priority', 'MEDIUM').upper().strip()
    due_date = data.get('due_date', '').strip()

    if not title:
        error_msg = "Task title cannot be empty."
        if is_json:
            return jsonify({'success': False, 'message': error_msg}), 400
        flash(error_msg, 'danger')
        return redirect(url_for('index'))

    try:
        updated = database.update_task(
            task_id=task_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date
        )

        if not updated:
            error_msg = "Task not found or could not be updated."
            if is_json:
                return jsonify({'success': False, 'message': error_msg}), 404
            flash(error_msg, 'warning')
            return redirect(url_for('index'))

        success_msg = "Task updated successfully!"
        updated_task = database.get_task_by_id(task_id)
        stats = database.get_task_statistics()

        if is_json:
            return jsonify({
                'success': True,
                'message': success_msg,
                'task': updated_task,
                'stats': stats
            }), 200

        flash(success_msg, 'success')
        return redirect(url_for('index'))

    except Exception as e:
        error_msg = "Failed to update task due to a database error."
        if is_json:
            return jsonify({'success': False, 'message': error_msg}), 500
        flash(error_msg, 'danger')
        return redirect(url_for('index'))


@app.route('/toggle/<int:task_id>', methods=['POST'])
def toggle_task_route(task_id):
    """
    Toggle task completion status (Pending <-> Completed).
    """
    is_json = (
        request.is_json or 
        request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 
        'application/json' in request.headers.get('Accept', '')
    )

    try:
        updated_task = database.toggle_task_completion(task_id)

        if not updated_task:
            error_msg = "Task not found."
            if is_json:
                return jsonify({'success': False, 'message': error_msg}), 404
            flash(error_msg, 'warning')
            return redirect(url_for('index'))

        status_str = "completed" if updated_task['completed'] == 1 else "marked pending"
        success_msg = f'Task "{updated_task["title"]}" {status_str}!'
        stats = database.get_task_statistics()

        if is_json:
            return jsonify({
                'success': True,
                'message': success_msg,
                'task': updated_task,
                'stats': stats
            }), 200

        flash(success_msg, 'success')
        return redirect(url_for('index'))

    except Exception as e:
        error_msg = "Failed to toggle task status."
        if is_json:
            return jsonify({'success': False, 'message': error_msg}), 500
        flash(error_msg, 'danger')
        return redirect(url_for('index'))


@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task_route(task_id):
    """
    Delete a task by ID.
    """
    is_json = (
        request.is_json or 
        request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 
        'application/json' in request.headers.get('Accept', '')
    )

    try:
        task = database.get_task_by_id(task_id)
        if not task:
            error_msg = "Task not found."
            if is_json:
                return jsonify({'success': False, 'message': error_msg}), 404
            flash(error_msg, 'warning')
            return redirect(url_for('index'))

        title = task['title']
        deleted = database.delete_task(task_id)
        stats = database.get_task_statistics()

        success_msg = f'Task "{title}" deleted successfully.'
        if is_json:
            return jsonify({
                'success': True,
                'message': success_msg,
                'stats': stats
            }), 200

        flash(success_msg, 'info')
        return redirect(url_for('index'))

    except Exception as e:
        error_msg = "Failed to delete task."
        if is_json:
            return jsonify({'success': False, 'message': error_msg}), 500
        flash(error_msg, 'danger')
        return redirect(url_for('index'))


@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task_api(task_id):
    """
    API endpoint to retrieve a single task's data for the edit modal.
    """
    task = database.get_task_by_id(task_id)
    if not task:
        return jsonify({'success': False, 'message': 'Task not found'}), 404

    return jsonify({'success': True, 'task': task}), 200


@app.route('/api/stats', methods=['GET'])
def get_stats_api():
    """
    API endpoint to retrieve real-time statistics.
    """
    stats = database.get_task_statistics()
    return jsonify({'success': True, 'stats': stats}), 200


# Custom error handlers for smooth user experience
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html', tasks=[], stats=database.get_task_statistics(), current_filter='ALL', search_query='', error="Page not found"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('index.html', tasks=[], stats={'total': 0, 'completed': 0, 'pending': 0, 'percent': 0}, current_filter='ALL', search_query='', error="An unexpected server error occurred"), 500


if __name__ == '__main__':
    # Run development server on port 5000 (or PORT env var) with debug mode enabled
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port, debug=True)
