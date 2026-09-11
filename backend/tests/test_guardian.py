"""Unit tests for Stress Engine, Payment Risk Engine, Fraud Engine, and Guardian Service.

Covers tests 11 through 30 as specified in the Phase 2 contract.
"""

import unittest

from backend.domain.fraud_engine import analyze_fraud_risk
from backend.domain.payment_risk_engine import calculate_payment_risk_score
from backend.domain.stress_engine import calculate_financial_stress_score
from backend.services.guardian_service import (
    evaluate_customer_by_id,
    evaluate_guardian,
)


class TestGuardianAndSpecializedEngines(unittest.TestCase):
    """Test suite covering stress, payment risk, fraud, and Guardian service integration."""

    # ------------------------------------------------------------
    # Stress Engine Tests (11 - 16)
    # ------------------------------------------------------------

    def test_11_low_stress_customer(self):
        """Test customer with disciplined finances results in low or 0 stress score."""
        score = calculate_financial_stress_score(
            spending_change_pct=0.0,
            savings_trend="INCREASING",
            savings_change_pct=15.0,
            emi_ratio=0.0,
            failed_payments=0,
            missed_emi=False,
            monthly_spending=20000.0,
            income=60000.0,
        )
        self.assertEqual(score, 0)

    def test_12_spending_spike_contribution(self):
        """Test spending surge contributes +25 to stress score."""
        score = calculate_financial_stress_score(
            spending_change_pct=30.0,
            savings_trend="STABLE",
            emi_ratio=0.0,
        )
        self.assertEqual(score, 25)

    def test_13_savings_decline_contribution(self):
        """Test declining savings contributes +25 to stress score."""
        score = calculate_financial_stress_score(
            spending_change_pct=0.0,
            savings_trend="DECLINING",
            emi_ratio=0.0,
        )
        self.assertEqual(score, 25)

    def test_14_high_emi_ratio_contribution(self):
        """Test high EMI ratio (>30%) contributes +22 to stress score."""
        score = calculate_financial_stress_score(
            spending_change_pct=0.0,
            savings_trend="STABLE",
            emi_ratio=35.0,
        )
        self.assertEqual(score, 22)

    def test_15_failed_payment_contribution(self):
        """Test failed payments contribute +15 (for >=2) to stress score."""
        score = calculate_financial_stress_score(
            spending_change_pct=0.0,
            savings_trend="STABLE",
            failed_payments=2,
        )
        self.assertEqual(score, 15)

    def test_16_score_capped_at_100(self):
        """Test cumulative extreme stress factors are capped at 100."""
        score = calculate_financial_stress_score(
            spending_change_pct=50.0,  # +25
            savings_trend="DECLINING",  # +25
            emi_ratio=50.0,            # +30
            failed_payments=3,         # +15
            missed_emi=True,           # +30
            monthly_spending=70000.0,  # +15
            income=50000.0,
        )
        self.assertEqual(score, 100)

    # ------------------------------------------------------------
    # Payment Risk Engine Tests (17 - 19)
    # ------------------------------------------------------------

    def test_17_no_payment_issues(self):
        """Test healthy payment record produces zero payment risk score."""
        score = calculate_payment_risk_score(
            failed_payments=0,
            missed_emi=False,
            upcoming_emi_amount=0.0,
            estimated_savings=30000.0,
            emi_ratio=0.0,
        )
        self.assertEqual(score, 0)

    def test_18_failed_payments_risk(self):
        """Test failed payments elevate payment risk score."""
        score = calculate_payment_risk_score(
            failed_payments=2,
            missed_emi=False,
        )
        self.assertGreaterEqual(score, 35)

    def test_19_missed_emi_risk(self):
        """Test missed EMI heavily elevates payment risk score."""
        score = calculate_payment_risk_score(
            missed_emi=True,
        )
        self.assertGreaterEqual(score, 45)

    # ------------------------------------------------------------
    # Fraud Engine Tests (20 - 22)
    # ------------------------------------------------------------

    def test_20_normal_transaction(self):
        """Test typical transaction baseline returns benign fraud score and no anomaly."""
        hist = [
            {"amount": 3000.0, "type": "DEBIT", "status": "SUCCESS"},
            {"amount": 4000.0, "type": "DEBIT", "status": "SUCCESS"},
        ]
        recent = [
            {"amount": 3500.0, "type": "DEBIT", "status": "SUCCESS"},
        ]
        res = analyze_fraud_risk(recent, hist)
        self.assertLessEqual(res["fraud_score"], 15)
        self.assertEqual(res["anomaly_status"], "NO_ANOMALY_DETECTED")
        self.assertEqual(res["flagged_transactions"], [])

    def test_21_unusually_large_transaction(self):
        """Test unusually large transaction raises fraud score and generates UNUSUAL_TRANSACTION."""
        hist = [
            {"amount": 3000.0, "type": "DEBIT", "status": "SUCCESS"},
            {"amount": 5000.0, "type": "DEBIT", "status": "SUCCESS"},
        ]
        recent = [
            {"amount": 85000.0, "type": "DEBIT", "status": "SUCCESS"},
        ]
        res = analyze_fraud_risk(recent, hist)
        self.assertGreaterEqual(res["fraud_score"], 70)
        self.assertEqual(res["anomaly_status"], "SUSPECTED UNUSUAL ACTIVITY")
        self.assertEqual(len(res["signals"]), 1)
        self.assertEqual(res["signals"][0]["type"], "UNUSUAL_TRANSACTION")
        self.assertEqual(res["signals"][0]["evidence"][0]["current"], 85000.0)

    def test_22_unusual_not_confirmed_fraud(self):
        """Test that anomaly output strictly declares SUSPECTED UNUSUAL ACTIVITY, never CONFIRMED FRAUD."""
        hist = [{"amount": 2000.0, "type": "DEBIT", "status": "SUCCESS"}]
        recent = [{"amount": 99000.0, "type": "DEBIT", "status": "SUCCESS"}]
        res = analyze_fraud_risk(recent, hist)
        self.assertIn("SUSPECTED", res["anomaly_status"])
        self.assertNotIn("CONFIRMED", res["anomaly_status"])

    # ------------------------------------------------------------
    # Guardian Acceptance Cases & Contracts (23 - 30)
    # ------------------------------------------------------------

    def test_23_rahul_financial_stress(self):
        """Test Rahul's profile yields FINANCIAL_STRESS and ATTENTION_NEEDED."""
        res = evaluate_customer_by_id(1)
        self.assertEqual(res["classification"]["primary"], "FINANCIAL_STRESS")
        self.assertEqual(res["status"], "ATTENTION_NEEDED")
        self.assertEqual(res["recommended_intervention"]["action"], "REVIEW_UPCOMING_PAYMENTS")
        self.assertIn("BEHAVIOUR_CHANGE", res["classification"]["secondary"])

    def test_24_priya_healthy_financial_trend(self):
        """Test Priya's profile yields HEALTHY_FINANCIAL_TREND and NO_ACTION."""
        res = evaluate_customer_by_id(2)
        self.assertEqual(res["classification"]["primary"], "HEALTHY_FINANCIAL_TREND")
        self.assertEqual(res["status"], "NO_ACTION")
        self.assertEqual(res["recommended_intervention"]["type"], "NO_ACTION")

    def test_25_arjun_fraud_suspected(self):
        """Test Arjun's high-value transaction yields FRAUD_SUSPECTED and VERIFY_TRANSACTION."""
        res = evaluate_customer_by_id(3)
        self.assertEqual(res["classification"]["primary"], "FRAUD_SUSPECTED")
        self.assertIn(res["status"], ["ACTION_RECOMMENDED", "URGENT_ACTION"])
        self.assertEqual(res["recommended_intervention"]["type"], "VERIFY_TRANSACTION")

    def test_26_separate_scores_exist(self):
        """Test that all four distinct dimension scores exist in Guardian output."""
        res = evaluate_customer_by_id(1)
        scores = res["scores"]
        required_scores = {
            "financial_stress_score",
            "fraud_score",
            "payment_risk_score",
            "behaviour_change_score",
        }
        self.assertTrue(required_scores.issubset(scores.keys()))
        for s in required_scores:
            self.assertGreaterEqual(scores[s], 0)
            self.assertLessEqual(scores[s], 100)

    def test_27_evidence_is_structured(self):
        """Test that all emitted signals contain structured evidence dictionaries."""
        res = evaluate_customer_by_id(1)
        signals = res["signals"]
        self.assertGreater(len(signals), 0)
        for sig in signals:
            self.assertIn("type", sig)
            self.assertIn("severity", sig)
            self.assertIn("confidence", sig)
            self.assertIn("evidence", sig)
            self.assertIsInstance(sig["evidence"], list)
            for ev in sig["evidence"]:
                self.assertIn("metric", ev)
                self.assertIn("baseline", ev)
                self.assertIn("current", ev)
                self.assertIn("change_pct", ev)

    def test_28_confidence_range(self):
        """Test Guardian and signal confidences are strictly between 0.00 and 1.00."""
        for cid in [1, 2, 3]:
            res = evaluate_customer_by_id(cid)
            self.assertGreaterEqual(res["guardian_confidence"], 0.0)
            self.assertLessEqual(res["guardian_confidence"], 1.0)
            self.assertGreaterEqual(res["classification"]["confidence"], 0.0)
            self.assertLessEqual(res["classification"]["confidence"], 1.0)
            for sig in res["signals"]:
                self.assertGreaterEqual(sig["confidence"], 0.0)
                self.assertLessEqual(sig["confidence"], 1.0)

    def test_29_intervention_exists(self):
        """Test that valid recommended intervention structure exists."""
        res = evaluate_customer_by_id(1)
        intervention = res["recommended_intervention"]
        self.assertIn("type", intervention)
        self.assertIn("action", intervention)
        self.assertIn("priority", intervention)
        allowed_types = {
            "INFORM",
            "SUPPORT",
            "VERIFY_TRANSACTION",
            "PAYMENT_SUPPORT",
            "RECOMMEND",
            "NO_ACTION",
            "ESCALATE",
        }
        self.assertIn(intervention["type"], allowed_types)

    def test_30_deterministic_output(self):
        """Test that identical inputs to evaluate_guardian produce identical outputs."""
        customer = {"id": 1, "monthly_income": 45000.0, "monthly_emi": 14000.0}
        txns = [
            {"customer_id": 1, "timestamp": "2026-08-01", "amount": 45000.0, "type": "CREDIT", "category": "SALARY", "status": "SUCCESS"},
            {"customer_id": 1, "timestamp": "2026-08-05", "amount": 14000.0, "type": "DEBIT", "category": "EMI", "status": "SUCCESS"},
            {"customer_id": 1, "timestamp": "2026-08-10", "amount": 7087.0, "type": "DEBIT", "category": "FOOD", "status": "SUCCESS"},
            {"customer_id": 1, "timestamp": "2026-09-01", "amount": 45000.0, "type": "CREDIT", "category": "SALARY", "status": "SUCCESS"},
            {"customer_id": 1, "timestamp": "2026-09-05", "amount": 14000.0, "type": "DEBIT", "category": "EMI", "status": "SUCCESS"},
            {"customer_id": 1, "timestamp": "2026-09-10", "amount": 9000.0, "type": "DEBIT", "category": "FOOD", "status": "SUCCESS"},
        ]
        out1 = evaluate_guardian(customer, txns)
        out2 = evaluate_guardian(customer, txns)
        self.assertEqual(out1, out2)


if __name__ == "__main__":
    unittest.main()
