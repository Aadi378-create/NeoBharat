"""Unit tests for Phase 3 Decision Engine (backend/domain/decision_engine.py).

Verifies affordability calculations, EMI accounting safeguards, canonical NeoBharat
prototype safety heuristics, gate hierarchies, and deterministic outputs.
"""

import unittest

from backend.domain.decision_engine import (
    calculate_affordability,
    evaluate_decision,
)


class TestDecisionEngine(unittest.TestCase):
    """Test suite for Decision Engine policies and safety gates."""

    def test_1_affordability_no_double_counting_emi(self):
        """Test that estimated_savings is treated directly as post-EMI surplus without subtracting EMI twice."""
        profile = {
            "income": 45000.0,
            "monthly_spending": 38000.0,  # Already includes 14000 EMI
            "emi": 14000.0,
            "emi_ratio": 31.1,
            "estimated_savings": 7000.0,  # 45000 - 38000
        }
        affordability = calculate_affordability(profile)
        # Surplus must equal 7000, NOT 7000 - 14000 = -7000
        self.assertEqual(affordability["net_monthly_surplus"], 7000.0)
        self.assertEqual(affordability["current_emi"], 14000.0)
        self.assertEqual(affordability["income"], 45000.0)

    def test_2_gate_1_fraud_score_blocks_all_products(self):
        """Test fraud_score >= 65 produces VERIFY and blocks all commercial categories."""
        guardian = {
            "scores": {"financial_stress_score": 20, "payment_risk_score": 10, "fraud_score": 85},
            "classification": {"primary": "FRAUD_SUSPECTED"},
        }
        profile = {"income": 50000.0, "monthly_spending": 20000.0, "emi": 5000.0, "emi_ratio": 10.0, "estimated_savings": 30000.0}
        res = evaluate_decision(guardian, profile)
        self.assertEqual(res["outcome"], "VERIFY")
        self.assertEqual(res["action"], "VERIFY_SUSPICIOUS_TRANSACTION")
        self.assertEqual(res["eligible_categories"], [])
        self.assertEqual(res["affordability"]["safe_incremental_debt_capacity"], 0.0)

    def test_3_gate_2_payment_risk_blocks_credit(self):
        """Test payment_risk_score >= 60 produces SUPPORT and blocks credit products."""
        guardian = {
            "scores": {"financial_stress_score": 30, "payment_risk_score": 65, "fraud_score": 5},
            "classification": {"primary": "PAYMENT_RISK"},
        }
        profile = {"income": 50000.0, "monthly_spending": 30000.0, "emi": 10000.0, "emi_ratio": 20.0, "estimated_savings": 20000.0}
        res = evaluate_decision(guardian, profile)
        self.assertEqual(res["outcome"], "SUPPORT")
        self.assertTrue(res["credit_blocked"])
        self.assertIn("loan/credit", res["blocked_categories"])
        self.assertIn("credit card", res["blocked_categories"])

    def test_4_gate_3_stress_score_blocks_credit(self):
        """Test financial_stress_score >= 60 produces SUPPORT and blocks credit products."""
        guardian = {
            "scores": {"financial_stress_score": 72, "payment_risk_score": 40, "fraud_score": 5},
            "classification": {"primary": "FINANCIAL_STRESS"},
        }
        profile = {"income": 45000.0, "monthly_spending": 38000.0, "emi": 14000.0, "emi_ratio": 31.1, "estimated_savings": 7000.0}
        res = evaluate_decision(guardian, profile)
        self.assertEqual(res["outcome"], "SUPPORT")
        self.assertTrue(res["credit_blocked"])
        self.assertIn("loan/credit", res["blocked_categories"])
        self.assertEqual(res["affordability"]["safe_incremental_debt_capacity"], 0.0)

    def test_5_gate_4_emi_ratio_blocks_credit(self):
        """Test emi_ratio > 35.0% blocks credit products under NeoBharat Prototype Safety Heuristic."""
        guardian = {
            "scores": {"financial_stress_score": 35, "payment_risk_score": 25, "fraud_score": 5},
            "classification": {"primary": "NO_CONCERN"},
        }
        profile = {"income": 40000.0, "monthly_spending": 25000.0, "emi": 15000.0, "emi_ratio": 37.5, "estimated_savings": 15000.0}
        res = evaluate_decision(guardian, profile)
        self.assertTrue(res["credit_blocked"])
        self.assertIn("loan/credit", res["blocked_categories"])
        self.assertEqual(res["affordability"]["safe_incremental_debt_capacity"], 0.0)

    def test_6_gate_4_deficit_surplus_blocks_credit(self):
        """Test net_monthly_surplus <= 0 blocks credit products and sets debt capacity to 0."""
        guardian = {
            "scores": {"financial_stress_score": 40, "payment_risk_score": 30, "fraud_score": 5},
            "classification": {"primary": "NO_CONCERN"},
        }
        profile = {"income": 40000.0, "monthly_spending": 42000.0, "emi": 8000.0, "emi_ratio": 20.0, "estimated_savings": -2000.0}
        res = evaluate_decision(guardian, profile)
        self.assertTrue(res["credit_blocked"])
        self.assertEqual(res["affordability"]["safe_incremental_debt_capacity"], 0.0)

    def test_7_stress_below_60_does_not_block_credit(self):
        """Test that stress below 60 (e.g. 45) does NOT block credit under canonical policy."""
        guardian = {
            "scores": {"financial_stress_score": 45, "payment_risk_score": 20, "fraud_score": 5},
            "classification": {"primary": "NO_CONCERN"},
        }
        profile = {"income": 60000.0, "monthly_spending": 30000.0, "emi": 6000.0, "emi_ratio": 10.0, "estimated_savings": 30000.0}
        res = evaluate_decision(guardian, profile)
        self.assertFalse(res["credit_blocked"])
        self.assertIn("loan/credit", res["eligible_categories"])

    def test_8_gate_5_clean_profile_allows_recommendation(self):
        """Test clean profile with positive surplus produces RECOMMEND."""
        guardian = {
            "scores": {"financial_stress_score": 0, "payment_risk_score": 0, "fraud_score": 4},
            "classification": {"primary": "HEALTHY_FINANCIAL_TREND"},
        }
        profile = {"income": 65000.0, "monthly_spending": 21000.0, "emi": 0.0, "emi_ratio": 0.0, "estimated_savings": 44000.0}
        res = evaluate_decision(guardian, profile)
        self.assertEqual(res["outcome"], "RECOMMEND")
        self.assertFalse(res["credit_blocked"])
        self.assertIn("savings", res["eligible_categories"])
        self.assertIn("investment/SIP", res["eligible_categories"])

    def test_9_safe_incremental_debt_capacity_zero_when_blocked(self):
        """Test safe incremental debt capacity is strictly zero when credit is blocked."""
        profile = {"income": 50000.0, "monthly_spending": 40000.0, "emi": 19000.0, "emi_ratio": 38.0, "estimated_savings": 10000.0}
        affordability = calculate_affordability(profile)
        self.assertEqual(affordability["safe_incremental_debt_capacity"], 0.0)

    def test_10_no_recommendation_when_no_benefit(self):
        """Test NO_RECOMMENDATION is returned when surplus is insufficient for non-credit products."""
        guardian = {
            "scores": {"financial_stress_score": 35, "payment_risk_score": 25, "fraud_score": 5},
            "classification": {"primary": "NO_CONCERN"},
        }
        profile = {"income": 30000.0, "monthly_spending": 29800.0, "emi": 11000.0, "emi_ratio": 36.6, "estimated_savings": 200.0}
        res = evaluate_decision(guardian, profile)
        self.assertEqual(res["outcome"], "NO_RECOMMENDATION")
        self.assertEqual(res["eligible_categories"], [])

    def test_11_deterministic_decision_output(self):
        """Test that identical inputs repeatedly produce identical decision outputs."""
        guardian = {
            "scores": {"financial_stress_score": 72, "payment_risk_score": 61, "fraud_score": 7},
            "classification": {"primary": "FINANCIAL_STRESS"},
        }
        profile = {"income": 45000.0, "monthly_spending": 38000.0, "emi": 14000.0, "emi_ratio": 31.1, "estimated_savings": 7000.0}
        res1 = evaluate_decision(guardian, profile)
        res2 = evaluate_decision(guardian, profile)
        self.assertEqual(res1, res2)

    def test_12_zero_income_handled_safely(self):
        """Test safe handling when income is 0.0."""
        profile = {"income": 0.0, "monthly_spending": 5000.0, "emi": 0.0, "emi_ratio": 0.0, "estimated_savings": -5000.0}
        affordability = calculate_affordability(profile)
        self.assertEqual(affordability["safe_incremental_debt_capacity"], 0.0)
        self.assertEqual(affordability["net_monthly_surplus"], -5000.0)

    def test_13_empty_transactions_handled_safely(self):
        """Test safe fallback when profile is empty."""
        affordability = calculate_affordability({})
        self.assertEqual(affordability["income"], 0.0)
        self.assertEqual(affordability["safe_incremental_debt_capacity"], 0.0)

    def test_14_policy_reasons_contain_structured_evidence(self):
        """Test that every policy reason contains code, description, and numerical evidence."""
        guardian = {
            "scores": {"financial_stress_score": 75, "payment_risk_score": 65, "fraud_score": 10},
            "classification": {"primary": "FINANCIAL_STRESS"},
        }
        profile = {"income": 45000.0, "monthly_spending": 38000.0, "emi": 14000.0, "emi_ratio": 31.1, "estimated_savings": 7000.0}
        res = evaluate_decision(guardian, profile)
        self.assertGreaterEqual(len(res["policy_reasons"]), 2)
        for reason in res["policy_reasons"]:
            self.assertIn("code", reason)
            self.assertIn("description", reason)
            self.assertIn("evidence", reason)
            self.assertIn("metric", reason["evidence"])
            self.assertIn("value", reason["evidence"])
            self.assertIn("threshold", reason["evidence"])

    def test_15_blocked_categories_integrity(self):
        """Test that loan/credit and credit card are in blocked_categories during financial stress."""
        guardian = {
            "scores": {"financial_stress_score": 70, "payment_risk_score": 30, "fraud_score": 5},
            "classification": {"primary": "FINANCIAL_STRESS"},
        }
        profile = {"income": 50000.0, "monthly_spending": 35000.0, "emi": 10000.0, "emi_ratio": 20.0, "estimated_savings": 15000.0}
        res = evaluate_decision(guardian, profile)
        self.assertIn("loan/credit", res["blocked_categories"])
        self.assertIn("credit card", res["blocked_categories"])


if __name__ == "__main__":
    unittest.main()
