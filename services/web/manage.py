from flask.cli import FlaskGroup

from project import init_app

def start_app(*args, **kwargs):



    app = init_app(kwargs['ifwibor'])

    cli = FlaskGroup(app)

    return app

