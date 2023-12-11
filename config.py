from os import environ, path

dirname = path.abspath(path.dirname(__file__))

class Config:
  SECRET_KEY = environ.get('SECRET_KEY') or '__MY_SECRET_KEY__'
  SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URI') or 'sqlite:///' + path.join(dirname, 'db.sqlite')
  SQLALCHEMY_TRACK_MODIFICATIONS = False