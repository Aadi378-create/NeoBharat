import logging
from flask import Blueprint, jsonify, request, session, current_app
from werkzeug.security import check_password_hash

try:
    from backend.repositories.customer_repository import get_customer_by_phone
except ImportError:
    from repositories.customer_repository import get_customer_by_phone

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/auth")

@auth_bp.route("/login", methods=["POST"])
def login():
    """Login a customer with phone and PIN."""
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "Request body must be a valid JSON object"}), 400

        phone = str(data.get("phone", "")).strip()
        pin = str(data.get("pin", "")).strip()

        if not phone or not pin:
            return jsonify({"error": "Phone and PIN are required"}), 400

        # Ensure PIN isn't malformed
        if not pin.isdigit() or len(pin) != 6:
            return jsonify({"error": "Invalid credentials"}), 401

        customer = get_customer_by_phone(phone, db_path=current_app.config.get("DATABASE_PATH"))
        if not customer:
            return jsonify({"error": "Invalid credentials"}), 401

        pin_hash = customer.get("pin_hash")
        if not pin_hash or not check_password_hash(pin_hash, pin):
            return jsonify({"error": "Invalid credentials"}), 401

        # Safe subset for frontend
        safe_customer = {
            "id": customer["id"],
            "name": customer["name"],
            "age": customer.get("age"),
            "language": customer.get("language", "en"),
            "monthly_income": customer.get("monthly_income"),
            "monthly_emi": customer.get("monthly_emi"),
            "phone": customer.get("phone"),
            "created_at": customer.get("created_at"),
        }
        
        session["customer_id"] = customer["id"]

        return jsonify({"customer": safe_customer}), 200
    except Exception as e:
        logger.exception("Login error: %s", e)
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/logout", methods=["POST"])
def logout():
    try:
        session.clear()
        return jsonify({"status": "logged_out"}), 200
    except Exception as e:
        logger.exception("Logout error: %s", e)
        return jsonify({"error": str(e)}), 500
