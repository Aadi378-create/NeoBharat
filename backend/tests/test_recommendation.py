"""Unit tests for Recommendation Engine and Service (Phase 3).

Tests acceptance cases for Rahul, Priya, and Arjun, verifies grievance metadata,
validates Illustrative Prototype Product constraints, and enforces customer-protection rules.
"""

import unittest

from backend.domain.recommendation_engine import (
    PROTOTYPE_PRODUCT_CATALOG,
    generate_recommendation,
)
from backend.services.guardian_service import evaluate_customer_by_id as evaluate_guardian_by_id
from backend.services.recommendation_service import (
    evaluate_recommendation_by_id,
    evaluate_recommendation_data,
)


class TestRecommendationEngineAndService(unittest.TestCase):
    """Test suite for Recommendation Engine, Service, and Acceptance Cases."""

    def test_1_rahul_acceptance_support_no_credit(self):
        """Test Rahul receives SUPPORT, REVIEW_UPCOMING_PAYMENTS, and strictly NO credit recommendation."""
        res = evaluate_recommendation_by_id(1)
        self.assertEqual(res["decision"], "SUPPORT")
        self.assertEqual(res["recommendation"]["action"], "SUPPORT")
        self.assertIsNone(res["recommendation"]["product_category"])
        self.assertIsNone(res["recommendation"]["product_name"])
        self.assertEqual(res["recommendation"]["supportive_guidance"]["action"], "REVIEW_UPCOMING_PAYMENTS")
        self.assertEqual(res["affordability"]["safe_incremental_debt_capacity"], 0.0)

    def test_2_priya_acceptance_recommend_suitable_product(self):
        """Test Priya receives RECOMMEND for a suitable wealth accumulation product (investment/SIP)."""
        res = evaluate_recommendation_by_id(2)
        self.assertEqual(res["decision"], "RECOMMEND")
        self.assertEqual(res["recommendation"]["action"], "RECOMMEND")
        self.assertEqual(res["recommendation"]["product_category"], "investment/SIP")
        self.assertIn("SIP", res["recommendation"]["product_name"])
        self.assertGreater(res["affordability"]["net_monthly_surplus"], 0.0)

    def test_3_arjun_acceptance_verify_no_products(self):
        """Test Arjun receives VERIFY with zero commercial product offers."""
        res = evaluate_recommendation_by_id(3)
        self.assertEqual(res["decision"], "VERIFY")
        self.assertEqual(res["recommendation"]["action"], "VERIFY")
        self.assertIsNone(res["recommendation"]["product_category"])
        self.assertEqual(res["recommendation"]["supportive_guidance"]["action"], "VERIFY_SUSPICIOUS_TRANSACTION")

    def test_4_illustrative_prototype_product_labels(self):
        """Test that all products in catalog are explicitly labelled as 'Illustrative Prototype Product'."""
        for key, product in PROTOTYPE_PRODUCT_CATALOG.items():
            self.assertIn("Illustrative Prototype Product", product["product_name"])
            self.assertIn("Illustrative Prototype Product", product["illustrative_terms"])

    def test_5_product_terms_no_fabricated_apr_yield(self):
        """Test that product fields do not fabricate APR, interest rates, or yields; unpopulated fields are None."""
        for key, product in PROTOTYPE_PRODUCT_CATALOG.items():
            self.assertIn("product_category", product)
            self.assertIn("product_name", product)
            self.assertIn("purpose", product)
            self.assertIn("illustrative_terms", product)
            self.assertIn("fees", product)
            self.assertIn("risk_disclosure", product)
            # Ensure fees are None or explicitly stated prototype text
            if product["fees"] is not None:
                self.assertIn("prototype", str(product["fees"]).lower())

    def test_6_grievance_metadata_structure(self):
        """Test that recommendation output includes structured prototype grievance metadata."""
        for cid in [1, 2, 3]:
            res = evaluate_recommendation_by_id(cid)
            self.assertIn("grievance", res)
            self.assertTrue(res["grievance"]["available"])
            self.assertEqual(res["grievance"]["action"], "CONTACT_SUPPORT")
            self.assertFalse(res["grievance"]["escalation_required"])

    def test_7_consumer_protection_metadata_terminology(self):
        """Test metadata strictly uses 'RBI-aligned customer-protection design' and 'NeoBharat Prototype Safety Heuristic'."""
        res = evaluate_recommendation_by_id(1)
        meta = res["consumer_protection_metadata"]
        self.assertEqual(meta["framework"], "RBI-aligned customer-protection design")
        self.assertEqual(meta["policy_type"], "NeoBharat Prototype Safety Heuristic")
        self.assertTrue(meta["predatory_lending_blocked"])

    def test_8_no_coercive_language_in_rationales(self):
        """Test that suitability rationales contain no coercive, urgency, or shame-based wording."""
        coercive_words = ["hurry", "limited time", "don't miss", "act now", "risk losing", "guaranteed approval"]
        for cid in [1, 2, 3]:
            res = evaluate_recommendation_by_id(cid)
            rationale = res["recommendation"]["suitability_rationale"].lower()
            for word in coercive_words:
                self.assertNotIn(word, rationale)

    def test_9_savings_product_structure(self):
        """Test savings product structure when customer has surplus but stable savings."""
        decision = {
            "outcome": "RECOMMEND",
            "eligible_categories": ["savings", "investment/SIP"],
            "affordability": {"net_monthly_surplus": 3000.0, "safe_incremental_debt_capacity": 0.0},
        }
        profile = {"savings_trend": "STABLE"}
        rec = generate_recommendation(decision, profile)
        self.assertEqual(rec["product_category"], "savings")
        self.assertIn("Auto-Sweep", rec["product_name"])

    def test_10_sip_product_structure(self):
        """Test SIP product structure when customer has increasing savings and surplus >= 5000."""
        decision = {
            "outcome": "RECOMMEND",
            "eligible_categories": ["investment/SIP", "savings"],
            "affordability": {"net_monthly_surplus": 10000.0, "safe_incremental_debt_capacity": 0.0},
        }
        profile = {"savings_trend": "INCREASING"}
        rec = generate_recommendation(decision, profile)
        self.assertEqual(rec["product_category"], "investment/SIP")
        self.assertIn("SIP", rec["product_name"])
        self.assertIsNotNone(rec["risk_disclosure"])

    def test_11_service_integration_with_sqlite_repositories(self):
        """Test evaluate_recommendation_by_id integrates seamlessly with SQLite."""
        res = evaluate_recommendation_by_id(1)
        self.assertEqual(res["customer_id"], 1)
        self.assertIn("guardian_context", res)
        self.assertIn("scores", res["guardian_context"])
        self.assertEqual(res["guardian_context"]["scores"]["financial_stress_score"], 72)

    def test_12_no_recommendation_mandatory_when_appropriate(self):
        """Test that NO_RECOMMENDATION outcome formats properly with null product fields."""
        decision = {
            "outcome": "NO_RECOMMENDATION",
            "eligible_categories": [],
            "affordability": {"net_monthly_surplus": 0.0, "safe_incremental_debt_capacity": 0.0},
        }
        rec = generate_recommendation(decision, {})
        self.assertEqual(rec["action"], "NO_RECOMMENDATION")
        self.assertIsNone(rec["product_category"])
        self.assertIsNone(rec["product_name"])
        self.assertIsNone(rec["supportive_guidance"])
        self.assertIn("No commercial banking product", rec["suitability_rationale"])

    def test_13_contract_schema_completeness(self):
        """Test that the recommendation JSON contains all required contract keys."""
        res = evaluate_recommendation_by_id(2)
        required_keys = {
            "customer_id",
            "decision",
            "guardian_context",
            "affordability",
            "recommendation",
            "policy_reasons",
            "grievance",
            "consumer_protection_metadata",
        }
        self.assertTrue(required_keys.issubset(res.keys()))

    def test_14_service_idempotency(self):
        """Test that repeated calls to evaluate_recommendation_by_id yield identical results."""
        out1 = evaluate_recommendation_by_id(1)
        out2 = evaluate_recommendation_by_id(1)
        self.assertEqual(out1, out2)

    def test_15_regression_all_phase1_and_phase2_intact(self):
        """Test regression: Phase 2 Guardian outputs for Rahul, Priya, Arjun remain unchanged."""
        g_rahul = evaluate_guardian_by_id(1)
        self.assertEqual(g_rahul["classification"]["primary"], "FINANCIAL_STRESS")
        self.assertEqual(g_rahul["scores"]["financial_stress_score"], 72)

        g_priya = evaluate_guardian_by_id(2)
        self.assertEqual(g_priya["classification"]["primary"], "HEALTHY_FINANCIAL_TREND")
        self.assertEqual(g_priya["scores"]["financial_stress_score"], 0)

        g_arjun = evaluate_guardian_by_id(3)
        self.assertEqual(g_arjun["classification"]["primary"], "FRAUD_SUSPECTED")
        self.assertEqual(g_arjun["scores"]["fraud_score"], 95)


if __name__ == "__main__":
    unittest.main()
