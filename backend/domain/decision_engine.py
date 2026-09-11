"""Decision Engine for BharatPay AI.

Applies deterministic, customer-benefit policy evaluation and safety gates:
- Verified EMI accounting: monthly_spending includes EMI; estimated_savings is post-EMI surplus.
- Canonical NeoBharat Prototype Safety Heuristics:
  Credit/loan recommendations blocked if ANY of:
  1. financial_stress_score >= 60
  2. payment_risk_score >= 60
  3. fraud_score >= 65
  4. emi_ratio > 35%
  5. net_monthly_surplus <= 0
- Four supported outcomes: RECOMMEND, SUPPORT, VERIFY, NO_RECOMMENDATION.
- Mandatory NO_RECOMMENDATION when no demonstrable customer benefit exists.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Ensure project root and backend dir are in sys.path
_backend_dir = Path(__file__).resolve().parent.parent
_project_root = _backend_dir.parent
for _p in (str(_project_root), str(_backend_dir)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

ALL_PRODUCT_CATEGORIES: Set[str] = {
    "savings",
    "investment/SIP",
    "loan/credit",
    "insurance",
    "credit card",
}

CREDIT_CATEGORIES: Set[str] = {"loan/credit", "credit card"}


def calculate_affordability(financial_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate customer cash flow and debt service capacity.

    CRITICAL EMI ACCOUNTING SAFEGUARD:
    Phase 1 establishes that monthly_spending already includes all successful
    debits, including EMI. estimated_savings = income - monthly_spending.
    Therefore, estimated_savings is ALREADY the post-EMI surplus.
    NEVER subtract EMI from estimated_savings again (doing so would double-count EMI).

    Args:
        financial_profile: Financial profile dict from financial_metrics.

    Returns:
        Dict[str, Any]: Affordability metrics including net surplus and safe capacity.
    """
    income = float(financial_profile.get("income", 0.0))
    monthly_spending = float(financial_profile.get("monthly_spending", 0.0))
    emi = float(financial_profile.get("emi", 0.0))
    emi_ratio = float(financial_profile.get("emi_ratio", 0.0))
    # Post-EMI surplus directly equals estimated_savings
    net_monthly_surplus = float(financial_profile.get("estimated_savings", 0.0))

    # Calculate safe incremental debt capacity only if customer has positive surplus and sustainable debt ratio
    if net_monthly_surplus <= 0 or emi_ratio > 35.0 or income <= 0:
        safe_incremental_debt_capacity = 0.0
    else:
        # Conservative policy heuristic: lesser of 40% surplus or 10% income,
        # strictly capped such that total projected EMI does not exceed 35% of income
        max_by_surplus = net_monthly_surplus * 0.40
        max_by_income = income * 0.10
        capacity = min(max_by_surplus, max_by_income)
        max_allowable_total_emi = income * 0.35
        available_headroom = max(0.0, max_allowable_total_emi - emi)
        safe_incremental_debt_capacity = round(min(capacity, available_headroom), 2)

    return {
        "income": income,
        "monthly_spending": monthly_spending,
        "current_emi": emi,
        "emi_ratio": emi_ratio,
        "net_monthly_surplus": net_monthly_surplus,
        "safe_incremental_debt_capacity": safe_incremental_debt_capacity,
    }


