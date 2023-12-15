from os import environ, path

dirname = path.abspath(path.dirname(__file__))

class Config:
  POST_PER_PAGE = 3
  SECRET_KEY = environ.get('SECRET_KEY') or '__MY_SECRET_KEY__'
  SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URI') or 'sqlite:///' + path.join(dirname, 'db.sqlite')
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  MAIL_SERVER = environ.get('MAIL_SERVER') or 'smtp.googlemail.com'
  MAIL_PORT = int(environ.get('MAIL_PORT') or 25) or 587
  MAIL_USE_TLS = environ.get('MAIL_USE_TLS') or 1
  MAIL_USERNAME = environ.get('MAIL_USERNAME') or 'allahsegun@gmail.com'
  MAIL_PASSWORD = environ.get('MAIL_PASSWORD') or 'HSallah123..'
  ADMINS = ['your-email@example.com']