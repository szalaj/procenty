# file used for developing
from obliczeniakredytowe import init_app
import os
print(__name__)
os.environ['APPDB_PATH'] = "/home/szalaj/procenty/services/db/" 
app = init_app()

if __name__ == "__main__":
    #app.run(port=80, debug=True)

    app.run(host='0.0.0.0', port=5000)
