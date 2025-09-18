from flask import Flask
from app.routes.users import users_bp
from app.routes.mentorship import mentorship_bp
from app.routes.opportunities import opportunities_bp
from app.routes.stories import stories_bp
from app.routes.applications import applications_bp

def create_app():
    app = Flask(__name__)

    # Register blueprints
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(mentorship_bp, url_prefix="/api/mentorship")
    app.register_blueprint(opportunities_bp, url_prefix="/api/opportunities")
    app.register_blueprint(stories_bp, url_prefix="/api/stories")
    app.register_blueprint(applications_bp, url_prefix="/api/applications")

    return app
