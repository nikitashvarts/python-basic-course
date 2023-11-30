import csv
from .task_manager import TaskManager, TaskPriority


class CSVManager:
    def __init__(self):
        self.task_manager = TaskManager.get_instance()

    def import_tasks(self, file_path):
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                title = row['Title']
                description = row['Description']
                deadline = row['Deadline']
                priority = TaskPriority[row['Priority']]
                project = row['Project']

                self.task_manager.add_task(title, description, deadline, priority, project)

    def export_tasks(self, file_path):
        tasks = self.task_manager.get_tasks(sort_by=None, order=None, project=None)

        with open(file_path, 'w') as file:
            fieldnames = ['Title', 'Description', 'Deadline', 'Priority', 'Project']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            for task in tasks:
                writer.writerow({
                    'Title': task[1],
                    'Description': task[2],
                    'Deadline': task[3],
                    'Priority': task[4],
                    'Project': task[5]
                })
