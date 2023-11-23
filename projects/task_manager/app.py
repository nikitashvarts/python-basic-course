import os
from flask import Flask
from routes import tasks_bp

app = Flask(__name__)
app.register_blueprint(tasks_bp)
app.config.from_mapping(
    DATABASE=os.path.join(app.instance_path, 'tasks.sqlite')
)

os.makedirs(app.instance_path, exist_ok=True)

if __name__ == '__main__':
    app.run()
