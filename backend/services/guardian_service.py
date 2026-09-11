"""Financial Guardian Service for BharatPay AI.

Orchestrates:
1. Financial profile calculation
2. Personal baseline behavioural analysis
3. Financial stress scoring
4. Fraud / anomaly risk assessment
5. Payment risk scoring
6. Contextual classification, status assignment, supportive intervention selection,
   and structured explanation assembly.
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
    from backend.domain.behavioural_engine import analyze_behaviour
    from backend.domain.financial_metrics import (
        calculate_financial_profile,
        split_transactions_by_period,
    )
    from backend.domain.fraud_engine import analyze_fraud_risk
    from backend.domain.payment_risk_engine import calculate_payment_risk_score
    from backend.domain.stress_engine import (
        calculate_financial_stress_score,
        extract_stress_factors,
    )
    from backend.repositories.customer_repository import get_customer_by_id
    from backend.repositories.transaction_repository import (
        get_all_transactions_for_customer_ordered,
    )
except ImportError:
    from domain.behavioural_engine import analyze_behaviour
    from domain.financial_metrics import (
        calculate_financial_profile,
        split_transactions_by_period,
    )
    from domain.fraud_engine import analyze_fraud_risk
    from domain.payment_risk_engine import calculate_payment_risk_score
    from domain.stress_engine import (
        calculate_financial_stress_score,
        extract_stress_factors,
    )
    from repositories.customer_repository import get_customer_by_id
    from repositories.transaction_repository import (
        get_all_transactions_for_customer_ordered,
    )


def determine_guardian_classification_and_status(
    stress_score: int,
    fraud_score: int,
    payment_risk_score: int,
    behaviour_score: int,
    savings_trend: str,
    spending_trend: str,
) -> Dict[str, Any]:
    """Determine primary and secondary classifications, status, and recommended intervention."""
    secondary: List[str] = []

    # 1. Check for Suspected Fraud / Major Transaction Anomaly
    if fraud_score >= 65:
        primary = "FRAUD_SUSPECTED"
        if stress_score >= 50:
            secondary.append("FINANCIAL_STRESS")
        if behaviour_score >= 50:
            secondary.append("BEHAVIOUR_CHANGE")

        status = "URGENT_ACTION" if fraud_score >= 85 else "ACTION_RECOMMENDED"
        intervention = {
            "type": "VERIFY_TRANSACTION",
            "action": "VERIFY_SUSPICIOUS_TRANSACTION",
            "priority": "HIGH",
        }
        confidence = 0.95
        summary = "Unusual high-value transaction detected that deviates significantly from personal history."

    # 2. Check for Significant Financial Stress
    elif stress_score >= 60:
        primary = "FINANCIAL_STRESS"
        if behaviour_score >= 50:
            secondary.append("BEHAVIOUR_CHANGE")
        if payment_risk_score >= 50:
            secondary.append("PAYMENT_RISK")

        status = "ACTION_RECOMMENDED" if stress_score >= 85 else "ATTENTION_NEEDED"
        intervention = {
            "type": "SUPPORT",
            "action": "REVIEW_UPCOMING_PAYMENTS",
            "priority": "HIGH",
        }
        confidence = 0.91
        summary = "Recent financial activity differs from the customer's historical pattern."

    # 3. Check for Payment Difficulty Indicators
    elif payment_risk_score >= 60:
        primary = "PAYMENT_RISK"
        if stress_score >= 40:
            secondary.append("FINANCIAL_STRESS")
        if behaviour_score >= 50:
            secondary.append("BEHAVIOUR_CHANGE")

        status = "ATTENTION_NEEDED"
        intervention = {
            "type": "PAYMENT_SUPPORT",
            "action": "REVIEW_UPCOMING_PAYMENTS",
            "priority": "HIGH",
        }
        confidence = 0.89
        summary = "Upcoming payment obligations indicate potential liquidity pressure."

    # 4. Check for General Behavioural Shift (without severe stress)
    elif behaviour_score >= 60:
        primary = "BEHAVIOUR_CHANGE"
        if stress_score >= 40:
            secondary.append("FINANCIAL_STRESS")

        status = "INFORM"
        intervention = {
            "type": "INFORM",
            "action": "MONITOR_SPENDING_SHIFTS",
            "priority": "MEDIUM",
        }
        confidence = 0.88
        summary = "Customer spending or savings patterns have shifted noticeably compared with baseline."

    # 5. Healthy Financial Trend
    elif (savings_trend == "INCREASING" or spending_trend == "STABLE") and stress_score < 30:
        primary = "HEALTHY_FINANCIAL_TREND"
        secondary = ["NO_CONCERN"]
        status = "NO_ACTION"
        intervention = {
            "type": "NO_ACTION",
            "action": "NONE",
            "priority": "LOW",
        }
        confidence = 0.95
        summary = "Financial patterns remain stable, disciplined, and within healthy baselines."

    # 6. Default Benign
    else:
        primary = "NO_CONCERN"
        status = "NO_ACTION"
        intervention = {
            "type": "NO_ACTION",
            "action": "NONE",
            "priority": "LOW",
        }
        confidence = 0.90
        summary = "No anomalous patterns or elevated financial risks identified."

    return {
        "primary": primary,
        "secondary": secondary,
        "status": status,
        "intervention": intervention,
        "confidence": confidence,
        "summary": summary,
    }


def evaluate_guardian(
    customer: Optional[Dict[str, Any]],
    transactions: List[Dict[str, Any]],
    reference_month: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute complete Guardian evaluation from customer data and transactions.

    Args:
        customer: Customer record dictionary.
        transactions: List of customer transactions.
        reference_month: Optional 'YYYY-MM' evaluation month.

    Returns:
        Dict[str, Any]: Full Guardian output strictly matching Phase 2 JSON contract.
    """
    customer_id = customer.get("id") if customer else None
    if not customer_id and transactions:
        customer_id = transactions[0].get("customer_id")

    # 1. Financial Profile
    financial_profile = calculate_financial_profile(
        transactions=transactions,
        customer=customer,
        reference_month=reference_month,
    )

    # 2. Behavioural Analysis
    behavioural_analysis = analyze_behaviour(
        transactions=transactions,
        customer=customer,
        reference_month=reference_month,
    )

    # 3. Period splits for Fraud Engine
    recent_txns, hist_txns = split_transactions_by_period(transactions, reference_month)
    eval_txns = recent_txns if recent_txns else transactions

    # 4. Stress Score
    stress_score = calculate_financial_stress_score(
        financial_profile=financial_profile,
        behavioural_analysis=behavioural_analysis,
    )

    # 5. Fraud Score & Signals
    fraud_result = analyze_fraud_risk(
        recent_transactions=eval_txns,
        historical_transactions=hist_txns,
        customer=customer,
    )
    fraud_score = fraud_result["fraud_score"]

    # 6. Payment Risk Score
    payment_risk_score = calculate_payment_risk_score(
        financial_profile=financial_profile,
        behavioural_analysis=behavioural_analysis,
    )

    # 7. Behaviour Change Score
    behaviour_scores = behavioural_analysis.get("behavioural_scores", {})
    behaviour_change_score = int(behaviour_scores.get("overall_behaviour_change_score", 0))

    # 8. Combine Signals
    all_signals: List[Dict[str, Any]] = []
    # Add behavioural signals
    all_signals.extend(behavioural_analysis.get("signals", []))
    # Add fraud anomaly signals
    all_signals.extend(fraud_result.get("signals", []))

    # 9. Classifications and Status
    decision = determine_guardian_classification_and_status(
        stress_score=stress_score,
        fraud_score=fraud_score,
        payment_risk_score=payment_risk_score,
        behaviour_score=behaviour_change_score,
        savings_trend=financial_profile.get("savings_trend", "STABLE"),
        spending_trend=financial_profile.get("spending_trend", "STABLE"),
    )

    # 10. Explanation Structure
    explanation_factors = extract_stress_factors(financial_profile, behavioural_analysis)

    # Add fraud factor if anomalous transaction present
    if fraud_result["flagged_transactions"]:
        for flagged in fraud_result["flagged_transactions"]:
            flagged_amt = flagged["transaction"]["amount"]
            explanation_factors.insert(
                0,
                {
                    "factor": "Unusual Transaction",
                    "value": f"₹{int(flagged_amt):,}",
                    "impact": "NEGATIVE",
                },
            )

    return {
        "customer_id": customer_id,
        "status": decision["status"],
        "guardian_confidence": decision["confidence"],
        "classification": {
            "primary": decision["primary"],
            "secondary": decision["secondary"],
            "confidence": decision["confidence"],
        },
        "scores": {
            "financial_stress_score": stress_score,
            "fraud_score": fraud_score,
            "payment_risk_score": payment_risk_score,
            "behaviour_change_score": behaviour_change_score,
        },
        "signals": all_signals,
        "recommended_intervention": decision["intervention"],
        "explanation": {
            "summary": decision["summary"],
            "factors": explanation_factors,
        },
    }


def evaluate_customer_by_id(
    customer_id: int,
    reference_month: Optional[str] = None,
) -> Dict[str, Any]:
    """Retrieve customer and transactions from database repositories and evaluate Guardian.

    Args:
        customer_id: ID of the customer in SQLite.
        reference_month: Optional 'YYYY-MM' evaluation month.

    Returns:
        Dict[str, Any]: Full Guardian assessment JSON.
    """
    customer = get_customer_by_id(customer_id)
    transactions = get_all_transactions_for_customer_ordered(customer_id, order="ASC")
    return evaluate_guardian(customer, transactions, reference_month)
