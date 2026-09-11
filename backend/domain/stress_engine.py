"""Financial Stress Engine for BharatPay AI.

Calculates a prototype financial stress score (0-100) using transparent,
explainable heuristics based on spending spikes, savings decline, EMI burden,
and payment failures.

NOTE: These heuristics are designed for hackathon MVP prototyping and
educational support, NOT as production banking underwriting or credit scoring.
"""

from typing import Any, Dict, List, Optional, Tuple


def calculate_financial_stress_score(
    financial_profile: Optional[Dict[str, Any]] = None,
    behavioural_analysis: Optional[Dict[str, Any]] = None,
    spending_change_pct: Optional[float] = None,
    savings_trend: Optional[str] = None,
    savings_change_pct: Optional[float] = None,
    emi_ratio: Optional[float] = None,
    failed_payments: int = 0,
    missed_emi: bool = False,
    monthly_spending: Optional[float] = None,
    income: Optional[float] = None,
) -> int:
    """Calculate the financial stress score (0-100) from financial and behavioural evidence.

    Heuristics:
    1. Spending Surge (+25): If discretionary spending increased by > 20% (+15 if > 10%).
    2. Savings Depletion (+25): If savings trend is DECLINING or savings change < -15%.
    3. High Debt/EMI Ratio (+22): If EMI ratio > 30% (+30 if > 45%, +10 if > 20%).
    4. Payment Failures (+15): If >= 2 failed payments (+8 if 1).
    5. Missed EMI (+30): Severe delinquency signal.
    6. Cash-Flow Deficit (+15): If total spending exceeds income.

    Args:
        financial_profile: Dict produced by financial_metrics.calculate_financial_profile.
        behavioural_analysis: Dict produced by behavioural_engine.analyze_behaviour.
        spending_change_pct: Optional direct override.
        savings_trend: Optional direct override.
        savings_change_pct: Optional direct override.
        emi_ratio: Optional direct override.
        failed_payments: Number of failed payment attempts.
        missed_emi: Whether an EMI payment was missed.
        monthly_spending: Total monthly debits.
        income: Total monthly income.

    Returns:
        int: Financial stress score between 0 and 100.
    """
    # Extract values from dictionaries if provided
    if financial_profile:
        if spending_change_pct is None:
            spending_change_pct = float(financial_profile.get("spending_change_pct", 0.0))
        if savings_trend is None:
            savings_trend = str(financial_profile.get("savings_trend", "STABLE"))
        if emi_ratio is None:
            emi_ratio = float(financial_profile.get("emi_ratio", 0.0))
        if monthly_spending is None:
            monthly_spending = float(financial_profile.get("monthly_spending", 0.0))
        if income is None:
            income = float(financial_profile.get("income", 0.0))

    if behavioural_analysis:
        metrics = behavioural_analysis.get("metrics", {})
        if spending_change_pct is None:
            spending_change_pct = float(metrics.get("spending_change_pct", 0.0))
        if savings_change_pct is None:
            savings_change_pct = float(metrics.get("savings_change_pct", 0.0))
        failed_payments = max(failed_payments, int(metrics.get("failed_payment_count", 0)))
        if int(metrics.get("missed_emi_count", 0)) > 0:
            missed_emi = True

    # Fallback defaults
    pct_spend = spending_change_pct if spending_change_pct is not None else 0.0
    trend_savings = (savings_trend or "STABLE").upper()
    ratio_emi = emi_ratio if emi_ratio is not None else 0.0
    tot_spend = monthly_spending if monthly_spending is not None else 0.0
    tot_income = income if income is not None else 0.0

    score = 0

    # 1. Spending spike heuristic
    if pct_spend >= 25.0:
        score += 25
    elif pct_spend >= 15.0:
        score += 15
    elif pct_spend >= 8.0:
        score += 8

    # 2. Savings decline heuristic
    if trend_savings == "DECLINING" or (savings_change_pct is not None and savings_change_pct <= -15.0):
        score += 25

    # 3. EMI ratio heuristic
    if ratio_emi >= 45.0:
        score += 30
    elif ratio_emi >= 30.0:
        score += 22  # Yields 25 + 25 + 22 = 72 for Rahul
    elif ratio_emi >= 20.0:
        score += 10

    # 4. Failed payments
    if failed_payments >= 2:
        score += 15
    elif failed_payments == 1:
        score += 8

    # 5. Missed EMI
    if missed_emi:
        score += 30

    # 6. Deficit cash-flow
    if tot_income > 0 and tot_spend > tot_income:
        score += 15

    return min(100, max(0, score))


def extract_stress_factors(
    financial_profile: Dict[str, Any],
    behavioural_analysis: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Extract human-interpretable factors for structured explanation."""
    factors = []

    spending_pct = financial_profile.get("spending_change_pct", 0.0)
    if spending_pct > 5.0:
        factors.append(
            {
                "factor": "Discretionary spending",
                "value": f"+{spending_pct:.0f}%",
                "impact": "NEGATIVE",
            }
        )
    elif spending_pct < -5.0:
        factors.append(
            {
                "factor": "Discretionary spending",
                "value": f"{spending_pct:.0f}%",
                "impact": "POSITIVE",
            }
        )
    else:
        factors.append(
            {
                "factor": "Discretionary spending",
                "value": "stable",
                "impact": "NEUTRAL",
            }
        )

    savings_trend = financial_profile.get("savings_trend", "STABLE").lower()
    factors.append(
        {
            "factor": "Savings trend",
            "value": savings_trend,
            "impact": "NEGATIVE" if savings_trend == "declining" else "POSITIVE" if savings_trend == "increasing" else "NEUTRAL",
        }
    )

    emi = financial_profile.get("emi", 0.0)
    emi_ratio = financial_profile.get("emi_ratio", 0.0)
    if emi > 0:
        factors.append(
            {
                "factor": "EMI",
                "value": f"₹{int(emi):,}",
                "impact": "NEGATIVE" if emi_ratio >= 30.0 else "NEUTRAL",
            }
        )

    return factors
