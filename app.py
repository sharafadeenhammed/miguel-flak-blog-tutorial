from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_babel import Babel
from config import Config

def get_locale():
  return request.accept_languages.best_match(app.config['LANGUAGES'])


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
ma = Marshmallow(app)
migration = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
login.login_message_category = 'warning'
mail = Mail(app)
moment = Moment(app=app)
babel = Babel(app=app, locale_selector=get_locale )




import models

