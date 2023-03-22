from flask.cli import FlaskGroup

from project import init_app

app = init_app()

cli = FlaskGroup(app)


if __name__ == "__main__":
    cli()