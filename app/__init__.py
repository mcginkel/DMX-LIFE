"""
DMX Life Application - App Initialization
"""
import os
import json
import datetime
from flask import Flask

def create_app(config=None):
    """Initialize and configure the Flask application"""
    app = Flask(__name__)
    
    # Default configuration
    app.config.update(
        SECRET_KEY=os.urandom(24),
        CONFIG_FILE=os.path.join(os.path.dirname(__file__), 'config.json'),
        MAX_SCENES=10
    )
    
    # Add context processors for templates
    @app.context_processor
    def inject_year():
        return {'current_year': datetime.datetime.now().year}
    
    # Override with any passed configuration
    if config:
        app.config.update(config)
    
    # Load configuration from file if it exists
    if os.path.exists(app.config['CONFIG_FILE']):
        try:
            with open(app.config['CONFIG_FILE'], 'r') as f:
                app.config.update(json.load(f))
        except Exception as e:
            app.logger.error(f"Error loading configuration: {e}")
    
    # Register blueprints
    from app.views.main import main_bp
    from app.views.setup import setup_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(setup_bp, url_prefix='/setup')
    
    # Initialize DMX controller
    from app.dmx_controller import init_dmx_controller
    init_dmx_controller(app)
    
    return app
