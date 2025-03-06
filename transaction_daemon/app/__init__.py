from flask import Flask
from .config import Config
from .routes import api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from .routes import api_bp
    app.register_blueprint(api_bp)

    return app