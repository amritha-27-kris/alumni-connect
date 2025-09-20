from flask import Flask
from flask_cors import CORS

from .routes.users import users_bp
from .routes.opportunities import opportunities_bp
from .routes.mentorship import mentorship_bp
from .routes.stories import stories_bp
from .routes.applications import applications_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Register blueprints
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(opportunities_bp, url_prefix="/api/opportunities")
    app.register_blueprint(mentorship_bp, url_prefix="/api/mentorship")
    app.register_blueprint(stories_bp, url_prefix="/api/stories")
    app.register_blueprint(applications_bp, url_prefix="/api/applications")

    @app.route("/")
    def index():
        return {"message": "Welcome to Alumni Connect API. Use /api/* routes."}

    return app
