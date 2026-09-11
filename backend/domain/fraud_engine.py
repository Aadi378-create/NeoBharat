"""Fraud Engine for BharatPay AI.

Detects statistical transaction anomalies and outputs a fraud score (0-100).

CRITICAL ETHICAL & ARCHITECTURAL RULE:
Anomalies represent "SUSPECTED UNUSUAL ACTIVITY", NEVER "CONFIRMED FRAUD".
The system must never declare fraud as confirmed.
"""

from typing import Any, Dict, List, Optional, Tuple


def _calculate_stats(values: List[float]) -> Tuple[float, float, float]:
    """Calculate mean, standard deviation, and maximum of a list of floats."""
    if not values:
        return 0.0, 0.0, 0.0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    std = variance ** 0.5
    return round(mean, 2), round(std, 2), max(values)


def analyze_fraud_risk(
    recent_transactions: List[Dict[str, Any]],
    historical_transactions: List[Dict[str, Any]],
    customer: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Analyze transactions for anomalous deviations against historical baseline.

    Args:
        recent_transactions: List of recent transactions.
        historical_transactions: Baseline historical transactions.
        customer: Optional customer profile.

    Returns:
        Dict[str, Any]: Structured fraud risk assessment containing:
            - fraud_score (0-100)
            - anomaly_status ("SUSPECTED UNUSUAL ACTIVITY" or "NO_ANOMALY_DETECTED")
            - flagged_transactions
            - signals (list of UNUSUAL_TRANSACTION signals with structured evidence)
    """
    hist_debits = [
        float(t["amount"])
        for t in historical_transactions
        if t.get("type") == "DEBIT" and t.get("status", "SUCCESS") == "SUCCESS"
    ]
    recent_debits = [
        t
        for t in recent_transactions
        if t.get("type") == "DEBIT" and t.get("status", "SUCCESS") == "SUCCESS"
    ]

    # Baseline calculations
    if not hist_debits:
        # If no baseline exists, default to benign low baseline
        return {
            "fraud_score": 0,
            "anomaly_status": "NO_ANOMALY_DETECTED",
            "flagged_transactions": [],
            "signals": [],
        }

    mean_debit, std_debit, max_debit = _calculate_stats(hist_debits)

    flagged_transactions = []
    signals = []
    highest_severity_score = 0

    for txn in recent_debits:
        amt = float(txn["amount"])
        # Check if amount is extraordinarily high compared to customer's personal history
        # Condition: Amount exceeds 3x max historical debit or 6x historical mean
        multiplier_vs_max = round(amt / max_debit, 1) if max_debit > 0 else 1.0
        multiplier_vs_mean = round(amt / mean_debit, 1) if mean_debit > 0 else 1.0

        if (multiplier_vs_max >= 2.5 and amt > 20000.0) or multiplier_vs_mean >= 5.0:
            deviation_pct = round(((amt - max_debit) / max_debit) * 100.0, 1)
            severity = "CRITICAL" if multiplier_vs_max >= 5.0 else "HIGH"
            txn_score = min(98, max(65, int(60 + min(35, multiplier_vs_max * 4))))
            highest_severity_score = max(highest_severity_score, txn_score)

            flagged_transactions.append(
                {
                    "transaction": txn,
                    "reason": "Transaction amount significantly exceeds personal historical maximum",
                    "baseline_max": max_debit,
                    "multiplier_vs_max": multiplier_vs_max,
                }
            )

            signals.append(
                {
                    "type": "UNUSUAL_TRANSACTION",
                    "severity": severity,
                    "score": txn_score,
                    "confidence": 0.95,
                    "evidence": [
                        {
                            "metric": "transaction_amount",
                            "baseline": max_debit,
                            "current": amt,
                            "change_pct": deviation_pct,
                        }
                    ],
                }
            )

    if flagged_transactions:
        fraud_score = highest_severity_score
        anomaly_status = "SUSPECTED UNUSUAL ACTIVITY"
    else:
        # Base benign noise score (0 - 10)
        fraud_score = min(10, len(recent_debits))
        anomaly_status = "NO_ANOMALY_DETECTED"

    return {
        "fraud_score": fraud_score,
        "anomaly_status": anomaly_status,
        "flagged_transactions": flagged_transactions,
        "signals": signals,
    }
