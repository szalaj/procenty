import os


basedir = os.path.abspath(os.path.dirname(__file__))
dbdir = os.path.abspath(os.path.join(basedir, '../../db/database.db'))


print(dbdir)
class Config(object):
    print(f"{os.getenv('APPDB_PATH')} nic")
    STATIC_FOLDER = f"{os.getenv('APP_FOLDER')}/obliczeniakredytowe/static"
    MEDIA_FOLDER = f"{os.getenv('APP_FOLDER')}/obliczeniakredytowe/media"
    SECRET_KEY = 'asdfal3l3j4lkjlaksd333'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + f"{os.getenv('APPDB_PATH')}database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = "Europe/Berlin"