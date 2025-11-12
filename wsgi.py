import os
import logging
from app import create_app

# Configure logging before creating the app
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

logger.info("=" * 80)
logger.info("🌐 [WSGI] WSGI Application Entry Point")
logger.info("=" * 80)

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logger.info("=" * 80)
    logger.info(f"🚀 Starting WSGI server on 0.0.0.0:{port}")
    logger.info(f"🔗 Webhook endpoint: http://<your-domain>/webhook")
    logger.info("✅ Ready to receive WhatsApp webhook requests!")
    logger.info("=" * 80)
    app.run(host="0.0.0.0", port=port)