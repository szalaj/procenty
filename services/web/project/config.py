import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    STATIC_FOLDER = f"{os.getenv('APP_FOLDER')}/project/static"
    MEDIA_FOLDER = f"{os.getenv('APP_FOLDER')}/project/media"
    SECRET_KEY = 'asdfal3l3j4lkjlaksd333'
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"