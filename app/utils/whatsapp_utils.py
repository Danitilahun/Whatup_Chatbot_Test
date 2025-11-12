import logging
from flask import current_app, jsonify
import json
import requests

# from app.services.openai_service import generate_response
import re


def log_http_response(response):
    logging.info("📨 [HTTP RESPONSE] WhatsApp API Response:")
    logging.info(f"  Status Code: {response.status_code}")
    logging.info(f"  Content-Type: {response.headers.get('content-type')}")
    logging.info(f"  Response Body: {response.text}")
    if response.status_code >= 400:
        logging.error(f"❌ [HTTP RESPONSE] Error response from WhatsApp API!")
    else:
        logging.info(f"✅ [HTTP RESPONSE] Successful response from WhatsApp API!")


def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )


def generate_response(response):
    # Return text in uppercase
    return response.upper()


def send_message(data):
    logging.info("=" * 80)
    logging.info("📤 [SEND MESSAGE] Preparing to send message to WhatsApp API")
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }
    
    logging.debug(f"Headers: {{'Content-type': 'application/json', 'Authorization': 'Bearer ***hidden***'}}")

    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"
    logging.info(f"📍 API Endpoint: {url}")
    
    try:
        logging.info(f"Message payload: {data}")
        logging.info("🔄 [SEND MESSAGE] Sending POST request to WhatsApp API...")
        
        response = requests.post(
            url, data=data, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        
        logging.info(f"📥 [SEND MESSAGE] Response received from WhatsApp API")
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        
    except requests.Timeout:
        logging.error("❌ [SEND MESSAGE] Timeout occurred while sending message (10s timeout exceeded)")
        logging.info("=" * 80)
        return jsonify({"status": "error", "message": "Request timed out"}), 408
        
    except requests.ConnectionError as e:
        logging.error(f"❌ [SEND MESSAGE] Connection error while sending message: {str(e)}")
        logging.error(f"Could not connect to WhatsApp API at: {url}")
        logging.info("=" * 80)
        return jsonify({"status": "error", "message": "Connection error"}), 500
        
    except requests.HTTPError as e:
        logging.error(f"❌ [SEND MESSAGE] HTTP error occurred: {str(e)}")
        logging.error(f"Response status: {response.status_code}")
        logging.error(f"Response text: {response.text}")
        logging.info("=" * 80)
        return jsonify({"status": "error", "message": "HTTP error from WhatsApp API"}), 500
        
    except (requests.RequestException) as e:  # This will catch any general request exception
        logging.error(f"❌ [SEND MESSAGE] Request failed: {str(e)}")
        logging.info("=" * 80)
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
        
    else:
        # Process the response as normal
        log_http_response(response)
        logging.info("=" * 80)
        return response


def process_text_for_whatsapp(text):
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text


def process_whatsapp_message(body):
    logging.info("=" * 80)
    logging.info("🔄 [PROCESS MESSAGE] Starting WhatsApp message processing...")
    
    try:
        # Extract sender information
        logging.info("📋 [PROCESS MESSAGE] Extracting sender information...")
        wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
        name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]
        logging.info(f"✅ Sender: {name} (WhatsApp ID: {wa_id})")
        
        # Extract message content
        logging.info("📋 [PROCESS MESSAGE] Extracting message content...")
        message = body["entry"][0]["changes"][0]["value"]["messages"][0]
        message_id = message.get("id", "unknown")
        message_timestamp = message.get("timestamp", "unknown")
        message_body = message["text"]["body"]
        logging.info(f"✅ Message ID: {message_id}")
        logging.info(f"✅ Message timestamp: {message_timestamp}")
        logging.info(f"📝 Message content: '{message_body}'")
        
        # Generate response
        logging.info("🧠 [PROCESS MESSAGE] Generating response...")
        response = generate_response(message_body)
        logging.info(f"✅ Response generated: '{response}'")

        # OpenAI Integration
        # response = generate_response(message_body, wa_id, name)
        # response = process_text_for_whatsapp(response)

        # Prepare message payload
        logging.info("📦 [PROCESS MESSAGE] Preparing message payload...")
        recipient = current_app.config["RECIPIENT_WAID"]
        logging.info(f"📍 Recipient: {recipient}")
        
        data = get_text_message_input(recipient, response)
        logging.info(f"✅ Payload prepared: {data}")
        
        # Send the response message
        logging.info("📤 [PROCESS MESSAGE] Sending response message...")
        send_message(data)
        
        logging.info("✅ [PROCESS MESSAGE] Message processing completed successfully!")
        logging.info("=" * 80)
        
    except KeyError as e:
        logging.error(f"❌ [PROCESS MESSAGE] Missing key in message structure: {str(e)}")
        logging.error(f"Message body structure: {json.dumps(body, indent=2)}")
        logging.info("=" * 80)
        raise
    except Exception as e:
        logging.error(f"❌ [PROCESS MESSAGE] Unexpected error while processing message: {str(e)}", exc_info=True)
        logging.info("=" * 80)
        raise


def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    logging.info("🔍 [VALIDATION] Checking message structure validity...")
    
    # Check each part of the structure with detailed logging
    checks = [
        ("object field", body.get("object")),
        ("entry field", body.get("entry")),
        ("entry[0] exists", body.get("entry") and body["entry"][0] if body.get("entry") else False),
        ("changes field", body.get("entry") and body["entry"][0].get("changes") if body.get("entry") else False),
        ("changes[0] exists", body.get("entry") and body["entry"][0].get("changes") and body["entry"][0]["changes"][0] if body.get("entry") and body["entry"][0].get("changes") else False),
        ("value field", body.get("entry") and body["entry"][0].get("changes") and body["entry"][0]["changes"][0].get("value") if body.get("entry") and body["entry"][0].get("changes") else False),
        ("messages field", body.get("entry") and body["entry"][0].get("changes") and body["entry"][0]["changes"][0].get("value") and body["entry"][0]["changes"][0]["value"].get("messages") if body.get("entry") and body["entry"][0].get("changes") and body["entry"][0]["changes"][0].get("value") else False),
        ("messages[0] exists", body.get("entry") and body["entry"][0].get("changes") and body["entry"][0]["changes"][0].get("value") and body["entry"][0]["changes"][0]["value"].get("messages") and body["entry"][0]["changes"][0]["value"]["messages"][0] if body.get("entry") and body["entry"][0].get("changes") and body["entry"][0]["changes"][0].get("value") and body["entry"][0]["changes"][0]["value"].get("messages") else False),
    ]
    
    for check_name, check_result in checks:
        status = "✅" if check_result else "❌"
        logging.debug(f"  {status} {check_name}: {check_result}")
    
    is_valid = (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )
    
    if is_valid:
        logging.info("✅ [VALIDATION] Message structure is valid!")
    else:
        logging.warning("❌ [VALIDATION] Message structure is INVALID!")
    
    return is_valid
