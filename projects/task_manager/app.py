import os
import sys
import sqlite3
from flask import Flask
from routes import tasks_bp

app = Flask(__name__)
app.register_blueprint(tasks_bp)
app.config.from_mapping(
    DATABASE=os.path.join(app.instance_path, 'tasks.sqlite')
)


@app.errorhandler(sqlite3.Error)
def handle_error(err):
    return f'Database operation failed: {err}', 500


try:
    os.makedirs(app.instance_path, exist_ok=True)
except OSError as e:
    sys.exit(f'Failed to create the instance directory at {e.filename}')

if __name__ == '__main__':
    app.run()
