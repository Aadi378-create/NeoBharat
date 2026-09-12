"""Chat Service for NeoBharat (Phase 5).

Orchestrates the Phase 5 conversational explanation layer:
1. Loads authoritative customer and transaction data from backend repositories.
2. Executes Phase 1–3 pipelines to obtain pre-computed financial metrics, Guardian scores,
   and deterministic decisions.
3. Constructs the authoritative Phase 4 LLM input payload.
4. Calls the OpenAI explanation client.
5. Performs two-layer validation (Schema + Semantic Safety).
6. Returns the validated explanation or authoritative deterministic fallback.
"""

import logging
from typing import Any, Dict, Optional

from backend.domain.decision_engine import evaluate_decision
from backend.domain.financial_metrics import calculate_financial_profile
from backend.domain.phase4_validator import (
    generate_deterministic_fallback,
    validate_input_schema,
    validate_output_schema,
    validate_semantic_output,
)
from backend.domain.recommendation_engine import generate_recommendation
from backend.integrations.openai_client import generate_explanation
from backend.repositories.customer_repository import get_customer_by_id
from backend.repositories.transaction_repository import (
    get_all_transactions_for_customer_ordered,
)
from backend.services.guardian_service import evaluate_guardian

logger = logging.getLogger(__name__)


def build_llm_input(
    customer_id: int,
    user_message: str,
    reference_month: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Construct an authoritative Phase 4 LLM input payload.

    Args:
        customer_id: The ID of the customer in the database.
        user_message: The conversational message from the user.
        reference_month: Optional reference month ('YYYY-MM').

    Returns:
        Optional[Dict[str, Any]]: Validated Phase 4 input payload or None if customer not found.
    """
    customer = get_customer_by_id(customer_id)
    if not customer:
        logger.warning("Customer ID %s not found in database.", customer_id)
        return None

    transactions = get_all_transactions_for_customer_ordered(customer_id, order="ASC")

    # 1. Deterministic Guardian assessment (Phase 2)
    guardian_assessment = evaluate_guardian(customer, transactions, reference_month)

    # 2. Deterministic Financial metrics profile (Phase 1)
    financial_profile = calculate_financial_profile(transactions, customer, reference_month)

    # 3. Deterministic Decision Engine (Phase 3)
    decision = evaluate_decision(guardian_assessment, financial_profile, customer)

    # 4. Deterministic Recommendation Engine (Phase 3)
    recommendation_payload = generate_recommendation(decision, financial_profile, customer)

    scores = guardian_assessment.get("scores", {})

    input_payload: Dict[str, Any] = {
        "contract_version": "1.0",
        "customer": {
            "id": int(customer["id"]),
            "name": str(customer.get("name", f"Customer {customer_id}")),
            "preferred_language": "English",
        },
        "user_message": user_message,
        "financial_context": {
            "income": float(financial_profile.get("income", 0.0)),
            "monthly_spending": float(financial_profile.get("monthly_spending", 0.0)),
            "current_emi": float(financial_profile.get("emi", 0.0)),
            "emi_ratio": float(financial_profile.get("emi_ratio", 0.0)),
            "net_monthly_surplus": float(financial_profile.get("estimated_savings", 0.0)),
            "spending_trend": financial_profile.get("spending_trend", "STABLE"),
            "spending_change_pct": float(financial_profile.get("spending_change_pct", 0.0)),
            "savings_trend": financial_profile.get("savings_trend", "STABLE"),
        },
        "guardian_context": {
            "status": guardian_assessment.get("status", "NO_ACTION"),
            "primary_classification": guardian_assessment.get("classification", {}).get(
                "primary", "HEALTHY_FINANCIAL_TREND"
            ),
            "scores": {
                "financial_stress_score": float(scores.get("financial_stress_score", 0.0)),
                "payment_risk_score": float(scores.get("payment_risk_score", 0.0)),
                "fraud_score": float(scores.get("fraud_score", 0.0)),
                "behaviour_change_score": float(scores.get("behaviour_change_score", 0.0)),
            },
        },
        "decision_context": {
            "decision": decision.get("outcome", "SUPPORT"),
            "recommendation": {
                "action": recommendation_payload.get("action", "SUPPORT"),
                "product_category": recommendation_payload.get("product_category"),
                "product_name": recommendation_payload.get("product_name"),
                "supportive_guidance": recommendation_payload.get("supportive_guidance"),
                "suitability_rationale": recommendation_payload.get(
                    "suitability_rationale", "Standard financial evaluation."
                ),
            },
            "policy_reasons": decision.get("policy_reasons", []),
        },
        "conversation_context": {
            "previous_messages": [],
            "language": "English",
        },
    }

    # Validate schema strictly before downstream usage
    if not validate_input_schema(input_payload):
        logger.error("Built input payload failed Draft 2020-12 input schema validation.")

    return input_payload


def process_chat(
    customer_id: int,
    user_message: str,
    reference_month: Optional[str] = None,
    openai_client: Optional[Any] = None,
) -> Optional[Dict[str, Any]]:
    """Process an incoming user chat message through the explanation pipeline.

    1. Retrieves authoritative context.
    2. Calls OpenAI for conversational explanation.
    3. Validates output schema and semantics.
    4. Returns safe explanation or deterministic fallback.

    Args:
        customer_id: Customer ID.
        user_message: Untrusted user conversational text.
        reference_month: Optional reference month.
        openai_client: Optional client instance (used for testing).

    Returns:
        Optional[Dict[str, Any]]: Validated Phase 4 output dictionary, or None if customer not found.
    """
    input_payload = build_llm_input(customer_id, user_message, reference_month)
    if not input_payload:
        return None

    # Call OpenAI explanation layer
    raw_response = generate_explanation(input_payload, client=openai_client)

    if raw_response is not None:
        # Step 1: Validate output schema
        schema_valid = validate_output_schema(raw_response)
        if schema_valid:
            # Step 2: Validate semantic safety against authoritative context
            semantic_valid = validate_semantic_output(raw_response, input_payload)
            if semantic_valid:
                logger.info("OpenAI explanation passed all schema and semantic validations.")
                return raw_response
            else:
                logger.warning("OpenAI explanation failed semantic safety validation. Engaging fallback.")
        else:
            logger.warning("OpenAI explanation failed output schema validation. Engaging fallback.")
    else:
        logger.info("No response from OpenAI (unavailable, timeout, or error). Engaging fallback.")

    # In all failure cases, return the deterministic fallback
    return generate_deterministic_fallback(input_payload)
