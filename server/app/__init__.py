from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-string')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Tokens don't expire for demo
    
    # Initialize extensions
    CORS(app, origins=["http://localhost:3000"])  # Allow React dev server
    jwt = JWTManager(app)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.opportunities import opportunities_bp
    from app.routes.scholarships import scholarships_bp
    from app.routes.mentorship import mentorship_bp
    from app.routes.webinars import webinars_bp
    from app.routes.stories import stories_bp
    from app.routes.applications import applications_bp
    from app.routes.messages import messages_bp
    from app.routes.connections import connections_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(opportunities_bp, url_prefix='/api/opportunities')
    app.register_blueprint(scholarships_bp, url_prefix='/api/scholarships')
    app.register_blueprint(mentorship_bp, url_prefix='/api/mentorship')
    app.register_blueprint(webinars_bp, url_prefix='/api/webinars')
    app.register_blueprint(stories_bp, url_prefix='/api/stories')
    app.register_blueprint(applications_bp, url_prefix='/api/applications')
    app.register_blueprint(messages_bp, url_prefix='/api/messages')
    app.register_blueprint(connections_bp, url_prefix='/api/connections')
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Alumni Connect API is running'}
    
    return app