import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import Config
from sqlalchemy import create_engine, text

print('Using DB URI:', Config.SQLALCHEMY_DATABASE_URI)
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
with engine.connect() as conn:
    res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='attendance' ORDER BY ordinal_position"))
    cols = [row[0] for row in res]
    print('attendance columns:', cols)
