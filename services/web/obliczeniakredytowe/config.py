import os


basedir = os.path.abspath(os.path.dirname(__file__))
print(basedir)
dbpath = os.path.abspath(os.path.join(basedir, '../../db/database.db'))
print(dbpath)

class Config(object):
    STATIC_FOLDER = f"{os.getenv('APP_FOLDER')}/obliczeniakredytowe/static"
    MEDIA_FOLDER = f"{os.getenv('APP_FOLDER')}/obliczeniakredytowe/media"
    SECRET_KEY = 'asdfal3l3j4lkjlaksd333'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + dbpath
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = "Europe/Berlin"