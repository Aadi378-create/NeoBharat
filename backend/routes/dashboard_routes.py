"""Dashboard API Routes for NeoBharat (Phase 6A).

Exposes existing deterministic backend functionality through thin HTTP endpoints:
- GET /api/customers: List all seeded customer records for the customer selector.
- GET /api/customers/<int:customer_id>: Retrieve a single customer record.
- GET /api/customers/<int:customer_id>/profile: Retrieve pre-calculated financial metrics profile.
- GET /api/customers/<int:customer_id>/guardian: Retrieve pre-evaluated Guardian assessment.
- GET /api/customers/<int:customer_id>/recommendation: Retrieve pre-evaluated Phase 3 recommendation.

These routes are pure serialization adapters. All business and financial calculations
are performed exclusively by existing Phase 1–3 domain engines and services.
"""

import logging
from flask import Blueprint, jsonify, request, session
from datetime import datetime, timezone
from backend.integrations.firebase_client import get_firestore_client


try:
    from backend.domain.financial_metrics import calculate_financial_profile
    from backend.database.connection import get_db_connection
    from backend.repositories.customer_repository import (
        get_all_customers,
        get_customer_by_id, insert_customer,
    )
    from backend.repositories.transaction_repository import (
        get_all_transactions_for_customer_ordered, insert_transaction,
    )
    from backend.services.guardian_service import evaluate_customer_by_id
    from backend.services.recommendation_service import evaluate_recommendation_by_id
except ImportError:
    from domain.financial_metrics import calculate_financial_profile
    from database.connection import get_db_connection
    from repositories.customer_repository import (
        get_all_customers,
        get_customer_by_id, insert_customer,
    )
    from repositories.transaction_repository import (
        get_all_transactions_for_customer_ordered, insert_transaction,
    )
    from services.guardian_service import evaluate_customer_by_id
    from services.recommendation_service import evaluate_recommendation_by_id

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint("dashboard_bp", __name__, url_prefix="/api")

def check_auth(customer_id: int):
    auth_id = session.get("customer_id")
    if not auth_id:
        return jsonify({"error": "Unauthorized"}), 401
    if auth_id != customer_id:
        return jsonify({"error": "Forbidden"}), 403
    return None




