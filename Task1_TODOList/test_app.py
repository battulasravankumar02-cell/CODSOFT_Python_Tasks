"""
Comprehensive Unit & Integration Tests for CODSOFT Task 1 To-Do List Application
Tests all database operations and Flask routes thoroughly.
"""

import unittest
import os
import tempfile
import json
import database
from app import app


class TestTodoList(unittest.TestCase):

    def setUp(self):
        # Configure app for testing
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Create temporary database for testing
        self.db_fd, self.db_path = tempfile.mkstemp()
        database.DB_PATH = self.db_path
        database.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_database_crud(self):
        """Test database helper functions directly."""
        # 1. Add Task
        task_id = database.add_task(
            title="Complete Python Assignment",
            description="Practice functions and classes",
            priority="HIGH",
            due_date="2026-09-30"
        )
        self.assertIsInstance(task_id, int)

        # 2. Retrieve Task
        task = database.get_task_by_id(task_id)
        self.assertIsNotNone(task)
        self.assertEqual(task['title'], "Complete Python Assignment")
        self.assertEqual(task['priority'], "HIGH")
        self.assertEqual(task['completed'], 0)

        # 3. Update Task
        updated = database.update_task(
            task_id=task_id,
            title="Complete Python Assignment Updated",
            description="Updated details",
            priority="MEDIUM",
            due_date="2026-10-01"
        )
        self.assertTrue(updated)
        updated_task = database.get_task_by_id(task_id)
        self.assertEqual(updated_task['title'], "Complete Python Assignment Updated")
        self.assertEqual(updated_task['priority'], "MEDIUM")

        # 4. Toggle Completion
        toggled = database.toggle_task_completion(task_id)
        self.assertEqual(toggled['completed'], 1)
        self.assertIsNotNone(toggled['completed_at'])

        # Toggle back to pending
        toggled_back = database.toggle_task_completion(task_id)
        self.assertEqual(toggled_back['completed'], 0)

        # 5. Statistics
        stats = database.get_task_statistics()
        self.assertEqual(stats['total'], 1)
        self.assertEqual(stats['completed'], 0)
        self.assertEqual(stats['pending'], 1)

        # 6. Delete Task
        deleted = database.delete_task(task_id)
        self.assertTrue(deleted)
        self.assertIsNone(database.get_task_by_id(task_id))

    def test_flask_routes(self):
        """Test all Flask endpoints."""
        # 1. GET / (Home page)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'TO-DO LIST', response.data)
        self.assertIn(b'No tasks yet', response.data)

        # 2. POST /add (JSON)
        add_res = self.client.post('/add', json={
            'title': 'Test Flask Route Task',
            'description': 'Description here',
            'priority': 'HIGH',
            'due_date': '2026-10-05'
        })
        self.assertEqual(add_res.status_code, 201)
        data = json.loads(add_res.data)
        self.assertTrue(data['success'])
        task_id = data['task']['id']

        # 3. GET / (Task now listed)
        home_res = self.client.get('/')
        self.assertEqual(home_res.status_code, 200)
        self.assertIn(b'Test Flask Route Task', home_res.data)

        # 4. Validation on Empty Title
        bad_add_res = self.client.post('/add', json={'title': '   '})
        self.assertEqual(bad_add_res.status_code, 400)

        # 5. GET /api/tasks/<id>
        api_res = self.client.get(f'/api/tasks/{task_id}')
        self.assertEqual(api_res.status_code, 200)
        api_data = json.loads(api_res.data)
        self.assertEqual(api_data['task']['title'], 'Test Flask Route Task')

        # 6. POST /update/<id>
        update_res = self.client.post(f'/update/{task_id}', json={
            'title': 'Test Flask Route Task Renamed',
            'description': 'Updated description',
            'priority': 'LOW',
            'due_date': '2026-10-10'
        })
        self.assertEqual(update_res.status_code, 200)

        # 7. POST /toggle/<id> (AJAX)
        toggle_res = self.client.post(f'/toggle/{task_id}', headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEqual(toggle_res.status_code, 200)
        toggle_data = json.loads(toggle_res.data)
        self.assertEqual(toggle_data['task']['completed'], 1)
        self.assertEqual(toggle_data['stats']['completed'], 1)

        # 8. POST /delete/<id> (AJAX)
        del_res = self.client.post(f'/delete/{task_id}', headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEqual(del_res.status_code, 200)
        del_data = json.loads(del_res.data)
        self.assertTrue(del_data['success'])
        self.assertEqual(del_data['stats']['total'], 0)


if __name__ == '__main__':
    unittest.main()
