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
from flask import Blueprint, jsonify

try:
    from backend.domain.financial_metrics import calculate_financial_profile
    from backend.repositories.customer_repository import (
        get_all_customers,
        get_customer_by_id,
    )
    from backend.repositories.transaction_repository import (
        get_all_transactions_for_customer_ordered,
    )
    from backend.services.guardian_service import evaluate_customer_by_id
    from backend.services.recommendation_service import evaluate_recommendation_by_id
except ImportError:
    from domain.financial_metrics import calculate_financial_profile
    from repositories.customer_repository import (
        get_all_customers,
        get_customer_by_id,
    )
    from repositories.transaction_repository import (
        get_all_transactions_for_customer_ordered,
    )
    from services.guardian_service import evaluate_customer_by_id
    from services.recommendation_service import evaluate_recommendation_by_id

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint("dashboard_bp", __name__, url_prefix="/api")


@dashboard_bp.route("/customers", methods=["GET"])
def list_customers():
    """Return all seeded customer records for the customer selector."""
    customers = get_all_customers()
    return jsonify(customers), 200


@dashboard_bp.route("/customers/<int:customer_id>", methods=["GET"])
def get_customer(customer_id: int):
    """Return customer record by ID."""
    customer = get_customer_by_id(customer_id)
    if not customer:
        return jsonify({"error": f"Customer with ID {customer_id} not found"}), 404
    return jsonify(customer), 200


@dashboard_bp.route("/customers/<int:customer_id>/profile", methods=["GET"])
def get_customer_profile(customer_id: int):
    """Return the deterministic financial profile for a customer."""
    customer = get_customer_by_id(customer_id)
    if not customer:
        return jsonify({"error": f"Customer with ID {customer_id} not found"}), 404

    transactions = get_all_transactions_for_customer_ordered(customer_id, order="ASC")
    profile = calculate_financial_profile(transactions, customer)
    return jsonify(profile), 200


@dashboard_bp.route("/customers/<int:customer_id>/guardian", methods=["GET"])
def get_customer_guardian(customer_id: int):
    """Return the deterministic Guardian evaluation for a customer."""
    customer = get_customer_by_id(customer_id)
    if not customer:
        return jsonify({"error": f"Customer with ID {customer_id} not found"}), 404

    guardian_assessment = evaluate_customer_by_id(customer_id)
    return jsonify(guardian_assessment), 200


@dashboard_bp.route("/customers/<int:customer_id>/recommendation", methods=["GET"])
def get_customer_recommendation(customer_id: int):
    """Return the deterministic recommendation and decision for a customer."""
    customer = get_customer_by_id(customer_id)
    if not customer:
        return jsonify({"error": f"Customer with ID {customer_id} not found"}), 404

    recommendation = evaluate_recommendation_by_id(customer_id)
    return jsonify(recommendation), 200
