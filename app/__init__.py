from flask import Flask

def create_app(config_object):
    """Construct the core application."""
    app = Flask('song_recommender')
    app.config.from_object(config_object)

    # Imports
    from .views import view

    # REGISTER ROUTES
    app.register_blueprint(view, url_prefix="/")

    return app