"""Unit tests for Behavioural Engine (backend/domain/behavioural_engine.py).

Tests check personal baseline comparisons, category shifts, behavioural scores,
signal emission, and edge case handling.
"""

import unittest

from backend.domain.behavioural_engine import (
    analyze_behaviour,
    analyze_category_changes,
    generate_behavioural_signals,
)


class TestBehaviouralEngine(unittest.TestCase):
    """Test suite for Behavioural Engine."""

    def test_1_stable_spending(self):
        """Test customer whose spending matches historical baseline within 5%."""
        txns = [
            # Baseline Aug
            {"timestamp": "2026-08-01", "amount": 50000.0, "type": "CREDIT", "category": "SALARY", "status": "SUCCESS"},
            {"timestamp": "2026-08-10", "amount": 6000.0, "type": "DEBIT", "category": "FOOD", "status": "SUCCESS"},
            # Recent Sep
            {"timestamp": "2026-09-01", "amount": 50000.0, "type": "CREDIT", "category": "SALARY", "status": "SUCCESS"},
            {"timestamp": "2026-09-10", "amount": 6100.0, "type": "DEBIT", "category": "FOOD", "status": "SUCCESS"},
        ]
        result = analyze_behaviour(txns)
        self.assertAlmostEqual(result["metrics"]["spending_change_pct"], 1.7, places=1)
        self.assertLess(result["behavioural_scores"]["spending_change_score"], 20)

    def test_2_spending_increase(self):
        """Test spending surge (+27%) generating a SPENDING_SPIKE signal with evidence."""
        txns = [
            # Baseline Aug: 7087 discretionary
            {"timestamp": "2026-08-01", "amount": 45000.0, "type": "CREDIT", "category": "SALARY", "status": "SUCCESS"},
            {"timestamp": "2026-08-10", "amount": 7087.0, "type": "DEBIT", "category": "FOOD", "status": "SUCCESS"},
            # Recent Sep: 9000 discretionary
            {"timestamp": "2026-09-01", "amount": 45000.0, "type": "CREDIT", "category": "SALARY", "status": "SUCCESS"},
            {"timestamp": "2026-09-10", "amount": 9000.0, "type": "DEBIT", "category": "FOOD", "status": "SUCCESS"},
        ]
        result = analyze_behaviour(txns)
        self.assertEqual(result["metrics"]["spending_change_pct"], 27.0)
        self.assertGreaterEqual(result["behavioural_scores"]["spending_change_score"], 70)

        # Verify signal
        spike_signals = [s for s in result["signals"] if s["type"] == "SPENDING_SPIKE"]
        self.assertEqual(len(spike_signals), 1)
        signal = spike_signals[0]
        self.assertEqual(signal["severity"], "MEDIUM")
        self.assertGreaterEqual(signal["confidence"], 0.8)
        self.assertLessEqual(signal["confidence"], 1.0)
        self.assertEqual(len(signal["evidence"]), 1)
        self.assertEqual(signal["evidence"][0]["baseline"], 7087.0)
        self.assertEqual(signal["evidence"][0]["current"], 9000.0)
        self.assertEqual(signal["evidence"][0]["change_pct"], 27.0)

    def test_3_spending_decrease(self):
        """Test significant spending reduction (-30%)."""
        txns = [
            # Baseline Aug: 10,000 discretionary
            {"timestamp": "2026-08-01", "amount": 45000.0, "type": "CREDIT", "category": "SALARY", "status": "SUCCESS"},
            {"timestamp": "2026-08-10", "amount": 10000.0, "type": "DEBIT", "category": "FOOD", "status": "SUCCESS"},
            # Recent Sep: 7,000 discretionary
            {"timestamp": "2026-09-01", "amount": 45000.0, "type": "CREDIT", "category": "SALARY", "status": "SUCCESS"},
            {"timestamp": "2026-09-10", "amount": 7000.0, "type": "DEBIT", "category": "FOOD", "status": "SUCCESS"},
        ]
        result = analyze_behaviour(txns)
        self.assertEqual(result["metrics"]["spending_change_pct"], -30.0)
        self.assertGreaterEqual(result["behavioural_scores"]["spending_change_score"], 70)

    def test_4_savings_decline(self):
        """Test savings depletion generating SAVINGS_DECLINE signal."""
        txns = [
            # Baseline Aug: Income 50k, spending 30k -> Savings = 20k
            {"timestamp": "2026-08-01", "amount": 50000.0, "type": "CREDIT", "category": "SALARY", "status": "SUCCESS"},
            {"timestamp": "2026-08-10", "amount": 30000.0, "type": "DEBIT", "category": "FOOD", "status": "SUCCESS"},
            # Recent Sep: Income 50k, spending 45k -> Savings = 5k (-75% decline)
            {"timestamp": "2026-09-01", "amount": 50000.0, "type": "CREDIT", "category": "SALARY", "status": "SUCCESS"},
            {"timestamp": "2026-09-10", "amount": 45000.0, "type": "DEBIT", "category": "FOOD", "status": "SUCCESS"},
        ]
        result = analyze_behaviour(txns)
        self.assertEqual(result["metrics"]["savings_change_pct"], -75.0)
        self.assertGreaterEqual(result["behavioural_scores"]["savings_change_score"], 80)

        decline_signals = [s for s in result["signals"] if s["type"] == "SAVINGS_DECLINE"]
        self.assertEqual(len(decline_signals), 1)
        self.assertEqual(decline_signals[0]["evidence"][0]["change_pct"], -75.0)

    def test_5_savings_improvement(self):
        """Test disciplined customer with increasing savings."""
        txns = [
            # Baseline Aug: Income 50k, spending 40k -> Savings 10k
            {"timestamp": "2026-08-01", "amount": 50000.0, "type": "CREDIT", "category": "SALARY", "status": "SUCCESS"},
            {"timestamp": "2026-08-10", "amount": 40000.0, "type": "DEBIT", "category": "FOOD", "status": "SUCCESS"},
            # Recent Sep: Income 50k, spending 30k -> Savings 20k (+100% improvement)
            {"timestamp": "2026-09-01", "amount": 50000.0, "type": "CREDIT", "category": "SALARY", "status": "SUCCESS"},
            {"timestamp": "2026-09-10", "amount": 30000.0, "type": "DEBIT", "category": "FOOD", "status": "SUCCESS"},
        ]
        result = analyze_behaviour(txns)
        self.assertEqual(result["metrics"]["savings_change_pct"], 100.0)

    def test_6_category_level_change(self):
        """Test category-level spending shifts with deviation score and direction."""
        recent = [
            {"amount": 4000.0, "type": "DEBIT", "category": "SHOPPING", "status": "SUCCESS"},
            {"amount": 5000.0, "type": "DEBIT", "category": "FOOD", "status": "SUCCESS"},
        ]
        historical = [
            {"amount": 2000.0, "type": "DEBIT", "category": "SHOPPING", "status": "SUCCESS"},
            {"amount": 5000.0, "type": "DEBIT", "category": "FOOD", "status": "SUCCESS"},
        ]
        cat_changes = analyze_category_changes(recent, historical)
        shopping = next(c for c in cat_changes if c["category"] == "SHOPPING")
        self.assertEqual(shopping["baseline_average"], 2000.0)
        self.assertEqual(shopping["recent_average"], 4000.0)
        self.assertEqual(shopping["change_pct"], 100.0)
        self.assertEqual(shopping["direction"], "INCREASING")
        self.assertEqual(shopping["significance"], "HIGH")

        food = next(c for c in cat_changes if c["category"] == "FOOD")
        self.assertEqual(food["direction"], "STABLE")
        self.assertEqual(food["significance"], "LOW")

    def test_7_failed_payments(self):
        """Test tracking of failed payment attempts and FAILED_PAYMENTS signal."""
        txns = [
            {"timestamp": "2026-09-01", "amount": 50000.0, "type": "CREDIT", "category": "SALARY", "status": "SUCCESS"},
            {"timestamp": "2026-09-05", "amount": 10000.0, "type": "DEBIT", "category": "BILLS", "status": "FAILED"},
            {"timestamp": "2026-09-06", "amount": 10000.0, "type": "DEBIT", "category": "BILLS", "status": "FAILED"},
        ]
        result = analyze_behaviour(txns)
        self.assertEqual(result["metrics"]["failed_payment_count"], 2)
        self.assertGreaterEqual(result["behavioural_scores"]["payment_behaviour_score"], 60)

        fail_signals = [s for s in result["signals"] if s["type"] == "FAILED_PAYMENTS"]
        self.assertEqual(len(fail_signals), 1)
        self.assertEqual(fail_signals[0]["severity"], "HIGH")

    def test_8_insufficient_historical_data(self):
        """Test single month of transactions handles missing baseline gracefully."""
        txns = [
            {"timestamp": "2026-09-01", "amount": 50000.0, "type": "CREDIT", "category": "SALARY", "status": "SUCCESS"},
            {"timestamp": "2026-09-10", "amount": 15000.0, "type": "DEBIT", "category": "FOOD", "status": "SUCCESS"},
        ]
        result = analyze_behaviour(txns)
        self.assertEqual(result["metrics"]["spending_change_pct"], 0.0)
        self.assertEqual(result["metrics"]["savings_change_pct"], 0.0)
        self.assertEqual(result["category_changes"], [])

    def test_9_empty_transaction_data(self):
        """Test empty transaction list returns default zero structure without error."""
        result = analyze_behaviour([])
        self.assertEqual(result["behavioural_scores"]["spending_change_score"], 0)
        self.assertEqual(result["behavioural_scores"]["overall_behaviour_change_score"], 0)
        self.assertEqual(result["metrics"]["spending_change_pct"], 0.0)
        self.assertEqual(result["signals"], [])

    def test_10_deterministic_output(self):
        """Test that identical input data repeatedly produces identical output."""
        txns = [
            {"timestamp": "2026-08-01", "amount": 45000.0, "type": "CREDIT", "category": "SALARY", "status": "SUCCESS"},
            {"timestamp": "2026-08-10", "amount": 7000.0, "type": "DEBIT", "category": "FOOD", "status": "SUCCESS"},
            {"timestamp": "2026-09-01", "amount": 45000.0, "type": "CREDIT", "category": "SALARY", "status": "SUCCESS"},
            {"timestamp": "2026-09-10", "amount": 9000.0, "type": "DEBIT", "category": "FOOD", "status": "SUCCESS"},
        ]
        res1 = analyze_behaviour(txns)
        res2 = analyze_behaviour(txns)
        self.assertEqual(res1, res2)


if __name__ == "__main__":
    unittest.main()
