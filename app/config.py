import sys
import os
from dotenv import load_dotenv
import logging


def load_configurations(app):
    logging.info("=" * 80)
    logging.info("⚙️ [CONFIG] Loading configurations from environment...")
    
    load_dotenv()
    logging.info("✅ [CONFIG] Environment variables loaded from .env file")
    
    # Load and log each configuration
    access_token = os.getenv("ACCESS_TOKEN")
    your_phone = os.getenv("YOUR_PHONE_NUMBER")
    app_id = os.getenv("APP_ID")
    app_secret = os.getenv("APP_SECRET")
    recipient_waid = os.getenv("RECIPIENT_WAID")
    version = os.getenv("VERSION")
    phone_id = os.getenv("PHONE_NUMBER_ID")
    verify_token = os.getenv("VERIFY_TOKEN")
    
    # Set configurations
    app.config["ACCESS_TOKEN"] = access_token
    app.config["YOUR_PHONE_NUMBER"] = your_phone
    app.config["APP_ID"] = app_id
    app.config["APP_SECRET"] = app_secret
    app.config["RECIPIENT_WAID"] = recipient_waid
    app.config["VERSION"] = version
    app.config["PHONE_NUMBER_ID"] = phone_id
    app.config["VERIFY_TOKEN"] = verify_token
    
    # Production settings
    app.config["ENV"] = os.getenv("FLASK_ENV", "production")
    app.config["DEBUG"] = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.config["JSON_SORT_KEYS"] = False
    
    # Log configuration status
    logging.info("📋 [CONFIG] Environment variables loaded:")
    logging.info(f"  ACCESS_TOKEN: {'✅ Set' if access_token else '❌ NOT SET'}")
    logging.info(f"  YOUR_PHONE_NUMBER: {'✅ Set' if your_phone else '❌ NOT SET'} ({your_phone if your_phone else 'N/A'})")
    logging.info(f"  APP_ID: {'✅ Set' if app_id else '❌ NOT SET'}")
    logging.info(f"  APP_SECRET: {'✅ Set' if app_secret else '❌ NOT SET'}")
    logging.info(f"  RECIPIENT_WAID: {'✅ Set' if recipient_waid else '❌ NOT SET'} ({recipient_waid if recipient_waid else 'N/A'})")
    logging.info(f"  VERSION: {'✅ Set' if version else '❌ NOT SET'} ({version if version else 'N/A'})")
    logging.info(f"  PHONE_NUMBER_ID: {'✅ Set' if phone_id else '❌ NOT SET'} ({phone_id if phone_id else 'N/A'})")
    logging.info(f"  VERIFY_TOKEN: {'✅ Set' if verify_token else '❌ NOT SET'}")
    logging.info(f"  FLASK_ENV: {app.config['ENV']}")
    logging.info(f"  FLASK_DEBUG: {app.config['DEBUG']}")
    logging.info("✅ [CONFIG] All configurations loaded successfully!")
    logging.info("=" * 80)


def configure_logging():
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )
    
    # Log the logging configuration
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info(f"🔌 [LOGGING] Logging configured with level: {log_level}")
    logger.info("📝 [LOGGING] Format: %(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger.info("=" * 80)
