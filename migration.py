from app import app, db
from flask_migrate import Migrate

migration = Migrate(app, db)
  