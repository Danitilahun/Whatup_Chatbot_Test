from flask import Flask
from app.config import load_configurations, configure_logging
from .views import webhook_blueprint


def create_app():
    import logging
    
    app = Flask(__name__)

    # Load configurations and logging settings
    load_configurations(app)
    configure_logging()
    
    logging.info("=" * 80)
    logging.info("🔧 [APP INIT] Creating Flask application...")

    # Import and register blueprints, if any
    logging.info("📋 [APP INIT] Registering webhook blueprint...")
    app.register_blueprint(webhook_blueprint)
    logging.info("✅ [APP INIT] Webhook blueprint registered at /webhook")
    
    logging.info("✅ [APP INIT] Flask application created successfully!")
    logging.info("=" * 80)

    return app
