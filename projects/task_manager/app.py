import os
from flask import Flask

app = Flask(__name__)
app.config.from_mapping(
    DATABASE=os.path.join(app.instance_path, 'tasks.sqlite')
)

os.makedirs(app.instance_path, exist_ok=True)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
