"""Chat API Routes for NeoBharat (Phase 5).

Exposes POST /api/chat. Accepts user conversational queries, invokes
the safe explanation pipeline, and returns validated structured responses.
Client-supplied financial metrics, scores, or decisions are strictly ignored.
"""

import logging
from flask import Blueprint, jsonify, request

from backend.services.chat_service import process_chat

logger = logging.getLogger(__name__)

chat_bp = Blueprint("chat_bp", __name__, url_prefix="/api")


@chat_bp.route("/chat", methods=["POST"])
def chat():
    """Handle conversational chat requests.

    Request JSON payload:
        {
            "customer_id": <int>,
            "message": <str>
        }

    Returns:
        200: Validated Phase 4 output structure (LLM explanation or deterministic fallback).
        400: Malformed or missing request fields.
        404: Customer not found.
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON object"}), 400

    customer_id = data.get("customer_id")
    if customer_id is None or not isinstance(customer_id, int) or isinstance(customer_id, bool):
        return jsonify({"error": "Field 'customer_id' is required and must be an integer"}), 400

    user_message = data.get("message")
    if user_message is None or not isinstance(user_message, str) or not user_message.strip():
        return jsonify({"error": "Field 'message' is required and must be a non-empty string"}), 400

    if len(user_message) > 4000:
        return jsonify({"error": "Field 'message' cannot exceed 4000 characters"}), 400

    # Execute safe explanation pipeline
    result = process_chat(customer_id, user_message.strip())
    if result is None:
        return jsonify({"error": f"Customer with ID {customer_id} not found"}), 404

    return jsonify(result), 200
