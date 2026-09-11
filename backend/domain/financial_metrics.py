"""Domain module for deterministic financial metric calculations.

This module is strictly independent of Flask, database layers, and external frameworks.
All calculations operate directly on standard Python data structures (dicts/lists).
"""

from typing import Any, Dict, List, Optional, Set, Tuple

# Allowed / expected categories
FIXED_EXPENSE_CATEGORIES: Set[str] = {"BILLS", "EMI"}
DISCRETIONARY_CATEGORIES: Set[str] = {
    "FOOD",
    "SHOPPING",
    "ENTERTAINMENT",
    "TRANSPORT",
}

# Configurable threshold for trend determination (in percentage points)
DEFAULT_TREND_THRESHOLD_PCT: float = 5.0


def calculate_income(transactions: List[Dict[str, Any]]) -> float:
    """Calculate total income from transactions.

    Definition: Total successful CREDIT transactions categorized as SALARY.

    Args:
        transactions: List of transaction dictionaries.

    Returns:
        float: Total salary income rounded to 2 decimal places.
    """
    total = sum(
        float(t["amount"])
        for t in transactions
        if t.get("type") == "CREDIT"
        and t.get("category") == "SALARY"
        and t.get("status", "SUCCESS") == "SUCCESS"
    )
    return round(total, 2)


def calculate_monthly_spending(transactions: List[Dict[str, Any]]) -> float:
    """Calculate total monthly spending.

    Definition: Total successful DEBIT transactions excluding non-expense transfers.

    Args:
        transactions: List of transaction dictionaries.

    Returns:
        float: Total debited expenditure rounded to 2 decimal places.
    """
    total = sum(
        float(t["amount"])
        for t in transactions
        if t.get("type") == "DEBIT"
        and t.get("status", "SUCCESS") == "SUCCESS"
    )
    return round(total, 2)


def calculate_fixed_expenses(transactions: List[Dict[str, Any]]) -> float:
    """Calculate fixed recurring expenses.

    Definition: Successful DEBIT transactions for recurring obligations (BILLS, EMI).

    Args:
        transactions: List of transaction dictionaries.

    Returns:
        float: Total fixed expenses rounded to 2 decimal places.
    """
    total = sum(
        float(t["amount"])
        for t in transactions
        if t.get("type") == "DEBIT"
        and t.get("category") in FIXED_EXPENSE_CATEGORIES
        and t.get("status", "SUCCESS") == "SUCCESS"
    )
    return round(total, 2)


def calculate_discretionary_spending(transactions: List[Dict[str, Any]]) -> float:
    """Calculate discretionary spending.

    Definition: Successful DEBIT transactions for non-essential lifestyle
    categories (FOOD, SHOPPING, ENTERTAINMENT, TRANSPORT).

    Args:
        transactions: List of transaction dictionaries.

    Returns:
        float: Total discretionary expenses rounded to 2 decimal places.
    """
    total = sum(
        float(t["amount"])
        for t in transactions
        if t.get("type") == "DEBIT"
        and t.get("category") in DISCRETIONARY_CATEGORIES
        and t.get("status", "SUCCESS") == "SUCCESS"
    )
    return round(total, 2)


def calculate_emi(transactions: List[Dict[str, Any]]) -> float:
    """Calculate EMI payments.

    Definition: Successful DEBIT transactions specifically categorized as EMI.

    Args:
        transactions: List of transaction dictionaries.

    Returns:
        float: Total EMI payments rounded to 2 decimal places.
    """
    total = sum(
        float(t["amount"])
        for t in transactions
        if t.get("type") == "DEBIT"
        and t.get("category") == "EMI"
        and t.get("status", "SUCCESS") == "SUCCESS"
    )
    return round(total, 2)


