import sqlite3
from enum import Enum, auto
from flask import current_app


class TaskPriority(Enum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()


class TaskManager:
    def __init__(self):
        db_name = current_app.config['DATABASE']
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def __del__(self):
        self.conn.close()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                deadline DATE,
                priority TEXT CHECK(priority IN ('LOW', 'MEDIUM', 'HIGH'))
            )
        ''')
        self.conn.commit()

    def add_task(self, title, description, deadline, priority):
        TaskManager.__validate_priority(priority)

        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (title, description, deadline, priority)
            VALUES (?, ?, ?, ?)
        ''', (title, description, deadline, priority.name))
        self.conn.commit()

    def get_tasks(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks')
        return cursor.fetchall()

    def update_task(self, task_id, title=None, description=None, deadline=None, priority=None):
        update_query = 'UPDATE tasks SET '
        updates = []
        if title:
            updates.append(f'title = "{title}"')
        if description:
            updates.append(f'description = "{description}"')
        if deadline:
            updates.append(f'deadline = "{deadline}"')
        if priority:
            TaskManager.__validate_priority(priority)
            updates.append(f'priority = "{priority.name}"')

        update_query += ', '.join(updates) + f' WHERE id = {task_id}'
        cursor = self.conn.cursor()
        cursor.execute(update_query)
        self.conn.commit()

    def delete_task(self, task_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        self.conn.commit()

    @staticmethod
    def __validate_priority(priority):
        if not isinstance(priority, TaskPriority):
            raise ValueError('Priority must be of type "TaskPriority"')
