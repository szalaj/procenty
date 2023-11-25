from flask.cli import FlaskGroup
import os
import obliczeniakredytowe 
from loguru import logger
import sys

if 0:
    os.environ['APPDB_PATH'] = "/home/ubuntu/data/" 
    os.environ['LOG_PATH'] = "/home/ubuntu/data/" 
else:
    print('starcik lokal')
    # test mode with gunicorn
    current_path = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.abspath(os.path.join(current_path, '../db'))
    print(db_path)
    os.environ['APPDB_PATH'] = db_path 
    os.environ['LOG_PATH'] = current_path   


log_level = "DEBUG"
log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS zz}</green> | <level>{level: <8}</level> | <yellow>Line {line: >4} ({file}):</yellow> <b>{message}</b>"
logger.add(f"{os.getenv('LOG_PATH')}/file.log", level=log_level, format=log_format, colorize=False, backtrace=True, diagnose=True)


app = obliczeniakredytowe.init_app()

cli = FlaskGroup(app)


if __name__ == "__main__":
    cli()