from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
ma = Marshmallow(app)
migration = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
login.login_message_category = 'warning'
mail = Mail(app)

import models

