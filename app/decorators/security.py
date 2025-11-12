from functools import wraps
from flask import current_app, jsonify, request
import logging
import hashlib
import hmac


def validate_signature(payload, signature):
    """
    Validate the incoming payload's signature against our expected signature
    """
    logging.info("🔐 [SECURITY] Validating request signature...")
    
    try:
        # Use the App Secret to hash the payload
        expected_signature = hmac.new(
            bytes(current_app.config["APP_SECRET"], "latin-1"),
            msg=payload.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

        logging.debug(f"Expected signature: {expected_signature[:20]}...")
        logging.debug(f"Provided signature: {signature[:20]}...")
        
        # Check if the signature matches
        is_valid = hmac.compare_digest(expected_signature, signature)
        
        if is_valid:
            logging.info("✅ [SECURITY] Signature validation successful!")
        else:
            logging.warning("❌ [SECURITY] Signature mismatch!")
            logging.warning(f"Expected: {expected_signature}")
            logging.warning(f"Got: {signature}")
        
        return is_valid
    except Exception as e:
        logging.error(f"❌ [SECURITY] Error during signature validation: {str(e)}", exc_info=True)
        return False


def signature_required(f):
    """
    Decorator to ensure that the incoming requests to our webhook are valid and signed with the correct signature.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        logging.info("=" * 80)
        logging.info("🔐 [SECURITY DECORATOR] Checking request signature...")
        
        try:
            # Extract signature from header
            full_signature = request.headers.get("X-Hub-Signature-256", "")
            logging.debug(f"X-Hub-Signature-256 header: {full_signature[:30]}..." if full_signature else "Header not found")
            
            if not full_signature:
                logging.error("❌ [SECURITY DECORATOR] X-Hub-Signature-256 header is missing!")
                logging.info("=" * 80)
                return jsonify({"status": "error", "message": "Missing signature header"}), 403
            
            # Removing 'sha256=' prefix
            signature = full_signature[7:] if full_signature.startswith("sha256=") else full_signature
            logging.debug(f"Extracted signature: {signature[:20]}...")
            
            # Get raw request data
            request_data = request.data.decode("utf-8")
            logging.debug(f"Request data length: {len(request_data)} bytes")
            
            # Validate signature
            if not validate_signature(request_data, signature):
                logging.error("❌ [SECURITY DECORATOR] Signature verification failed!")
                logging.info("=" * 80)
                return jsonify({"status": "error", "message": "Invalid signature"}), 403
            
            logging.info("✅ [SECURITY DECORATOR] Request passed signature verification")
            logging.info("=" * 80)
            return f(*args, **kwargs)
        
        except Exception as e:
            logging.error(f"❌ [SECURITY DECORATOR] Unexpected error: {str(e)}", exc_info=True)
            logging.info("=" * 80)
            return jsonify({"status": "error", "message": "Signature validation error"}), 403

    return decorated_function
