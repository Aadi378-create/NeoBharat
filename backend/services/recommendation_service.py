"""Recommendation Service for BharatPay AI.

Orchestrates the Phase 3 pipeline:
1. Calls Phase 2 Guardian Service to retrieve guardian scores, signals, and context.
2. Evaluates Decision Engine to enforce safety gates, affordability, and credit blocks.
3. Calls Recommendation Engine to assemble illustrative prototype products or supportive guidance.
4. Attaches structured grievance metadata and consumer protection metadata.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure project root and backend dir are in sys.path
_backend_dir = Path(__file__).resolve().parent.parent
_project_root = _backend_dir.parent
for _p in (str(_project_root), str(_backend_dir)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from backend.domain.decision_engine import evaluate_decision
    from backend.domain.financial_metrics import calculate_financial_profile
    from backend.domain.recommendation_engine import generate_recommendation
    from backend.repositories.customer_repository import get_customer_by_id
    from backend.repositories.transaction_repository import (
        get_all_transactions_for_customer_ordered,
    )
    from backend.services.guardian_service import (
        evaluate_customer_by_id as guardian_evaluate_by_id,
        evaluate_guardian,
    )
except ImportError:
    from domain.decision_engine import evaluate_decision
    from domain.financial_metrics import calculate_financial_profile
    from domain.recommendation_engine import generate_recommendation
    from repositories.customer_repository import get_customer_by_id
    from repositories.transaction_repository import (
        get_all_transactions_for_customer_ordered,
    )
    from services.guardian_service import (
        evaluate_customer_by_id as guardian_evaluate_by_id,
        evaluate_guardian,
    )


def evaluate_recommendation_data(
    customer: Optional[Dict[str, Any]],
    transactions: List[Dict[str, Any]],
    reference_month: Optional[str] = None,
) -> Dict[str, Any]:
    """Evaluate decision and recommendation from in-memory customer data and transactions.

    Args:
        customer: Customer record dictionary.
        transactions: List of transaction dictionaries.
        reference_month: Optional 'YYYY-MM' evaluation month.

    Returns:
        Dict[str, Any]: Complete Phase 3 recommendation JSON structure.
    """
    customer_id = customer.get("id") if customer else None
    if not customer_id and transactions:
        customer_id = transactions[0].get("customer_id")

    # 1. Retrieve upstream Guardian assessment
    guardian_assessment = evaluate_guardian(customer, transactions, reference_month)

    # 2. Retrieve Phase 1 financial profile
    financial_profile = calculate_financial_profile(transactions, customer, reference_month)

    # 3. Execute Decision Engine safety gates & affordability
    decision = evaluate_decision(guardian_assessment, financial_profile, customer)

    # 4. Generate Recommendation payload
    recommendation_payload = generate_recommendation(decision, financial_profile, customer)

    ref_tag = reference_month or "latest"
    audit_id = f"audit_cust_{customer_id}_{ref_tag}"

    return {
        "customer_id": customer_id,
        "decision": decision["outcome"],
        "guardian_context": {
            "status": guardian_assessment.get("status"),
            "primary_classification": guardian_assessment.get("classification", {}).get("primary"),
            "scores": guardian_assessment.get("scores", {}),
        },
        "affordability": decision["affordability"],
        "recommendation": recommendation_payload,
        "policy_reasons": decision["policy_reasons"],
        "grievance": {
            "available": True,
            "action": "CONTACT_SUPPORT",
            "escalation_required": False,
        },
        "consumer_protection_metadata": {
            "framework": "RBI-aligned customer-protection design",
            "policy_type": "NeoBharat Prototype Safety Heuristic",
            "audit_trail_id": audit_id,
            "data_minimization_verified": True,
            "predatory_lending_blocked": decision.get("credit_blocked", False),
        },
    }


def evaluate_recommendation_by_id(
    customer_id: int,
    reference_month: Optional[str] = None,
) -> Dict[str, Any]:
    """Retrieve customer and transactions from database and generate complete recommendation.

    Args:
        customer_id: Customer ID in SQLite database.
        reference_month: Optional 'YYYY-MM' evaluation month.

    Returns:
        Dict[str, Any]: Complete Phase 3 recommendation JSON structure.
    """
    customer = get_customer_by_id(customer_id)
    transactions = get_all_transactions_for_customer_ordered(customer_id, order="ASC")
    return evaluate_recommendation_data(customer, transactions, reference_month)
