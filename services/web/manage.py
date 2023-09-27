from flask.cli import FlaskGroup
import os
from obliczeniakredytowe import init_app


if 0:
    os.environ['APPDB_PATH'] = "/home/ubuntu/data/" 
else:
    # test mode with gunicorn
    os.environ['APPDB_PATH'] = "/home/szalaj/procenty/services/db/" 

app = init_app()

cli = FlaskGroup(app)


if __name__ == "__main__":
    cli()