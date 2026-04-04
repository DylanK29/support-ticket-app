#Flask Application Factory

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app(config_name=None):
    #Create Flask application
    app = Flask(__name__)
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    from config import config
    app.config.from_object(config[config_name])
    
    #Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    #Register blueprint
    from app.routes import main
    app.register_blueprint(main)
    
    #Create tables
    with app.app_context():
        db.create_all()

    #Create uploads folder
    uploads_folder = os.path.join(app.root_path, 'static', 'uploads')
    if not os.path.exists(uploads_folder):
        os.makedirs(uploads_folder)
    app.config['UPLOAD_FOLDER'] = uploads_folder
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  #16MB max
    
    return app

@login_manager.user_loader
def load_user(user_id):
    #Load user by ID
    from app.models import User
    return User.query.get(int(user_id))