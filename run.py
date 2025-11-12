import logging
import os

from app import create_app


app = create_app()

if __name__ == "__main__":
    logging.info("=" * 80)
    logging.info("🚀 Flask app starting...")
    logging.info(f"Environment: {os.getenv('FLASK_ENV', 'production')}")
    logging.info(f"Debug mode: {os.getenv('FLASK_DEBUG', 'False')}")
    logging.info(f"Log level: {os.getenv('LOG_LEVEL', 'INFO')}")
    
    # Development server - use gunicorn in production
    port = int(os.getenv("PORT", 8000))
    logging.info(f"📍 Server starting on 0.0.0.0:{port}")
    logging.info(f"🔗 Webhook URL should be: http://<your-domain>/webhook")
    logging.info("=" * 80)
    
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "False").lower() == "true")
