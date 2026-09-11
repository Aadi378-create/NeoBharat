"""Recommendation Engine for BharatPay AI.

Translates deterministic decisions into customer-benefit recommendations or guidance:
- Products are strictly designated as "Illustrative Prototype Product".
- Structured fields: product_category, product_name, purpose, illustrative_terms, fees, risk_disclosure.
- No fabricated APR, yield, interest rates, or approval claims.
- Supported actions: RECOMMEND, SUPPORT, VERIFY, NO_RECOMMENDATION.
- Mandatory NO_RECOMMENDATION when no demonstrable customer benefit exists.
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

PROTOTYPE_PRODUCT_CATALOG: Dict[str, Dict[str, Any]] = {
    "investment/SIP": {
        "product_category": "investment/SIP",
        "product_name": "Illustrative Prototype Product: Systematic Wealth Builder SIP",
        "purpose": "Disciplined monthly wealth building into diversified index funds",
        "illustrative_terms": "Illustrative Prototype Product: Monthly contribution scaled to surplus (e.g. ₹2,000–₹5,000/month)",
        "fees": None,
        "risk_disclosure": "Mutual fund investments are subject to market risks. Past performance does not guarantee future returns.",
    },
    "savings": {
        "product_category": "savings",
        "product_name": "Illustrative Prototype Product: Auto-Sweep High-Yield Savings",
        "purpose": "Automatic transfer of surplus cash balance to liquid deposits for emergency reserve",
        "illustrative_terms": "Illustrative Prototype Product: Sweeps idle balance above ₹10,000 into liquid deposits with instant liquidity",
        "fees": None,
        "risk_disclosure": None,
    },
    "loan/credit": {
        "product_category": "loan/credit",
        "product_name": "Illustrative Prototype Product: Responsible Credit Line",
        "purpose": "Pre-approved contingent liquidity line with structured repayment guardrails",
        "illustrative_terms": "Illustrative Prototype Product: Repayment limited strictly to safe incremental debt capacity",
        "fees": None,
        "risk_disclosure": "Borrowing incurs debt obligations. Prompt repayment preserves financial standing.",
    },
    "insurance": {
        "product_category": "insurance",
        "product_name": "Illustrative Prototype Product: Basic Health & Term Shield",
        "purpose": "Protection against unforeseen medical or family financial emergencies",
        "illustrative_terms": "Illustrative Prototype Product: Annual premium coverage scaled to surplus",
        "fees": None,
        "risk_disclosure": "Terms and policy exclusions apply as defined in prototype schedule.",
    },
}


def generate_recommendation(
    decision: Dict[str, Any],
    financial_profile: Dict[str, Any],
    customer: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Assemble customer recommendation payload based on decision outcome.

    Args:
        decision: Decision result from decision_engine.evaluate_decision.
        financial_profile: Profile dictionary from financial_metrics.
        customer: Optional customer record dictionary.

    Returns:
        Dict[str, Any]: Structured recommendation dictionary matching Phase 3 contract.
    """
    outcome = decision.get("outcome", "NO_RECOMMENDATION")
    affordability = decision.get("affordability", {})
    eligible_categories: List[str] = decision.get("eligible_categories", [])
    net_surplus = float(affordability.get("net_monthly_surplus", 0.0))
    savings_trend = str(financial_profile.get("savings_trend", "STABLE")).upper()

    # Case 1: VERIFY
    if outcome == "VERIFY":
        return {
            "action": "VERIFY",
            "product_category": None,
            "product_name": None,
            "purpose": None,
            "illustrative_terms": None,
            "fees": None,
            "risk_disclosure": None,
            "supportive_guidance": {
              "type": "VERIFY_TRANSACTION",
              "action": "VERIFY_SUSPICIOUS_TRANSACTION",
              "priority": "HIGH",
            },
            "suitability_rationale": "Commercial product recommendations are suspended until suspected unusual transaction activity is verified by the customer.",
        }

    # Case 2: SUPPORT
    if outcome == "SUPPORT":
        action_name = decision.get("action", "REVIEW_UPCOMING_PAYMENTS")
        return {
            "action": "SUPPORT",
            "product_category": None,
            "product_name": None,
            "purpose": None,
            "illustrative_terms": None,
            "fees": None,
            "risk_disclosure": None,
            "supportive_guidance": {
              "type": "SUPPORT",
              "action": action_name,
              "priority": "HIGH",
            },
            "suitability_rationale": "Customer exhibits indicators of financial stress or payment difficulty; commercial product recommendations are strictly withheld in favor of supportive financial review.",
        }

    # Case 3: RECOMMEND
    if outcome == "RECOMMEND":
        matched_product = None
        suitability_rationale = ""

        # Match product based on genuine customer benefit:
        # Priority A: If customer has disciplined savings growth and surplus, recommend wealth-building SIP
        if "investment/SIP" in eligible_categories and savings_trend == "INCREASING" and net_surplus >= 5000:
            matched_product = PROTOTYPE_PRODUCT_CATALOG["investment/SIP"]
            suitability_rationale = (
                f"Customer demonstrates established savings discipline and monthly surplus of ₹{net_surplus:,.2f} "
                "suitable for systematic long-term wealth accumulation."
            )
        # Priority B: If customer has surplus but stable/modest savings, recommend liquid auto-sweep
        elif "savings" in eligible_categories and net_surplus > 1000:
            matched_product = PROTOTYPE_PRODUCT_CATALOG["savings"]
            suitability_rationale = (
                f"Customer has surplus monthly cash flow of ₹{net_surplus:,.2f} "
                "suitable for building an emergency liquid reserve with auto-sweep."
            )
        # Priority C: Responsible credit line if customer explicitly has capacity and zero risk
        elif "loan/credit" in eligible_categories and affordability.get("safe_incremental_debt_capacity", 0.0) > 2000:
            matched_product = PROTOTYPE_PRODUCT_CATALOG["loan/credit"]
            suitability_rationale = (
                "Customer exhibits healthy debt metrics and positive cash flow suitable for a contingency credit line."
            )

        if matched_product:
            return {
                "action": "RECOMMEND",
                "product_category": matched_product["product_category"],
                "product_name": matched_product["product_name"],
                "purpose": matched_product["purpose"],
                "illustrative_terms": matched_product["illustrative_terms"],
                "fees": matched_product["fees"],
                "risk_disclosure": matched_product["risk_disclosure"],
                "supportive_guidance": None,
                "suitability_rationale": suitability_rationale,
            }

    # Case 4: NO_RECOMMENDATION (Default if no outcome or no clear customer benefit exists)
    return {
        "action": "NO_RECOMMENDATION",
        "product_category": None,
        "product_name": None,
        "purpose": None,
        "illustrative_terms": None,
        "fees": None,
        "risk_disclosure": None,
        "supportive_guidance": None,
        "suitability_rationale": "No commercial banking product currently identified that provides a clear, demonstrated customer benefit without adding financial pressure.",
    }
