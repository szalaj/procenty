
from flask import Flask, redirect, url_for
from flask_login import LoginManager


def init_app():
    app = Flask(__name__)
    app.config.from_object("project.config.Config")

    login_manager = LoginManager()
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)
    
    @login_manager.unauthorized_handler
    def unauthorized():
        return redirect(url_for('bp.login'))
    

    from .routes import bp as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app





