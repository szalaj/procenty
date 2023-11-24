# file used for developing
from obliczeniakredytowe import init_app
import os
print(__name__)

# get current path
current_path = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.abspath(os.path.join(current_path, '../db'))
os.environ['APPDB_PATH'] = db_path 
#os.environ['APPDB_PATH'] = "/home/szalaj/procenty/services/db/" 

app = init_app()

if __name__ == "__main__":
    #app.run(port=80, debug=True)

    app.run(host='0.0.0.0', port=5000)
