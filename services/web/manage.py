from flask.cli import FlaskGroup

from obliczeniakredytowe import init_app

os.environ['APPDB_PATH'] = "/home/ubuntu/data/" 

app = init_app()

cli = FlaskGroup(app)


if __name__ == "__main__":
    cli()