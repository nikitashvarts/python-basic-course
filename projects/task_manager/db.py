import sqlite3
from enum import Enum, auto
from flask import current_app, g


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
                priority TEXT CHECK(priority IN ('LOW', 'MEDIUM', 'HIGH')),
                project TEXT
            )
        ''')
        self.conn.commit()

    def add_task(self, title, description, deadline, priority, project):
        TaskManager.__validate_priority(priority)

        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (title, description, deadline, priority, project)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, description, deadline, priority.name, project))
        self.conn.commit()

    def get_tasks(self, sort_by, order, project):
        if sort_by not in ('id', 'title', 'deadline', 'priority'):
            sort_by = 'id'
        if order not in ('ASC', 'DESC'):
            order = 'ASC'

        query = ['SELECT * FROM tasks']
        values = []

        if project:
            query.append('WHERE project = ?')
            values.append(project)

        query.append(f'ORDER BY {sort_by} {order}')

        cursor = self.conn.cursor()
        cursor.execute(' '.join(query), values)
        return cursor.fetchall()

    def get_task_by_id(self, task_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        return cursor.fetchone()

    def update_task(self, task_id, title=None, description=None, deadline=None, priority=None, project=None):
        update_query = 'UPDATE tasks SET '
        updates = []
        values = []

        if title:
            updates.append('title = ?')
            values.append(title)
        if description:
            updates.append('description = ?')
            values.append(description)
        if deadline:
            updates.append('deadline = ?')
            values.append(deadline)
        if priority:
            TaskManager.__validate_priority(priority)
            updates.append('priority = ?')
            values.append(priority.name)
        if project:
            updates.append('project = ?')
            values.append(project)

        update_query += ', '.join(updates) + ' WHERE id = ?'
        values.append(task_id)

        cursor = self.conn.cursor()
        cursor.execute(update_query, values)
        self.conn.commit()

    def delete_task(self, task_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        self.conn.commit()

    def get_projects(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT DISTINCT project FROM tasks ORDER BY project ASC')
        return [project[0] for project in cursor.fetchall()]

    @staticmethod
    def get_instance():
        if 'task_manager' not in g:
            g.task_manager = TaskManager()
        return g.task_manager

    @staticmethod
    def __validate_priority(priority):
        if not isinstance(priority, TaskPriority):
            raise ValueError('Priority must be of type "TaskPriority"')
