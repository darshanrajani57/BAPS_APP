from flask import Flask
from config import Config
from models import db
from sqlalchemy import inspect
import logging

app = Flask(__name__)
# Override echo to reduce noise
Config.SQLALCHEMY_ECHO = False
app.config.from_object(Config)
db.init_app(app)

# Disable logging for sqlalchemy
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

def inspect_table():
    with app.app_context():
        inspector = inspect(db.engine)
        columns = inspector.get_columns('attendance')
        print("Columns in 'attendance' table:")
        for column in columns:
            print(f"- {column['name']} ({column['type']})")

if __name__ == "__main__":
    inspect_table()