@dashboard_bp.route("/customers", methods=["POST"])
def create_customer():
    from flask import current_app
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a valid JSON object"}), 400

    required_fields = ["name", "phone", "pin", "monthly_income"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    pin = str(data["pin"]).strip()
    if not pin.isdigit() or len(pin) != 6:
        return jsonify({"error": "Invalid PIN"}), 400

    from werkzeug.security import generate_password_hash
    pin_hash = generate_password_hash(pin)
    
    customer_data = {
        "name": str(data["name"]),
        "phone": str(data["phone"]),
        "pin_hash": pin_hash,
        "monthly_income": float(data["monthly_income"]),
        "monthly_emi": float(data.get("monthly_emi", 0)),
        "age": int(data.get("age", 25)),
        "language": str(data.get("language", "en")),
        "consent": bool(data.get("consent", True))
    }
    
    db_path = current_app.config.get("DATABASE_PATH")
    
    try:
        conn = get_db_connection(db_path)
        try:
            new_id = insert_customer(customer_data, conn=conn)
            conn.commit()
            
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customers WHERE id = ?", (new_id,))
            row = cursor.fetchone()
            customer_record = dict(row) if row else None
        finally:
            conn.close()
            
        if customer_record and "pin_hash" in customer_record:
            del customer_record["pin_hash"]
            
        try:
            db = get_firestore_client()
            doc_data = {
                "id": new_id,
                "name": customer_record["name"],
                "phone": customer_record["phone"],
                "monthly_income": customer_record["monthly_income"],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            db.collection("customers").document(str(new_id)).set(doc_data)
        except Exception as e:
            logger.warning(f"Firestore sync failed: {e}")
            
        return jsonify(customer_record), 201
    except Exception as e:
        if "UNIQUE constraint failed: customers.phone" in str(e):
            return jsonify({"error": "Phone number already registered"}), 400
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route("/customers/<int:customer_id>/transactions", methods=["POST"])
def add_customer_transaction(customer_id: int):
    from flask import current_app
    auth_err = check_auth(customer_id)
    if auth_err: return auth_err

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a valid JSON object"}), 400

    try:
        amount = float(data.get("amount", -1))
        if amount <= 0: raise ValueError()
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid amount"}), 400

    type_ = data.get("type", "")
    if type_ not in ["CREDIT", "DEBIT"]:
        return jsonify({"error": "Invalid type"}), 400

    VALID_CATEGORIES = {'SALARY', 'FOOD', 'SHOPPING', 'TRANSPORT', 'BILLS', 'EMI', 'ENTERTAINMENT', 'INVESTMENT', 'HEALTH', 'OTHER'}
    cat = str(data.get("category", "OTHER")).upper()
    if cat not in VALID_CATEGORIES:
        cat = "OTHER"

    now_iso = datetime.now(timezone.utc).isoformat()
    txn_data = {
        "customer_id": customer_id,
        "amount": amount,
        "type": type_,
        "category": cat,
        "merchant": data.get("merchant", "Test Merchant"),
        "status": data.get("status", "SUCCESS"),
        "timestamp": data.get("timestamp") or now_iso,
        "created_at": now_iso
    }

    db_path = current_app.config.get("DATABASE_PATH")

    try:
        conn = get_db_connection(db_path)
        try:
            new_id = insert_transaction(txn_data, conn=conn)
            conn.commit()
        finally:
            conn.close()
            
        txn_data["id"] = new_id
        
        try:
            db = get_firestore_client()
            db.collection("customers").document(str(customer_id)).collection("transactions").document(str(new_id)).set(txn_data)
        except Exception as e:
            logger.warning(f"Firestore sync failed: {e}")
            
        return jsonify(txn_data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@dashboard_bp.route("/customers/<int:customer_id>/transactions", methods=["GET"])
def get_customer_transactions(customer_id: int):
    auth_err = check_auth(customer_id)
    if auth_err: return auth_err

    customer = get_customer_by_id(customer_id)
    if not customer:
        return jsonify({"error": f"Customer with ID {customer_id} not found"}), 404

    transactions = get_all_transactions_for_customer_ordered(customer_id, order="DESC")
    return jsonify(transactions), 200


@dashboard_bp.route("/customers", methods=["GET"])
def list_customers():
    """Return all seeded customer records for the customer selector."""
    customers = get_all_customers()
    for c in customers:
        c.pop("pin_hash", None)
        c.pop("pin", None)
    return jsonify(customers), 200


@dashboard_bp.route("/customers/<int:customer_id>", methods=["GET"])
def get_customer(customer_id: int):
    auth_err = check_auth(customer_id)
    if auth_err: return auth_err
    customer = get_customer_by_id(customer_id)
    if not customer:
        return jsonify({"error": f"Customer with ID {customer_id} not found"}), 404
    customer.pop("pin_hash", None)
    customer.pop("pin", None)
    return jsonify(customer), 200


@dashboard_bp.route("/customers/<int:customer_id>/profile", methods=["GET"])
def get_customer_profile(customer_id: int):
    auth_err = check_auth(customer_id)
    if auth_err: return auth_err
    """Return the deterministic financial profile for a customer."""
    customer = get_customer_by_id(customer_id)
    if not customer:
        return jsonify({"error": f"Customer with ID {customer_id} not found"}), 404

    transactions = get_all_transactions_for_customer_ordered(customer_id, order="ASC")
    profile = calculate_financial_profile(transactions, customer)
    return jsonify(profile), 200


@dashboard_bp.route("/customers/<int:customer_id>/guardian", methods=["GET"])
def get_customer_guardian(customer_id: int):
    auth_err = check_auth(customer_id)
    if auth_err: return auth_err
    """Return the deterministic Guardian evaluation for a customer."""
    customer = get_customer_by_id(customer_id)
    if not customer:
        return jsonify({"error": f"Customer with ID {customer_id} not found"}), 404

    guardian_assessment = evaluate_customer_by_id(customer_id)
    return jsonify(guardian_assessment), 200


@dashboard_bp.route("/customers/<int:customer_id>/recommendation", methods=["GET"])
def get_customer_recommendation(customer_id: int):
    auth_err = check_auth(customer_id)
    if auth_err: return auth_err
    """Return the deterministic recommendation and decision for a customer."""
    customer = get_customer_by_id(customer_id)
    if not customer:
        return jsonify({"error": f"Customer with ID {customer_id} not found"}), 404

    recommendation = evaluate_recommendation_by_id(customer_id)
    return jsonify(recommendation), 200
