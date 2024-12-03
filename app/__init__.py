from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    with app.app_context():
        from .routes import main_bp
        app.register_blueprint(main_bp)

    return app