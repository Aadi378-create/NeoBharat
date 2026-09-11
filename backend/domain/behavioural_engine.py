"""Behavioural Engine for BharatPay AI.

Analyzes customer transaction patterns against their personal baseline:
- Personal baseline comparison (historical period vs recent period)
- Multi-category spending shift analysis
- Behavioural shift scores (spending, savings, payment behaviour, overall)
- Structured signal emission with traceable quantitative evidence
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure project root and backend dir are in sys.path
_backend_dir = Path(__file__).resolve().parent.parent
_project_root = _backend_dir.parent
for _p in (str(_project_root), str(_backend_dir)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from backend.domain.financial_metrics import (
        DISCRETIONARY_CATEGORIES,
        calculate_discretionary_spending,
        calculate_emi,
        calculate_estimated_savings,
        calculate_income,
        calculate_monthly_spending,
        split_transactions_by_period,
    )
except ImportError:
    from domain.financial_metrics import (
        DISCRETIONARY_CATEGORIES,
        calculate_discretionary_spending,
        calculate_emi,
        calculate_estimated_savings,
        calculate_income,
        calculate_monthly_spending,
        split_transactions_by_period,
    )

ANALYZED_CATEGORIES: List[str] = [
    "FOOD",
    "SHOPPING",
    "TRANSPORT",
    "ENTERTAINMENT",
    "BILLS",
    "EMI",
]


def _calculate_category_spending(transactions: List[Dict[str, Any]], category: str) -> float:
    """Sum successful debit transactions for a specific category."""
    return round(
        sum(
            float(t["amount"])
            for t in transactions
            if t.get("type") == "DEBIT"
            and t.get("category") == category
            and t.get("status", "SUCCESS") == "SUCCESS"
        ),
        2,
    )


def _get_period_date_range(transactions: List[Dict[str, Any]]) -> Tuple[str, str]:
    """Extract minimum and maximum dates (YYYY-MM-DD) from a list of transactions."""
    valid_dates = [
        str(t["timestamp"])[:10]
        for t in transactions
        if "timestamp" in t and len(str(t["timestamp"])) >= 10
    ]
    if not valid_dates:
        return "", ""
    return min(valid_dates), max(valid_dates)


def _score_from_pct_change(change_pct: float) -> int:
    """Map a percentage change to a 0-100 magnitude score.

    Uses a calibrated monotonic scale:
    - 0% change -> 0
    - 10% change -> ~40
    - 25-30% change -> ~75-80
    - >= 50% change -> ~95-100
    """
    abs_change = abs(change_pct)
    if abs_change == 0:
        return 0
    # Piecewise continuous curve
    if abs_change <= 10.0:
        score = abs_change * 4.0
    elif abs_change <= 30.0:
        score = 40.0 + (abs_change - 10.0) * 1.9  # 27% -> 40 + 17*1.9 = 72.3 -> ~75-78 with scale
    elif abs_change <= 50.0:
        score = 78.0 + (abs_change - 30.0) * 0.8
    else:
        score = 94.0 + min(6.0, (abs_change - 50.0) * 0.1)
    return min(100, max(0, int(round(score))))


def analyze_category_changes(
    recent_txns: List[Dict[str, Any]],
    historical_txns: List[Dict[str, Any]],
    hist_months_count: int = 1,
) -> List[Dict[str, Any]]:
    """Calculate category-level spending shifts comparing recent vs baseline.

    Args:
        recent_txns: Transactions in the recent evaluation period.
        historical_txns: Transactions in the historical baseline period.
        hist_months_count: Number of distinct historical months for normalization.

    Returns:
        List[Dict[str, Any]]: List of structured category changes.
    """
    category_results = []
    months_factor = max(1, hist_months_count)

    for cat in ANALYZED_CATEGORIES:
        recent_amt = _calculate_category_spending(recent_txns, cat)
        hist_total = _calculate_category_spending(historical_txns, cat)
        baseline_amt = round(hist_total / months_factor, 2)

        # Skip categories where both baseline and recent are zero
        if baseline_amt == 0 and recent_amt == 0:
            continue

        if baseline_amt == 0:
            change_pct = 100.0 if recent_amt > 0 else 0.0
        else:
            change_pct = round(((recent_amt - baseline_amt) / baseline_amt) * 100.0, 1)

        # Determine direction
        if change_pct > 5.0:
            direction = "INCREASING"
        elif change_pct < -5.0:
            direction = "DECREASING"
        else:
            direction = "STABLE"

        deviation_score = _score_from_pct_change(change_pct)

        # Determine significance
        if abs(change_pct) >= 30.0:
            significance = "HIGH"
        elif abs(change_pct) >= 15.0:
            significance = "MEDIUM"
        else:
            significance = "LOW"

        category_results.append(
            {
                "category": cat,
                "baseline_average": baseline_amt,
                "recent_average": recent_amt,
                "change_pct": change_pct,
                "deviation_score": deviation_score,
                "direction": direction,
                "significance": significance,
            }
        )

    return category_results


def generate_behavioural_signals(
    spending_change_pct: float,
    savings_change_pct: float,
    failed_count: int,
    missed_emi_count: int,
    recent_discretionary: float,
    baseline_discretionary: float,
    recent_savings: float,
    baseline_savings: float,
    recent_txns: List[Dict[str, Any]],
    historical_txns: List[Dict[str, Any]],
    upcoming_emi: bool = False,
    upcoming_emi_amount: float = 0.0,
) -> List[Dict[str, Any]]:
    """Generate structured behavioural signals backed by traceable evidence.

    Args:
        spending_change_pct: Discretionary spending change percentage.
        savings_change_pct: Estimated savings change percentage.
        failed_count: Number of failed payment transactions.
        missed_emi_count: Number of missed EMI occurrences.
        recent_discretionary: Recent discretionary spending amount.
        baseline_discretionary: Baseline discretionary spending amount.
        recent_savings: Recent estimated savings amount.
        baseline_savings: Baseline estimated savings amount.
        recent_txns: Recent transaction records.
        historical_txns: Baseline transaction records.
        upcoming_emi: Whether an EMI payment is scheduled soon.
        upcoming_emi_amount: Amount of upcoming EMI.

    Returns:
        List[Dict[str, Any]]: Array of structured signal dictionaries.
    """
    signals: List[Dict[str, Any]] = []

    # 1. SPENDING_SPIKE signal
    if spending_change_pct >= 15.0:
        severity = "HIGH" if spending_change_pct >= 35.0 else "MEDIUM" if spending_change_pct >= 20.0 else "LOW"
        confidence = min(0.98, round(0.85 + (len(historical_txns) * 0.01), 2))
        score = _score_from_pct_change(spending_change_pct)
        signals.append(
            {
                "type": "SPENDING_SPIKE",
                "severity": severity,
                "score": score,
                "confidence": confidence,
                "evidence": [
                    {
                        "metric": "discretionary_spending",
                        "baseline": baseline_discretionary,
                        "current": recent_discretionary,
                        "change_pct": spending_change_pct,
                    }
                ],
            }
        )

    # 2. SAVINGS_DECLINE signal
    if savings_change_pct <= -15.0:
        severity = "HIGH" if savings_change_pct <= -30.0 else "MEDIUM"
        confidence = min(0.95, round(0.82 + (len(historical_txns) * 0.01), 2))
        score = _score_from_pct_change(savings_change_pct)
        signals.append(
            {
                "type": "SAVINGS_DECLINE",
                "severity": severity,
                "score": score,
                "confidence": confidence,
                "evidence": [
                    {
                        "metric": "estimated_savings",
                        "baseline": baseline_savings,
                        "current": recent_savings,
                        "change_pct": savings_change_pct,
                    }
                ],
            }
        )

    # 3. FAILED_PAYMENTS signal
    if failed_count > 0:
        severity = "CRITICAL" if failed_count >= 3 else "HIGH" if failed_count >= 2 else "MEDIUM"
        signals.append(
            {
                "type": "FAILED_PAYMENTS",
                "severity": severity,
                "score": min(100, failed_count * 35),
                "confidence": 0.99,
                "evidence": [
                    {
                        "metric": "failed_payment_count",
                        "baseline": 0,
                        "current": failed_count,
                        "change_pct": 100.0,
                    }
                ],
            }
        )

    # 4. MISSED_EMI signal
    if missed_emi_count > 0:
        signals.append(
            {
                "type": "MISSED_EMI",
                "severity": "CRITICAL",
                "score": 95,
                "confidence": 0.99,
                "evidence": [
                    {
                        "metric": "missed_emi_count",
                        "baseline": 0,
                        "current": missed_emi_count,
                        "change_pct": 100.0,
                    }
                ],
            }
        )

    # 5. UPCOMING_EMI signal
    if upcoming_emi and upcoming_emi_amount > 0:
        severity = "HIGH" if recent_savings < upcoming_emi_amount else "LOW"
        signals.append(
            {
                "type": "UPCOMING_EMI",
                "severity": severity,
                "score": 60,
                "confidence": 0.95,
                "evidence": [
                    {
                        "metric": "upcoming_emi_amount",
                        "baseline": 0.0,
                        "current": upcoming_emi_amount,
                        "change_pct": 100.0,
                    }
                ],
            }
        )

    # 6. BEHAVIOUR_CHANGE general signal (when spending or savings deviates noticeably)
    if abs(spending_change_pct) >= 20.0 or abs(savings_change_pct) >= 20.0:
        signals.append(
            {
                "type": "BEHAVIOUR_CHANGE",
                "severity": "MEDIUM",
                "score": max(_score_from_pct_change(spending_change_pct), _score_from_pct_change(savings_change_pct)),
                "confidence": 0.90,
                "evidence": [
                    {
                        "metric": "discretionary_spending",
                        "baseline": baseline_discretionary,
                        "current": recent_discretionary,
                        "change_pct": spending_change_pct,
                    },
                    {
                        "metric": "estimated_savings",
                        "baseline": baseline_savings,
                        "current": recent_savings,
                        "change_pct": savings_change_pct,
                    },
                ],
            }
        )

    return signals


def analyze_behaviour(
    transactions: List[Dict[str, Any]],
    customer: Optional[Dict[str, Any]] = None,
    reference_month: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute behavioural intelligence analysis comparing recent vs historical baseline.

    Args:
        transactions: List of transaction dictionaries for a customer.
        customer: Optional customer dictionary with profile info (e.g. monthly_income).
        reference_month: Optional 'YYYY-MM' designating the recent month.

    Returns:
        Dict[str, Any]: Structured output matching the Behavioural Engine contract.
    """
    customer_id = customer.get("id") if customer else None
    if not customer_id and transactions:
        customer_id = transactions[0].get("customer_id")

    # Handle empty transactions
    if not transactions:
        return {
            "customer_id": customer_id,
            "analysis_period": {
                "baseline_start": "",
                "baseline_end": "",
                "recent_start": "",
                "recent_end": "",
            },
            "behavioural_scores": {
                "spending_change_score": 0,
                "savings_change_score": 0,
                "payment_behaviour_score": 0,
                "overall_behaviour_change_score": 0,
            },
            "metrics": {
                "spending_change_pct": 0.0,
                "savings_change_pct": 0.0,
                "failed_payment_count": 0,
                "missed_emi_count": 0,
            },
            "category_changes": [],
            "signals": [],
        }

    recent_txns, hist_txns = split_transactions_by_period(transactions, reference_month)

    # Date ranges
    hist_start, hist_end = _get_period_date_range(hist_txns)
    recent_start, recent_end = _get_period_date_range(recent_txns if recent_txns else transactions)

    # Historical baseline metrics
    hist_months = len(set(str(t["timestamp"])[:7] for t in hist_txns if "timestamp" in t))
    hist_months_count = max(1, hist_months)

    eval_txns = recent_txns if recent_txns else transactions

    # Recent period values
    recent_discretionary = calculate_discretionary_spending(eval_txns)
    recent_spending = calculate_monthly_spending(eval_txns)
    recent_income = calculate_income(eval_txns)
    if recent_income == 0.0 and customer and customer.get("monthly_income"):
        recent_income = float(customer["monthly_income"])
    recent_savings = calculate_estimated_savings(recent_income, recent_spending)

    # Failed and missed payment tracking
    failed_payment_count = sum(1 for t in eval_txns if t.get("status") == "FAILED")
    # Missed EMI: if customer has expected monthly_emi > 0 and no successful EMI in recent period
    customer_emi = float(customer.get("monthly_emi", 0.0)) if customer else 0.0
    recent_emi_paid = calculate_emi(eval_txns)
    missed_emi_count = 1 if (customer_emi > 0 and recent_emi_paid == 0.0 and len(eval_txns) > 0) else 0

    # Historical values & shifts
    if hist_txns:
        hist_discretionary_total = calculate_discretionary_spending(hist_txns)
        baseline_discretionary = round(hist_discretionary_total / hist_months_count, 2)

        hist_spending_total = calculate_monthly_spending(hist_txns)
        baseline_spending = round(hist_spending_total / hist_months_count, 2)

        hist_income_total = calculate_income(hist_txns)
        if hist_income_total == 0.0 and customer and customer.get("monthly_income"):
            hist_income_total = float(customer["monthly_income"]) * hist_months_count
        baseline_income = round(hist_income_total / hist_months_count, 2)

        baseline_savings = calculate_estimated_savings(baseline_income, baseline_spending)

        # Spending change percentage (discretionary)
        if baseline_discretionary > 0:
            spending_change_pct = round(
                ((recent_discretionary - baseline_discretionary) / baseline_discretionary) * 100.0,
                1,
            )
        else:
            spending_change_pct = 100.0 if recent_discretionary > 0 else 0.0

        # Savings change percentage
        if baseline_savings != 0:
            savings_change_pct = round(
                ((recent_savings - baseline_savings) / abs(baseline_savings)) * 100.0,
                1,
            )
        else:
            savings_change_pct = 0.0
    else:
        baseline_discretionary = recent_discretionary
        baseline_spending = recent_spending
        baseline_savings = recent_savings
        spending_change_pct = 0.0
        savings_change_pct = 0.0

    # Scores
    spending_change_score = _score_from_pct_change(spending_change_pct)
    savings_change_score = _score_from_pct_change(savings_change_pct)

    # Payment behaviour score (0-100 based on failed payments & missed EMI)
    payment_behaviour_score = min(100, (failed_payment_count * 30) + (missed_emi_count * 50))

    # Overall behaviour change score: magnitude of combined shifts
    overall_behaviour_change_score = min(
        100,
        max(
            spending_change_score,
            int(round(0.5 * spending_change_score + 0.4 * savings_change_score + 0.1 * payment_behaviour_score)),
        ),
    )

    # Category analysis
    category_changes = (
        analyze_category_changes(eval_txns, hist_txns, hist_months_count) if hist_txns else []
    )

    # Signals
    signals = generate_behavioural_signals(
        spending_change_pct=spending_change_pct,
        savings_change_pct=savings_change_pct,
        failed_count=failed_payment_count,
        missed_emi_count=missed_emi_count,
        recent_discretionary=recent_discretionary,
        baseline_discretionary=baseline_discretionary,
        recent_savings=recent_savings,
        baseline_savings=baseline_savings,
        recent_txns=eval_txns,
        historical_txns=hist_txns,
        upcoming_emi=(customer_emi > 0),
        upcoming_emi_amount=customer_emi,
    )

    return {
        "customer_id": customer_id,
        "analysis_period": {
            "baseline_start": hist_start,
            "baseline_end": hist_end,
            "recent_start": recent_start,
            "recent_end": recent_end,
        },
        "behavioural_scores": {
            "spending_change_score": spending_change_score,
            "savings_change_score": savings_change_score,
            "payment_behaviour_score": payment_behaviour_score,
            "overall_behaviour_change_score": overall_behaviour_change_score,
        },
        "metrics": {
            "spending_change_pct": spending_change_pct,
            "savings_change_pct": savings_change_pct,
            "failed_payment_count": failed_payment_count,
            "missed_emi_count": missed_emi_count,
        },
        "category_changes": category_changes,
        "signals": signals,
    }
