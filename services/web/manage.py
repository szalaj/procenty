from flask.cli import FlaskGroup
import os
from obliczeniakredytowe import init_app


if 0:
    os.environ['APPDB_PATH'] = "/home/ubuntu/data/" 
else:
    print('starcik lokal')
    # test mode with gunicorn
    current_path = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.abspath(os.path.join(current_path, '../db'))
    print(db_path)
    os.environ['APPDB_PATH'] = db_path 

app = init_app()

cli = FlaskGroup(app)


if __name__ == "__main__":
    cli()