
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

def init_app():
 
    app = Flask(__name__)
    app.config.from_object("project.config.Config")

    
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
    
    @login_manager.unauthorized_handler
    def unauthorized():
        return redirect(url_for('admin_bp.login'))
    
    from .routes.admin import admin_bp as admin_blueprint
    app.register_blueprint(admin_blueprint)

    from .routes.wps import bp as wps_blueprint
    app.register_blueprint(wps_blueprint)
    
    from .routes.dom import dom as dom_blueprint
    app.register_blueprint(dom_blueprint)

    return app





