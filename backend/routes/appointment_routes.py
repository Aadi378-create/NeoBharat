"""Appointment API Routes for NeoBharat.

Provides RESTful endpoints for the Financial Advisor appointment system:
- GET    /api/customers/<id>/appointments
- POST   /api/customers/<id>/appointments
- GET    /api/customers/<id>/advisor-context
- GET    /api/appointments/availability
- GET    /api/appointments/<appointment_id>
- PATCH  /api/appointments/<appointment_id>
- DELETE /api/appointments/<appointment_id>
"""

import logging
from flask import Blueprint, jsonify, request

from backend.services.appointment_service import (
    book_appointment,
    cancel_appointment,
    get_advisor_recommendation_for_customer,
    get_appointment,
    get_available_slots,
    list_customer_appointments,
    reschedule_appointment,
)

logger = logging.getLogger(__name__)

appointment_bp = Blueprint("appointment_bp", __name__, url_prefix="/api")


@appointment_bp.route("/customers/<int:customer_id>/appointments", methods=["GET"])
def get_customer_appointments_route(customer_id: int):
    """List all appointments for a specific customer."""
    try:
        appointments = list_customer_appointments(customer_id)
        return jsonify(appointments), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error("Error retrieving appointments for customer %s: %s", customer_id, e)
        return jsonify({"error": "Failed to retrieve appointments"}), 500


@appointment_bp.route("/customers/<int:customer_id>/appointments", methods=["POST"])
def book_appointment_route(customer_id: int):
    """Book a new financial-advisor appointment for a customer."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a valid JSON object"}), 400

    try:
        appointment = book_appointment(customer_id, data)
        return jsonify(appointment), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error("Unexpected error booking appointment for customer %s: %s", customer_id, e)
        return jsonify({"error": "Internal server error while booking appointment"}), 500


@appointment_bp.route("/customers/<int:customer_id>/advisor-context", methods=["GET"])
def get_customer_advisor_context_route(customer_id: int):
    """Get context-aware advisor recommendation based on backend decision."""
    try:
        context = get_advisor_recommendation_for_customer(customer_id)
        return jsonify(context), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error("Error getting advisor context for customer %s: %s", customer_id, e)
        return jsonify({"error": "Failed to evaluate advisor context"}), 500


@appointment_bp.route("/appointments/availability", methods=["GET"])
def get_availability_route():
    """Get prototype advisor availability for a given date."""
    target_date = request.args.get("date")
    if not target_date:
        return jsonify({"error": "Query parameter 'date' (YYYY-MM-DD) is required"}), 400

    advisor_type = request.args.get("advisor_type", "FINANCIAL_ADVISOR")

    try:
        availability = get_available_slots(target_date, advisor_type)
        return jsonify(availability), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error("Error getting availability for %s: %s", target_date, e)
        return jsonify({"error": "Failed to check availability"}), 500


@appointment_bp.route("/appointments/<appointment_id>", methods=["GET"])
def get_appointment_route(appointment_id: str):
    """Fetch details of a single appointment."""
    appointment = get_appointment(appointment_id)
    if not appointment:
        return jsonify({"error": f"Appointment '{appointment_id}' not found"}), 404
    return jsonify(appointment), 200


@appointment_bp.route("/appointments/<appointment_id>", methods=["PATCH"])
def patch_appointment_route(appointment_id: str):
    """Update or reschedule an appointment."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a valid JSON object"}), 400

    try:
        if "date" in data and "time" in data:
            updated = reschedule_appointment(appointment_id, data["date"], data["time"])
        elif "status" in data:
            from backend.services.appointment_service import update_appointment_status
            updated = update_appointment_status(appointment_id, data["status"], data.get("notes") or data.get("reason"))
        else:
            from backend.repositories.appointment_repository import update_appointment as repo_up
            updated = repo_up(appointment_id, data)

        if not updated:
            return jsonify({"error": f"Appointment '{appointment_id}' not found"}), 404
        return jsonify(updated), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error("Error updating appointment %s: %s", appointment_id, e)
        return jsonify({"error": "Failed to update appointment"}), 500


@appointment_bp.route("/appointments/<appointment_id>", methods=["DELETE"])
def delete_appointment_route(appointment_id: str):
    """Cancel / remove an appointment."""
    reason = request.args.get("reason")
    cancelled = cancel_appointment(appointment_id, reason)
    if not cancelled:
        return jsonify({"error": f"Appointment '{appointment_id}' not found"}), 404
    return jsonify({
        "message": f"Appointment '{appointment_id}' cancelled successfully",
        "appointment": cancelled,
        "status": "CANCELLED",
        "id": appointment_id,
    }), 200
