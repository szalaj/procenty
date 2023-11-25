# file used for developing
from obliczeniakredytowe import init_app
import os
import sys
from loguru import logger


print(f"run file _{__name__}")

# get current path
current_path = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.abspath(os.path.join(current_path, '../db'))
os.environ['APPDB_PATH'] = db_path 
os.environ['LOG_PATH'] = current_path   
#os.environ['APPDB_PATH'] = "/home/szalaj/procenty/services/db/" 

log_level = "DEBUG"
log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS zz}</green> | <level>{level: <8}</level> | <yellow>Line {line: >4} ({file}):</yellow> <b>{message}</b>"
logger.add(f"{os.getenv('LOG_PATH')}/file.log", level=log_level, format=log_format, colorize=False, backtrace=True, diagnose=True)



app = init_app()

if __name__ == "__main__":
    #app.run(port=80, debug=True)

    app.run(host='0.0.0.0', port=5000)
