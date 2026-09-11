"""Payment Risk Engine for BharatPay AI.

Calculates the payment_risk_score (0-100).

DEFINITION & REGULATORY BOUNDARY:
payment_risk_score represents observed indicators of payment difficulty based on:
- payment failures
- missed EMI obligations
- liquidity coverage (upcoming EMI amount vs available estimated savings buffer)
- EMI burden (debt service ratio)

It is NOT a probability of default, credit score, or lending decision.

Differentiated from Financial Stress:
- Stress measures macro financial pressure and lifestyle inflation.
- Payment Risk specifically captures observed operational friction and cash-flow
  coverage for upcoming payment obligations.
"""

from typing import Any, Dict, Optional


def calculate_payment_risk_score(
    financial_profile: Optional[Dict[str, Any]] = None,
    behavioural_analysis: Optional[Dict[str, Any]] = None,
    failed_payments: int = 0,
    missed_emi: bool = False,
    upcoming_emi_amount: float = 0.0,
    estimated_savings: float = 0.0,
    emi_ratio: float = 0.0,
) -> int:
    """Calculate the payment risk score (0-100).

    payment_risk_score represents observed indicators of payment difficulty based
    on payment failures, missed EMI obligations, liquidity coverage, and EMI burden.
    It is not a probability of default, credit score, or lending decision.

    Args:
        financial_profile: Profile dictionary from financial_metrics.
        behavioural_analysis: Analysis dictionary from behavioural_engine.
        failed_payments: Count of failed transactions.
        missed_emi: Whether an EMI payment was missed.
        upcoming_emi_amount: Amount of upcoming EMI due.
        estimated_savings: Recent estimated monthly savings.
        emi_ratio: Monthly EMI to income percentage.

    Returns:
        int: Payment risk score between 0 and 100.
    """
    if financial_profile:
        if estimated_savings == 0.0:
            estimated_savings = float(financial_profile.get("estimated_savings", 0.0))
        if emi_ratio == 0.0:
            emi_ratio = float(financial_profile.get("emi_ratio", 0.0))
        if upcoming_emi_amount == 0.0:
            upcoming_emi_amount = float(financial_profile.get("emi", 0.0))

    if behavioural_analysis:
        metrics = behavioural_analysis.get("metrics", {})
        failed_payments = max(failed_payments, int(metrics.get("failed_payment_count", 0)))
        if int(metrics.get("missed_emi_count", 0)) > 0:
            missed_emi = True

    score = 0

    # 1. Past failures and delinquencies (direct risk evidence)
    if missed_emi:
        score += 45
    if failed_payments >= 2:
        score += 35
    elif failed_payments == 1:
        score += 20

    # 2. Upcoming payment liquidity buffer
    if upcoming_emi_amount > 0:
        if estimated_savings < 0:
            # Deficit: customer has negative net monthly flow before upcoming payment
            score += 35
        elif estimated_savings < upcoming_emi_amount:
            # Insufficient buffer: monthly savings cannot cover full next EMI payment
            score += 28
        elif estimated_savings < upcoming_emi_amount * 1.5:
            # Thin buffer
            score += 15

    # 3. Debt burden
    if emi_ratio >= 45.0:
        score += 25
    elif emi_ratio >= 30.0:
        score += 18
    elif emi_ratio >= 20.0:
        score += 8

    # 4. Lifestyle spending pressure
    if financial_profile:
        spending_change = float(financial_profile.get("spending_change_pct", 0.0))
        if spending_change >= 25.0 and estimated_savings < upcoming_emi_amount:
            score += 15

    return min(100, max(0, score))
