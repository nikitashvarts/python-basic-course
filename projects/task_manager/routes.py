import os
import sys
from tempfile import gettempdir

from managers.csv_manager import CSVManager
from managers.task_manager import TaskManager, TaskPriority
from flask import Blueprint, render_template, request, redirect, url_for, send_file, after_this_request

tasks_bp = Blueprint('tasks', __name__, template_folder='templates')


@tasks_bp.route('/')
@tasks_bp.route('/tasks')
def show_tasks():
    sort_by = request.args.get('sort_by', 'id')
    order = request.args.get('order', 'ASC')
    project = request.args.get('project')

    task_manager = TaskManager.get_instance()
    tasks = task_manager.get_tasks(sort_by, order, project)
    projects = task_manager.get_projects()

    return render_template('task_list.html', tasks=tasks, projects=projects)


@tasks_bp.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        deadline = request.form['deadline']
        priority = TaskPriority[request.form['priority']]
        project = request.form['project']

        task_manager = TaskManager.get_instance()
        task_manager.add_task(title, description, deadline, priority, project)
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
        project = request.form['project']

        task_manager.update_task(task_id, title, description, deadline, priority, project)
        return redirect(url_for('.show_tasks'))

    return render_template('task_form.html', task=task)


@tasks_bp.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task_manager = TaskManager.get_instance()
    task_manager.delete_task(task_id)
    return redirect(url_for('.show_tasks'))


@tasks_bp.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'csv_file' not in request.files:
        return 'No file part', 400

    csv_file = request.files['csv_file']

    if csv_file.filename == '':
        return 'No file selected', 400

    if csv_file and csv_file.filename.endswith('.csv'):
        try:
            file_path = os.path.join(gettempdir(), csv_file.filename)
            csv_file.save(file_path)

            csv_manager = CSVManager()
            csv_manager.import_tasks(file_path)
            os.remove(file_path)
        except Exception:
            return 'Failed to import the CSV file, try uploading another one', 400

        return redirect(url_for('.show_tasks'))

    return 'Invalid file format, please upload a CSV file', 400


@tasks_bp.route('/download_csv')
def download_csv():
    try:
        csv_manager = CSVManager()
        file_path = os.path.join(gettempdir(), 'tasks_export.csv')
        csv_manager.export_tasks(file_path)
    except Exception:
        return 'Failed to export tasks to a CSV file', 400

    @after_this_request
    def remove_file(response):
        try:
            os.remove(file_path)
        except OSError as err:
            print(f'Failed to remove the exported CSV file: {err}', file=sys.stderr)
        return response

    return send_file(file_path, as_attachment=True, mimetype='text/csv')