def calculate_emi_ratio(monthly_emi: float, monthly_income: float) -> float:
    """Calculate EMI-to-Income ratio as a percentage.

    Formula: (monthly EMI / monthly income) * 100.
    Handles zero income safely by returning 0.0.

    Args:
        monthly_emi: Total monthly EMI amount.
        monthly_income: Total monthly income.

    Returns:
        float: EMI ratio percentage rounded to 1 decimal place.
    """
    if monthly_income <= 0:
        return 0.0
    return round((monthly_emi / monthly_income) * 100.0, 1)


def calculate_estimated_savings(monthly_income: float, monthly_spending: float) -> float:
    """Calculate estimated monthly savings.

    Formula: income - total relevant spending.
    NOTE: This is a synthetic estimate derived from the transaction dataset,
    NOT an actual bank account balance.

    Args:
        monthly_income: Total income for the period.
        monthly_spending: Total relevant spending for the period.

    Returns:
        float: Estimated savings rounded to 2 decimal places.
    """
    return round(monthly_income - monthly_spending, 2)


def calculate_trend(
    recent_value: float,
    historical_value: float,
    threshold_pct: float = DEFAULT_TREND_THRESHOLD_PCT,
) -> Tuple[str, float]:
    """Calculate percentage change and classify trend direction.

    Args:
        recent_value: Value in the recent evaluation period.
        historical_value: Value in the historical baseline period.
        threshold_pct: Absolute percentage difference required to trigger
            INCREASING or DECLINING. Differences within [-threshold, +threshold]
            are classified as STABLE.

    Returns:
        Tuple[str, float]: Trend classification ('INCREASING', 'DECLINING', 'STABLE')
            and the signed percentage change.
    """
    if historical_value == 0:
        if recent_value > 0:
            return "INCREASING", 100.0
        elif recent_value < 0:
            return "DECLINING", -100.0
        else:
            return "STABLE", 0.0

    change_pct = round(((recent_value - historical_value) / abs(historical_value)) * 100.0, 1)

    if change_pct > threshold_pct:
        trend = "INCREASING"
    elif change_pct < -threshold_pct:
        trend = "DECLINING"
    else:
        trend = "STABLE"

    return trend, change_pct


