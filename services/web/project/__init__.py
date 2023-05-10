
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler

import requests

db = SQLAlchemy()

def init_app():
 
    app = Flask(__name__)
    app.config.from_object("project.config.Config")

    
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
    
    @login_manager.unauthorized_handler
    def unauthorized():
        return redirect(url_for('admin_bp.login'))
    

    @scheduler.task('cron', id='updatewibor', hour='*', minute='0')
    def wibor_scheduler():

        print('------------scheduler----------------')

        try:
            response6m = requests.get('https://stooq.pl/q/d/l/?s=plopln6m&i=d')
            
            with open("./project/static/plopln6m_d.csv", "wb") as f:
                f.write(response6m.content)

            response3m = requests.get('https://stooq.pl/q/d/l/?s=plopln3m&i=d')
            
            with open("./project/static/plopln3m_d.csv", "wb") as f:
                f.write(response3m.content)
        except:
            print('update wibor failed')
        

    
    from .routes.admin import admin_bp as admin_blueprint
    app.register_blueprint(admin_blueprint)

    from .routes.wps import bp as wps_blueprint
    app.register_blueprint(wps_blueprint)
    
    from .routes.dom import dom as dom_blueprint
    app.register_blueprint(dom_blueprint)

    return app





