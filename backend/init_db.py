import os
from alembic.config import Config
from alembic import command

print("Running database migrations...")
# Find absolute path of alembic.ini relative to init_db.py location
base_dir = os.path.dirname(os.path.abspath(__file__))
alembic_ini_path = os.path.join(base_dir, "alembic.ini")

alembic_cfg = Config(alembic_ini_path)
command.upgrade(alembic_cfg, "head")
print("Database migrations applied successfully!")

