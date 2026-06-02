"""
Flask Application Factory

Creates and configures the Flask app with all business logic.
All legacy code is preserved and wrapped with new structure.
"""

from flask import Flask
from config import config
from extensions import init_extensions


def create_app(config_name='development'):
    """
    Application factory pattern.
    
    Creates Flask app with:
    - All legacy business logic preserved
    - New blueprint-based API structure
    - Proper database layer
    - Service wrappers
    """
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions (DB, Redis, CORS, etc)
    init_extensions(app)
    
    # Register database models
    with app.app_context():
        from extensions import db
        db.create_all()
    
    # Register API blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register CLI commands
    register_cli_commands(app)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        return {
            'status': 'healthy',
            'version': '2.0.0',
            'environment': config_name
        }
    
    print("✅ Flask app created successfully")
    return app


def register_blueprints(app):
    """Register all API blueprints"""
    from api import (
        chat_bp,
        security_bp,
        refactoring_bp,
        auth_bp,
        repositories_bp,
        health_bp,
        scoring_bp,
        compliance_bp,
        reports_bp,
        settings_bp,
    )

    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(security_bp, url_prefix='/api/security')
    app.register_blueprint(refactoring_bp, url_prefix='/api/refactoring')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(repositories_bp, url_prefix='/api/repositories')
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(scoring_bp, url_prefix='/api/scoring')
    app.register_blueprint(compliance_bp, url_prefix='/api/compliance')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(settings_bp, url_prefix='/api/settings')

    print("✅ Blueprints registered")


def register_error_handlers(app):
    """Register global error handlers"""
    
    @app.errorhandler(404)
    def not_found(e):
        return {
            'status': 'error',
            'code': 404,
            'message': 'Not found'
        }, 404
    
    @app.errorhandler(500)
    def internal_error(e):
        return {
            'status': 'error',
            'code': 500,
            'message': 'Internal server error'
        }, 500
    
    print("✅ Error handlers registered")


def register_cli_commands(app):
    """Register CLI commands"""
    
    @app.cli.command()
    def init_db():
        """Initialize the database."""
        from extensions import db
        db.create_all()
        print("✅ Database initialized")
    
    @app.cli.command()
    def seed_db():
        """Seed the database with sample data."""
        print("Seeding database...")
        # Add seeding logic here
        print("✅ Database seeded")
    
    print("✅ CLI commands registered")


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000, debug=True)
