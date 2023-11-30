from db import TaskManager, TaskPriority
from flask import Blueprint, render_template, request, redirect, url_for

tasks_bp = Blueprint('tasks', __name__, template_folder='templates')


@tasks_bp.route('/')
@tasks_bp.route('/tasks')
def show_tasks():
    sort_by = request.args.get('sort_by', 'id')
    order = request.args.get('order', 'ASC')

    task_manager = TaskManager.get_instance()
    tasks = task_manager.get_tasks(sort_by, order)
    return render_template('task_list.html', tasks=tasks)


@tasks_bp.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        deadline = request.form['deadline']
        priority = TaskPriority[request.form['priority']]

        task_manager = TaskManager.get_instance()
        task_manager.add_task(title, description, deadline, priority)
        return redirect(url_for('.show_tasks'))
    return render_template('task_form.html')


@tasks_bp.route('/update_task/<int:task_id>', methods=['GET', 'POST'])
def update_task(task_id):
    task_manager = TaskManager.get_instance()
    task = task_manager.get_task_by_id(task_id)
    if not task:
        return "Task not found", 404

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        deadline = request.form['deadline']
        priority = TaskPriority[request.form['priority']]

        task_manager.update_task(task_id, title, description, deadline, priority)
        return redirect(url_for('.show_tasks'))

    return render_template('task_form.html', task=task)


@tasks_bp.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task_manager = TaskManager.get_instance()
    task_manager.delete_task(task_id)
    return redirect(url_for('.show_tasks'))