def split_transactions_by_period(
    transactions: List[Dict[str, Any]],
    reference_month: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Split transactions into recent period and historical baseline period.

    Transactions are grouped by month extracted from ISO timestamps ('YYYY-MM').
    The recent period is either the reference_month (if given) or the latest
    month present in the data. The historical period comprises prior transactions.

    Args:
        transactions: Full list of transactions.
        reference_month: Optional 'YYYY-MM' string to designate the recent period.

    Returns:
        Tuple[List[Dict], List[Dict]]: (recent_transactions, historical_transactions).
    """
    if not transactions:
        return [], []

    # Filter transactions that have valid timestamps
    valid_txns = [t for t in transactions if "timestamp" in t and len(str(t["timestamp"])) >= 7]
    if not valid_txns:
        return transactions, []

    if reference_month:
        target_month = reference_month
    else:
        # Find the latest month
        months = [str(t["timestamp"])[:7] for t in valid_txns]
        target_month = max(months)

    recent = [t for t in valid_txns if str(t["timestamp"])[:7] == target_month]
    historical = [t for t in valid_txns if str(t["timestamp"])[:7] < target_month]

    return recent, historical


def calculate_financial_profile(
    transactions: List[Dict[str, Any]],
    customer: Optional[Dict[str, Any]] = None,
    reference_month: Optional[str] = None,
    trend_threshold_pct: float = DEFAULT_TREND_THRESHOLD_PCT,
) -> Dict[str, Any]:
    """Calculate the complete financial profile for a customer.

    Computes deterministic metrics across recent and historical transactions:
    1. income
    2. monthly_spending
    3. fixed_expenses
    4. discretionary_spending
    5. emi
    6. emi_ratio
    7. estimated_savings
    8. spending_trend
    9. savings_trend
    10. spending_change_pct

    Args:
        transactions: List of transaction dictionaries for the customer.
        customer: Optional customer profile dictionary. If transactions contain
            no salary credit, customer['monthly_income'] can be used as fallback.
        reference_month: Optional 'YYYY-MM' string specifying the recent month.
        trend_threshold_pct: Sensitivity threshold for trend classification.

    Returns:
        Dict[str, Any]: Calculated financial metrics structure.
    """
    if not transactions:
        fallback_income = float(customer.get("monthly_income", 0.0)) if customer else 0.0
        fallback_emi = float(customer.get("monthly_emi", 0.0)) if customer else 0.0
        return {
            "income": fallback_income,
            "monthly_spending": 0.0,
            "fixed_expenses": 0.0,
            "discretionary_spending": 0.0,
            "emi": fallback_emi,
            "emi_ratio": calculate_emi_ratio(fallback_emi, fallback_income),
            "estimated_savings": fallback_income,
            "savings_trend": "STABLE",
            "spending_trend": "STABLE",
            "spending_change_pct": 0.0,
        }

    recent_txns, hist_txns = split_transactions_by_period(transactions, reference_month)

    # If all transactions are in a single period, use them as recent
    eval_txns = recent_txns if recent_txns else transactions

    # 1. Income
    income = calculate_income(eval_txns)
    if income == 0.0 and customer and customer.get("monthly_income"):
        income = float(customer["monthly_income"])

    # 2. Monthly spending
    monthly_spending = calculate_monthly_spending(eval_txns)

    # 3. Fixed expenses
    fixed_expenses = calculate_fixed_expenses(eval_txns)

    # 4. Discretionary spending
    discretionary_spending = calculate_discretionary_spending(eval_txns)

    # 5. EMI
    emi = calculate_emi(eval_txns)
    if emi == 0.0 and customer and customer.get("monthly_emi"):
        emi = float(customer["monthly_emi"])

    # 6. EMI ratio
    emi_ratio = calculate_emi_ratio(emi, income)

    # 7. Estimated savings (synthetic estimate)
    estimated_savings = calculate_estimated_savings(income, monthly_spending)

    # 8, 9, 10. Trends and spending change percentage
    if hist_txns:
        # Spending change: Focuses on discretionary spending change (lifestyle change)
        hist_discretionary = calculate_discretionary_spending(hist_txns)
        # If there are multiple historical months, normalize by count of distinct historical months
        hist_months = len(set(str(t["timestamp"])[:7] for t in hist_txns))
        if hist_months > 1:
            hist_discretionary = hist_discretionary / hist_months

        spending_trend, spending_change_pct = calculate_trend(
            discretionary_spending, hist_discretionary, threshold_pct=trend_threshold_pct
        )

        # Historical savings estimate
        hist_income = calculate_income(hist_txns)
        if hist_income == 0.0 and customer and customer.get("monthly_income"):
            hist_income = float(customer["monthly_income"])
        hist_spending = calculate_monthly_spending(hist_txns)
        if hist_months > 1:
            hist_income = hist_income / hist_months
            hist_spending = hist_spending / hist_months

        hist_savings = calculate_estimated_savings(hist_income, hist_spending)
        savings_trend, _ = calculate_trend(
            estimated_savings, hist_savings, threshold_pct=trend_threshold_pct
        )
    else:
        spending_trend = "STABLE"
        spending_change_pct = 0.0
        savings_trend = "STABLE"

    return {
        "income": round(income, 2),
        "monthly_spending": round(monthly_spending, 2),
        "fixed_expenses": round(fixed_expenses, 2),
        "discretionary_spending": round(discretionary_spending, 2),
        "emi": round(emi, 2),
        "emi_ratio": emi_ratio,
        "estimated_savings": round(estimated_savings, 2),
        "savings_trend": savings_trend,
        "spending_trend": spending_trend,
        "spending_change_pct": spending_change_pct,
    }
