from flask import Flask

from .routes.category_routes import category_bp
from .routes.main import main_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    app.register_blueprint(main_bp)
    app.register_blueprint(category_bp)

    return app
