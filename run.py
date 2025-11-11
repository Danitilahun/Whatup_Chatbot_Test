import logging
import os

from app import create_app


app = create_app()

if __name__ == "__main__":
    logging.info("Flask app started")
    # Development server - use gunicorn in production
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "False").lower() == "true")
