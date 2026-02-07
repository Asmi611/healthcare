import os
from flask import Flask
from .routes import init_routes
from . import db
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.txt'))

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev-secret'),
        SESSION_COOKIE_HTTPONLY=True,
    )
    init_routes(app)
    return app
