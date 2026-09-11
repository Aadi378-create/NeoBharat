"""Unit tests for deterministic financial metric calculations.

Tests use small, controlled synthetic datasets independent of database and seed data.
"""

import unittest

from backend.domain.financial_metrics import (
    calculate_discretionary_spending,
    calculate_emi,
    calculate_emi_ratio,
    calculate_estimated_savings,
    calculate_financial_profile,
    calculate_fixed_expenses,
    calculate_income,
    calculate_monthly_spending,
    calculate_trend,
    split_transactions_by_period,
)


class TestFinancialMetrics(unittest.TestCase):
    """Test suite for financial metric calculations and trend classifications."""

    def test_1_income_calculation(self):
        """Test that income only includes successful CREDIT transactions categorized as SALARY."""
        txns = [
            {"amount": 50000.0, "type": "CREDIT", "category": "SALARY", "status": "SUCCESS"},
            {"amount": 2000.0, "type": "CREDIT", "category": "OTHER", "status": "SUCCESS"},  # Not salary
            {"amount": 50000.0, "type": "CREDIT", "category": "SALARY", "status": "FAILED"},  # Failed
            {"amount": 10000.0, "type": "DEBIT", "category": "SALARY", "status": "SUCCESS"},  # Debit
        ]
        income = calculate_income(txns)
        self.assertEqual(income, 50000.0)

    def test_2_expense_calculation(self):
        """Test that monthly spending only includes successful DEBIT transactions."""
        txns = [
            {"amount": 1500.0, "type": "DEBIT", "category": "FOOD", "status": "SUCCESS"},
            {"amount": 3500.0, "type": "DEBIT", "category": "BILLS", "status": "SUCCESS"},
            {"amount": 2000.0, "type": "DEBIT", "category": "SHOPPING", "status": "FAILED"},  # Failed
            {"amount": 5000.0, "type": "DEBIT", "category": "ENTERTAINMENT", "status": "PENDING"},  # Pending
            {"amount": 25000.0, "type": "CREDIT", "category": "SALARY", "status": "SUCCESS"},  # Credit
        ]
        spending = calculate_monthly_spending(txns)
        self.assertEqual(spending, 5000.0)

    def test_3_discretionary_spending(self):
        """Test discretionary spending calculation (FOOD, SHOPPING, ENTERTAINMENT, TRANSPORT)."""
        txns = [
            {"amount": 1200.0, "type": "DEBIT", "category": "FOOD", "status": "SUCCESS"},
            {"amount": 800.0, "type": "DEBIT", "category": "SHOPPING", "status": "SUCCESS"},
            {"amount": 500.0, "type": "DEBIT", "category": "TRANSPORT", "status": "SUCCESS"},
            {"amount": 500.0, "type": "DEBIT", "category": "ENTERTAINMENT", "status": "SUCCESS"},
            {"amount": 10000.0, "type": "DEBIT", "category": "BILLS", "status": "SUCCESS"},  # Non-discretionary
            {"amount": 7000.0, "type": "DEBIT", "category": "EMI", "status": "SUCCESS"},  # Non-discretionary
        ]
        discretionary = calculate_discretionary_spending(txns)
        self.assertEqual(discretionary, 3000.0)

    def test_4_emi_calculation(self):
        """Test EMI calculation only sums successful EMI debits."""
        txns = [
            {"amount": 14000.0, "type": "DEBIT", "category": "EMI", "status": "SUCCESS"},
            {"amount": 5000.0, "type": "DEBIT", "category": "EMI", "status": "FAILED"},
            {"amount": 5000.0, "type": "DEBIT", "category": "BILLS", "status": "SUCCESS"},
        ]
        emi = calculate_emi(txns)
        self.assertEqual(emi, 14000.0)

    def test_5_emi_ratio(self):
        """Test EMI ratio calculation (monthly EMI / monthly income * 100)."""
        # Rahul scenario: 14000 / 45000 * 100 = 31.111... -> 31.1%
        ratio = calculate_emi_ratio(14000.0, 45000.0)
        self.assertEqual(ratio, 31.1)

        # 10000 / 50000 * 100 = 20.0%
        self.assertEqual(calculate_emi_ratio(10000.0, 50000.0), 20.0)

    def test_6_savings_estimate(self):
        """Test estimated savings calculation (income - spending)."""
        savings = calculate_estimated_savings(45000.0, 38000.0)
        self.assertEqual(savings, 7000.0)

        # Deficit spending
        deficit = calculate_estimated_savings(20000.0, 25000.0)
        self.assertEqual(deficit, -5000.0)

    def test_7_increasing_spending_trend(self):
        """Test increasing spending trend classification and ~27% change detection."""
        hist_spending = 7087.0
        recent_spending = 9000.0
        trend, change_pct = calculate_trend(recent_spending, hist_spending, threshold_pct=5.0)
        self.assertEqual(trend, "INCREASING")
        self.assertEqual(change_pct, 27.0)

    def test_8_declining_savings_trend(self):
        """Test declining savings trend classification."""
        hist_savings = 10000.0
        recent_savings = 7000.0
        trend, change_pct = calculate_trend(recent_savings, hist_savings, threshold_pct=5.0)
        self.assertEqual(trend, "DECLINING")
        self.assertEqual(change_pct, -30.0)

    def test_9_stable_behaviour(self):
        """Test stable trend within the threshold boundary."""
        hist_val = 5000.0
        recent_val = 5100.0  # +2.0% change (within 5% threshold)
        trend, change_pct = calculate_trend(recent_val, hist_val, threshold_pct=5.0)
        self.assertEqual(trend, "STABLE")
        self.assertEqual(change_pct, 2.0)

    def test_10_zero_income_handling(self):
        """Test that zero income does not cause ZeroDivisionError and safely returns 0.0."""
        ratio = calculate_emi_ratio(5000.0, 0.0)
        self.assertEqual(ratio, 0.0)

        ratio_negative = calculate_emi_ratio(5000.0, -100.0)
        self.assertEqual(ratio_negative, 0.0)

    def test_11_empty_transaction_handling(self):
        """Test safe handling when transaction list is empty."""
        profile = calculate_financial_profile([])
        self.assertEqual(profile["income"], 0.0)
        self.assertEqual(profile["monthly_spending"], 0.0)
        self.assertEqual(profile["fixed_expenses"], 0.0)
        self.assertEqual(profile["discretionary_spending"], 0.0)
        self.assertEqual(profile["emi"], 0.0)
        self.assertEqual(profile["emi_ratio"], 0.0)
        self.assertEqual(profile["estimated_savings"], 0.0)
        self.assertEqual(profile["spending_trend"], "STABLE")
        self.assertEqual(profile["savings_trend"], "STABLE")
        self.assertEqual(profile["spending_change_pct"], 0.0)

    def test_12_complete_profile_structure(self):
        """Test full profile output against expected schema."""
        txns = [
            # August baseline
            {"timestamp": "2026-08-01", "amount": 50000.0, "type": "CREDIT", "category": "SALARY", "status": "SUCCESS"},
            {"timestamp": "2026-08-05", "amount": 10000.0, "type": "DEBIT", "category": "EMI", "status": "SUCCESS"},
            {"timestamp": "2026-08-10", "amount": 5000.0, "type": "DEBIT", "category": "BILLS", "status": "SUCCESS"},
            {"timestamp": "2026-08-15", "amount": 10000.0, "type": "DEBIT", "category": "FOOD", "status": "SUCCESS"},
            # September evaluation
            {"timestamp": "2026-09-01", "amount": 50000.0, "type": "CREDIT", "category": "SALARY", "status": "SUCCESS"},
            {"timestamp": "2026-09-05", "amount": 10000.0, "type": "DEBIT", "category": "EMI", "status": "SUCCESS"},
            {"timestamp": "2026-09-10", "amount": 5000.0, "type": "DEBIT", "category": "BILLS", "status": "SUCCESS"},
            {"timestamp": "2026-09-15", "amount": 13000.0, "type": "DEBIT", "category": "FOOD", "status": "SUCCESS"},
        ]
        profile = calculate_financial_profile(txns)

        expected_keys = {
            "income",
            "monthly_spending",
            "fixed_expenses",
            "discretionary_spending",
            "emi",
            "emi_ratio",
            "estimated_savings",
            "savings_trend",
            "spending_trend",
            "spending_change_pct",
        }
        self.assertEqual(set(profile.keys()), expected_keys)
        self.assertEqual(profile["income"], 50000.0)
        self.assertEqual(profile["monthly_spending"], 28000.0)
        self.assertEqual(profile["fixed_expenses"], 15000.0)
        self.assertEqual(profile["discretionary_spending"], 13000.0)
        self.assertEqual(profile["emi"], 10000.0)
        self.assertEqual(profile["emi_ratio"], 20.0)
        self.assertEqual(profile["estimated_savings"], 22000.0)
        self.assertEqual(profile["spending_trend"], "INCREASING")
        self.assertEqual(profile["spending_change_pct"], 30.0)
        self.assertEqual(profile["savings_trend"], "DECLINING")


if __name__ == "__main__":
    unittest.main()