def evaluate_decision(
    guardian_assessment: Dict[str, Any],
    financial_profile: Dict[str, Any],
    customer: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Evaluate customer eligibility, safety gates, and determine decision outcome.

    Outcomes:
    - VERIFY: Suspected unusual activity requires verification before any product action.
    - SUPPORT: High stress or payment difficulty indicators require supportive intervention.
    - RECOMMEND: Customer is financially sound and has an identified beneficial product match.
    - NO_RECOMMENDATION: Mandatory when no clear, demonstrated customer-benefit case exists.

    Args:
        guardian_assessment: Output from guardian_service.evaluate_guardian.
        financial_profile: Output from financial_metrics.calculate_financial_profile.
        customer: Optional customer record dictionary.

    Returns:
        Dict[str, Any]: Structured decision result with outcome, policy reasons, and gates.
    """
    scores = guardian_assessment.get("scores", {})
    classification = guardian_assessment.get("classification", {})
    primary_cls = classification.get("primary", "NO_CONCERN")

    stress_score = int(scores.get("financial_stress_score", 0))
    payment_risk_score = int(scores.get("payment_risk_score", 0))
    fraud_score = int(scores.get("fraud_score", 0))

    affordability = calculate_affordability(financial_profile)
    emi_ratio = affordability["emi_ratio"]
    net_surplus = affordability["net_monthly_surplus"]

    policy_reasons: List[Dict[str, Any]] = []
    blocked_categories: Set[str] = set()
    eligible_categories: Set[str] = set()

    # Canonical NeoBharat Prototype Safety Heuristics:
    # Credit/loan recommendations are blocked if ANY of:
    # 1. financial_stress_score >= 60
    # 2. payment_risk_score >= 60
    # 3. fraud_score >= 65
    # 4. emi_ratio > 35%
    # 5. net_monthly_surplus <= 0
    credit_blocked = False

    if stress_score >= 60:
        credit_blocked = True
        blocked_categories.update(CREDIT_CATEGORIES)
        policy_reasons.append(
            {
                "code": "HIGH_FINANCIAL_STRESS",
                "description": f"Financial stress score of {stress_score} meets NeoBharat Prototype Safety Heuristic (>=60). Credit products blocked.",
                "evidence": {"metric": "financial_stress_score", "value": stress_score, "threshold": 60},
            }
        )

    if payment_risk_score >= 60:
        credit_blocked = True
        blocked_categories.update(CREDIT_CATEGORIES)
        policy_reasons.append(
            {
                "code": "ELEVATED_PAYMENT_DIFFICULTY",
                "description": f"Payment risk score of {payment_risk_score} meets NeoBharat Prototype Safety Heuristic (>=60). Credit products blocked.",
                "evidence": {"metric": "payment_risk_score", "value": payment_risk_score, "threshold": 60},
            }
        )

    if fraud_score >= 65:
        credit_blocked = True
        blocked_categories.update(ALL_PRODUCT_CATEGORIES)  # Suspected fraud blocks ALL commercial products
        policy_reasons.append(
            {
                "code": "SUSPECTED_UNUSUAL_ACTIVITY",
                "description": f"Fraud score of {fraud_score} meets NeoBharat Prototype Safety Heuristic (>=65). All commercial products locked pending verification.",
                "evidence": {"metric": "fraud_score", "value": fraud_score, "threshold": 65},
            }
        )

    if emi_ratio > 35.0:
        credit_blocked = True
        blocked_categories.update(CREDIT_CATEGORIES)
        policy_reasons.append(
            {
                "code": "HIGH_DEBT_RATIO",
                "description": f"EMI ratio of {emi_ratio:.1f}% exceeds NeoBharat Prototype Safety Heuristic (35.0%). Additional debt blocked.",
                "evidence": {"metric": "emi_ratio", "value": emi_ratio, "threshold": 35.0},
            }
        )

    if net_surplus <= 0:
        credit_blocked = True
        blocked_categories.update(CREDIT_CATEGORIES)
        policy_reasons.append(
            {
                "code": "DEFICIT_OR_ZERO_SURPLUS",
                "description": f"Net monthly surplus of ₹{net_surplus:,.2f} indicates zero debt capacity under NeoBharat Prototype Safety Heuristic.",
                "evidence": {"metric": "net_monthly_surplus", "value": net_surplus, "threshold": 0.0},
            }
        )

    # Hierarchical Decision Gates
    # Gate 1: Security / Verification Gate
    if fraud_score >= 65 or primary_cls == "FRAUD_SUSPECTED":
        outcome = "VERIFY"
        action = "VERIFY_SUSPICIOUS_TRANSACTION"
        eligible_categories = set()
        # Ensure incremental debt capacity is zero
        affordability["safe_incremental_debt_capacity"] = 0.0

    # Gate 2: Payment Difficulty Gate
    elif payment_risk_score >= 60 or primary_cls == "PAYMENT_RISK":
        outcome = "SUPPORT"
        action = "REVIEW_UPCOMING_PAYMENTS"
        eligible_categories = set()
        affordability["safe_incremental_debt_capacity"] = 0.0

    # Gate 3: Financial Stress Gate
    elif stress_score >= 60 or primary_cls == "FINANCIAL_STRESS":
        outcome = "SUPPORT"
        action = "REVIEW_UPCOMING_PAYMENTS"
        eligible_categories = set()
        affordability["safe_incremental_debt_capacity"] = 0.0

    # Gate 4: Debt Ratio / Deficit Gate (without acute stress)
    elif credit_blocked:
        # Check if non-credit products provide a customer benefit
        if net_surplus > 1000 and stress_score < 40 and payment_risk_score < 30:
            outcome = "RECOMMEND"
            action = "RECOMMEND_PRODUCT"
            eligible_categories = ALL_PRODUCT_CATEGORIES - CREDIT_CATEGORIES
        else:
            outcome = "NO_RECOMMENDATION"
            action = "NONE"
            eligible_categories = set()
            policy_reasons.append(
                {
                    "code": "NO_SUITABLE_BENEFIT",
                    "description": "Customer cash flow does not support additional product commitments at this time.",
                    "evidence": {"metric": "net_monthly_surplus", "value": net_surplus, "threshold": 1000.0},
                }
            )
        affordability["safe_incremental_debt_capacity"] = 0.0

    # Gate 5: Product Suitability Gate
    else:
        # Customer is healthy; determine eligible categories
        eligible_categories = set(ALL_PRODUCT_CATEGORIES)
        outcome = "RECOMMEND"
        action = "RECOMMEND_PRODUCT"
        policy_reasons.append(
            {
                "code": "HEALTHY_FINANCIAL_STANDING",
                "description": "Customer exhibits healthy savings and low risk scores under NeoBharat Prototype Safety Heuristics.",
                "evidence": {"metric": "financial_stress_score", "value": stress_score, "threshold": 60},
            }
        )

    return {
        "outcome": outcome,
        "action": action,
        "credit_blocked": credit_blocked,
        "eligible_categories": sorted(list(eligible_categories)),
        "blocked_categories": sorted(list(blocked_categories)),
        "policy_reasons": policy_reasons,
        "affordability": affordability,
    }
