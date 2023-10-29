from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from datetime import timedelta
from .config import Config
from flask_cors import CORS

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app,  resources={r"/*": {"origins": ["http://localhost:3000", "https://siwes-eight.vercel.app"]}}, supports_credentials=True, allow_headers=["Content-Type"])
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager.init_app(app)
    login_manager.remember_cookie_duration = timedelta(days=30)

    from .databaseModel import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    @app.get('/')
    def home():
        return "Welcome!!! This is a Digital Siwes Log book"

    from .routes.register import register_blueprint
    from .routes.login import login_blueprint
    from .routes.student import student_blueprint
    from .routes.supervisor import supervisor_blueprint
    from .routes.student_profile import student_profile_blueprint
    from .routes.logout import logout_blueprint

    app.register_blueprint(register_blueprint, url_prefix="/register")
    app.register_blueprint(login_blueprint, url_prefix="/login")
    app.register_blueprint(student_blueprint, url_prefix="/student")
    app.register_blueprint(supervisor_blueprint, url_prefix='/supervisor')
    app.register_blueprint(student_profile_blueprint, url_prefix="/student_profile")
    app.register_blueprint(logout_blueprint, url_prefix="/logout")

    return app