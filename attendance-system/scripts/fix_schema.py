import sys
from pathlib import Path
# Ensure project root is on sys.path so we can import config/models
sys.path.append(str(Path(__file__).resolve().parents[1]))

from config import Config
from sqlalchemy import create_engine, text

print('Using DB URI:', Config.SQLALCHEMY_DATABASE_URI)

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
with engine.connect() as conn:
    # Use autocommit for DDL in PostgreSQL
    conn = conn.execution_options(isolation_level="AUTOCOMMIT")
    res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='attendance' AND column_name='sampark_name'"))
    exists = res.fetchone() is not None
    if exists:
        print('Column sampark_name already exists in attendance table.')
    else:
        print('Column sampark_name missing — adding it now...')
        conn.execute(text("ALTER TABLE attendance ADD COLUMN sampark_name VARCHAR(255);"))
        print('Column sampark_name added.')
