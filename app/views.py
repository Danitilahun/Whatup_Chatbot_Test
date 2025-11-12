import logging
import json

from flask import Blueprint, request, jsonify, current_app

from .decorators.security import signature_required
from .utils.whatsapp_utils import (
    process_whatsapp_message,
    is_valid_whatsapp_message,
)

webhook_blueprint = Blueprint("webhook", __name__)


def handle_message():
    """
    Handle incoming webhook events from the WhatsApp API.

    This function processes incoming WhatsApp messages and other events,
    such as delivery statuses. If the event is a valid message, it gets
    processed. If the incoming payload is not a recognized WhatsApp event,
    an error is returned.

    Every message send will trigger 4 HTTP requests to your webhook: message, sent, delivered, read.

    Returns:
        response: A tuple containing a JSON response and an HTTP status code.
    """
    logging.info("=" * 80)
    logging.info("🔵 [WEBHOOK POST] New webhook request received")
    logging.info(f"Headers: {dict(request.headers)}")
    
    try:
        body = request.get_json()
        logging.info(f"✅ [WEBHOOK POST] Successfully parsed JSON body")
        logging.info(f"📦 Request body: {json.dumps(body, indent=2)}")
    except Exception as e:
        logging.error(f"❌ [WEBHOOK POST] Failed to parse JSON body: {str(e)}")
        logging.error(f"Raw request data: {request.data}")
        return jsonify({"status": "error", "message": "Invalid JSON provided"}), 400

    # Check if it's a WhatsApp status update
    if (
        body.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("statuses")
    ):
        logging.info("📊 [WEBHOOK POST] Received a WhatsApp status update (message delivered/read/sent)")
        logging.info(f"Status details: {json.dumps(body.get('entry', [{}])[0].get('changes', [{}])[0].get('value', {}), indent=2)}")
        return jsonify({"status": "ok"}), 200

    try:
        logging.info("🔍 [WEBHOOK POST] Validating WhatsApp message structure...")
        if is_valid_whatsapp_message(body):
            logging.info("✅ [WEBHOOK POST] Valid WhatsApp message structure detected")
            logging.info("🔄 [WEBHOOK POST] Starting message processing...")
            process_whatsapp_message(body)
            logging.info("✅ [WEBHOOK POST] Message processed successfully")
            return jsonify({"status": "ok"}), 200
        else:
            # if the request is not a WhatsApp API event, return an error
            logging.warning("❌ [WEBHOOK POST] Invalid WhatsApp message structure - not a recognized WhatsApp API event")
            logging.debug(f"Body structure: {json.dumps(body, indent=2)}")
            return (
                jsonify({"status": "error", "message": "Not a WhatsApp API event"}),
                404,
            )
    except json.JSONDecodeError as e:
        logging.error(f"❌ [WEBHOOK POST] Failed to decode JSON: {str(e)}")
        return jsonify({"status": "error", "message": "Invalid JSON provided"}), 400
    except Exception as e:
        logging.error(f"❌ [WEBHOOK POST] Unexpected error during message processing: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": "Internal server error"}), 500
    finally:
        logging.info("=" * 80)


# Required webhook verifictaion for WhatsApp
def verify():
    logging.info("=" * 80)
    logging.info("🟢 [WEBHOOK VERIFY] Webhook verification request received")
    logging.info(f"Query parameters: {dict(request.args)}")
    
    # Parse params from the webhook verification request
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    logging.info(f"Mode: {mode}")
    logging.info(f"Challenge: {challenge}")
    logging.info(f"Token provided: {'***hidden***' if token else 'None'}")
    
    # Check if a token and mode were sent
    if mode and token:
        # Check the mode and token sent are correct
        if mode == "subscribe" and token == current_app.config["VERIFY_TOKEN"]:
            # Respond with 200 OK and challenge token from the request
            logging.info("✅ [WEBHOOK VERIFY] WEBHOOK_VERIFIED - Token matches!")
            logging.info(f"Returning challenge: {challenge}")
            logging.info("=" * 80)
            return challenge, 200
        else:
            # Responds with '403 Forbidden' if verify tokens do not match
            logging.warning("❌ [WEBHOOK VERIFY] VERIFICATION_FAILED - Token does not match!")
            logging.warning(f"Expected mode: 'subscribe', got: '{mode}'")
            logging.warning(f"Token mismatch - provided token does not match VERIFY_TOKEN in config")
            logging.info("=" * 80)
            return jsonify({"status": "error", "message": "Verification failed"}), 403
    else:
        # Responds with '400 Bad Request' if verify tokens do not match
        logging.warning("❌ [WEBHOOK VERIFY] MISSING_PARAMETER")
        logging.warning(f"Mode provided: {mode}")
        logging.warning(f"Token provided: {token}")
        logging.warning("Missing required parameters for webhook verification")
        logging.info("=" * 80)
        return jsonify({"status": "error", "message": "Missing parameters"}), 400


@webhook_blueprint.route("/webhook", methods=["GET"])
def webhook_get():
    logging.info("🟡 [ROUTE] GET /webhook request routed to verify()")
    return verify()

@webhook_blueprint.route("/webhook", methods=["POST"])
@signature_required
def webhook_post():
    logging.info("🟡 [ROUTE] POST /webhook request routed to handle_message() after signature verification")
    return handle_message()


