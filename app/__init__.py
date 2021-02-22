from flask import Flask

def create_app(config_object):
    """Construct the core application."""
    app = Flask('song_recommender',static_folder = None)
    app.config.from_object(config_object)
    with app.app_context():
        # Imports
        from .views import view

        # REGISTER ROUTES
        app.register_blueprint(view)

        return app