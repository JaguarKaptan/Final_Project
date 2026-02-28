import os
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from datetime import timedelta
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

    

db = SQLAlchemy()
mail = Mail()
csrf = CSRFProtect()
load_dotenv()
limiter = Limiter(get_remote_address)

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')

    app.config["SESSION_PERMANENT"] = os.environ.get("SESSION_PERMANENT", "False") == "True"
    app.config["SESSION_TYPE"] = os.environ.get("SESSION_TYPE", "filesystem")
    app.config["REMEMBER_COOKIE_DURATION"] = os.environ.get("REMEMBER_COOKIE_DURATION", "7")  # default to 7 days

    # Mail Configuration
    # app.config['MAIL_SERVER'] = 'localhost'
    # app.config['MAIL_PORT'] = 8025  # test server port
    app.config['MAIL_SUPPRESS_SEND'] = os.environ.get("MAIL_SUPPRESS_SEND", "False") == "True"
    # app.config['MAIL_DEFAULT_SENDER'] = ('Test Bot', 'test@example.com')

    app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER")
    app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT"))
    app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS") == "True"
    app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER")

    mail.init_app(app)

    csrf.init_app(app)

    #NEW
    limiter.init_app(app)

    # will be moved to the .env
    app.secret_key = os.environ.get("SECRET_KEY") # OLDIE '0pp1jGIWBg6QunveBvqyU9vMElA4H0gWjryr_GoTKFc' # will be moved to the .env

    #Initialize the database
    db.init_app(app)

    #Initialize the login manager for the session management
    login_manager = LoginManager()
    login_manager.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(uid):
        return User.query.get(uid)
    
    @login_manager.unauthorized_handler
    def unauthorized_callback():
        return redirect(url_for('login'))
    
    # Redirect to to the login page if user is no loged in
    login_manager.login_view = "login"

    bcrypt = Bcrypt(app)

    from routes import register_routes
    register_routes(app, db, bcrypt)

    migrate = Migrate(app, db)

    return app