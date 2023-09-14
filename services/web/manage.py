from flask.cli import FlaskGroup
import os
from obliczeniakredytowe import init_app

os.environ['APPDB_PATH'] = "/home/ubuntu/data/" 

app = init_app()

cli = FlaskGroup(app)


if __name__ == "__main__":
    cli()