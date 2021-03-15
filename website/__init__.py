from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_migrate import Migrate
from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash

db= SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.secret_key = "1234"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views

    app.register_blueprint(views)
    from .models import User, Review

    if not path.exists("website/"+DB_NAME):
        db.create_all(app=app)
        print("DB created")
        with app.app_context():
            user = User(email="admin", password=generate_password_hash('admin', method="sha256"), plec="admin", admin=True)
            db.session.add(user)
            db.session.commit()

    login_manager = LoginManager()
    login_manager.login_view = 'views.login'
    login_manager.init_app(app)

    migrate = Migrate(app, db)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app