"""Shared fixtures and helpers for Phase 4 tests."""

import copy
from typing import Any, Dict

import pytest


def build_input(**overrides) -> Dict[str, Any]:
    """Helper to construct a valid Phase 4 LLM input payload with customizable overrides."""
    base: Dict[str, Any] = {
        "contract_version": "1.0",
        "customer": {
            "id": 1,
            "name": "Rahul",
            "preferred_language": "English",
        },
        "user_message": "Can you explain my current financial review?",
        "financial_context": {
            "income": 45000.0,
            "monthly_spending": 38000.0,
            "current_emi": 14000.0,
            "emi_ratio": 31.1,
            "net_monthly_surplus": 7000.0,
            "spending_trend": "INCREASING",
            "spending_change_pct": 27.0,
            "savings_trend": "DECLINING",
        },
        "guardian_context": {
            "status": "ATTENTION_NEEDED",
            "primary_classification": "FINANCIAL_STRESS",
            "scores": {
                "financial_stress_score": 72.0,
                "payment_risk_score": 61.0,
                "fraud_score": 7.0,
                "behaviour_change_score": 72.0,
            },
        },
        "decision_context": {
            "decision": "SUPPORT",
            "recommendation": {
                "action": "REVIEW_UPCOMING_PAYMENTS",
                "product_category": None,
                "product_name": None,
                "supportive_guidance": {
                    "type": "SUPPORT",
                    "action": "REVIEW_UPCOMING_PAYMENTS",
                    "priority": "HIGH",
                },
                "suitability_rationale": "Customer exhibits indicators of financial stress or payment difficulty; commercial product recommendations are strictly withheld in favor of supportive financial review.",
            },
            "policy_reasons": [
                {
                    "code": "HIGH_FINANCIAL_STRESS",
                    "description": "Financial stress score of 72 meets NeoBharat Prototype Safety Heuristic (>=60). Credit products blocked.",
                    "evidence": {
                        "metric": "financial_stress_score",
                        "value": 72,
                        "threshold": 60,
                    },
                }
            ],
        },
        "conversation_context": {
            "previous_messages": [],
            "language": "English",
        },
    }

    result = copy.deepcopy(base)
    for k, v in overrides.items():
        if isinstance(v, dict) and k in result and isinstance(result[k], dict):
            result[k].update(v)
        else:
            result[k] = v
    return result


def build_output(**overrides) -> Dict[str, Any]:
    """Helper to construct a valid Phase 4 LLM output payload with customizable overrides."""
    base: Dict[str, Any] = {
        "contract_version": "1.0",
        "response_type": "SUPPORT_GUIDANCE",
        "message": (
            "Your recent financial activity shows spending and savings shifts. "
            "To support your financial wellbeing, please review your upcoming payments and commitments."
        ),
        "decision_acknowledgement": {
            "decision": "SUPPORT",
            "action": "REVIEW_UPCOMING_PAYMENTS",
        },
        "evidence": [
            {"metric": "financial_stress_score", "value": 72.0},
            {"metric": "payment_risk_score", "value": 61.0},
            {"metric": "current_emi", "value": 14000.0},
            {"metric": "net_monthly_surplus", "value": 7000.0},
        ],
        "next_step": {
            "type": "ACTION",
            "label": "Review upcoming payments and expenses",
        },
        "safety": {
            "financial_decision_made_by": "DETERMINISTIC_ENGINE",
            "llm_role": "EXPLANATION_ONLY",
        },
    }

    result = copy.deepcopy(base)
    for k, v in overrides.items():
        if isinstance(v, dict) and k in result and isinstance(result[k], dict):
            result[k].update(v)
        else:
            result[k] = v
    return result


def valid_rahul_output(**overrides) -> Dict[str, Any]:
    """Helper to construct a valid, semantically safe output specifically for Rahul."""
    return build_output(**overrides)


@pytest.fixture
def rahul() -> Dict[str, Any]:
    """Authoritative Phase 4 context for Rahul (Customer 1)."""
    return build_input(
        customer={"id": 1, "name": "Rahul", "preferred_language": "English"},
        user_message="Can you explain my financial status and can I get a loan?",
        financial_context={
            "income": 45000.0,
            "monthly_spending": 38000.0,
            "current_emi": 14000.0,
            "emi_ratio": 31.1,
            "net_monthly_surplus": 7000.0,
            "spending_trend": "INCREASING",
            "spending_change_pct": 27.0,
            "savings_trend": "DECLINING",
        },
        guardian_context={
            "status": "ATTENTION_NEEDED",
            "primary_classification": "FINANCIAL_STRESS",
            "scores": {
                "financial_stress_score": 72.0,
                "payment_risk_score": 61.0,
                "fraud_score": 7.0,
                "behaviour_change_score": 72.0,
            },
        },
        decision_context={
            "decision": "SUPPORT",
            "recommendation": {
                "action": "REVIEW_UPCOMING_PAYMENTS",
                "product_category": None,
                "product_name": None,
                "supportive_guidance": {
                    "type": "SUPPORT",
                    "action": "REVIEW_UPCOMING_PAYMENTS",
                    "priority": "HIGH",
                },
                "suitability_rationale": "Customer exhibits indicators of financial stress or payment difficulty; commercial product recommendations are strictly withheld in favor of supportive financial review.",
            },
            "policy_reasons": [
                {
                    "code": "HIGH_FINANCIAL_STRESS",
                    "description": "Financial stress score of 72 meets NeoBharat Prototype Safety Heuristic (>=60). Credit products blocked.",
                    "evidence": {"metric": "financial_stress_score", "value": 72, "threshold": 60},
                },
                {
                    "code": "ELEVATED_PAYMENT_DIFFICULTY",
                    "description": "Payment risk score of 61 meets NeoBharat Prototype Safety Heuristic (>=60). Credit products blocked.",
                    "evidence": {"metric": "payment_risk_score", "value": 61, "threshold": 60},
                },
            ],
        },
    )


@pytest.fixture
def priya() -> Dict[str, Any]:
    """Authoritative Phase 4 context for Priya (Customer 2)."""
    return build_input(
        customer={"id": 2, "name": "Priya", "preferred_language": "English"},
        user_message="What savings or investment options are available for me?",
        financial_context={
            "income": 65000.0,
            "monthly_spending": 21000.0,
            "current_emi": 0.0,
            "emi_ratio": 0.0,
            "net_monthly_surplus": 44000.0,
            "spending_trend": "STABLE",
            "spending_change_pct": 0.0,
            "savings_trend": "INCREASING",
        },
        guardian_context={
            "status": "NO_ACTION",
            "primary_classification": "HEALTHY_FINANCIAL_TREND",
            "scores": {
                "financial_stress_score": 0.0,
                "payment_risk_score": 0.0,
                "fraud_score": 4.0,
                "behaviour_change_score": 18.0,
            },
        },
        decision_context={
            "decision": "RECOMMEND",
            "recommendation": {
                "action": "RECOMMEND",
                "product_category": "investment/SIP",
                "product_name": "Illustrative Prototype Product: Systematic Wealth Builder SIP",
                "supportive_guidance": None,
                "suitability_rationale": "Customer demonstrates established savings discipline and monthly surplus of ₹44,000.00 suitable for systematic long-term wealth accumulation.",
            },
            "policy_reasons": [
                {
                    "code": "HEALTHY_FINANCIAL_STANDING",
                    "description": "Customer exhibits healthy savings and low risk scores under NeoBharat Prototype Safety Heuristics.",
                    "evidence": {"metric": "financial_stress_score", "value": 0, "threshold": 60},
                }
            ],
        },
    )


@pytest.fixture
def arjun() -> Dict[str, Any]:
    """Authoritative Phase 4 context for Arjun (Customer 3)."""
    return build_input(
        customer={"id": 3, "name": "Arjun", "preferred_language": "English"},
        user_message="Why is there a notification on my account?",
        financial_context={
            "income": 50000.0,
            "monthly_spending": 105700.0,
            "current_emi": 8000.0,
            "emi_ratio": 16.0,
            "net_monthly_surplus": -55700.0,
            "spending_trend": "INCREASING",
            "spending_change_pct": 1491.2,
            "savings_trend": "DECLINING",
        },
        guardian_context={
            "status": "URGENT_ACTION",
            "primary_classification": "FRAUD_SUSPECTED",
            "scores": {
                "financial_stress_score": 65.0,
                "payment_risk_score": 50.0,
                "fraud_score": 95.0,
                "behaviour_change_score": 100.0,
            },
        },
        decision_context={
            "decision": "VERIFY",
            "recommendation": {
                "action": "VERIFY_SUSPICIOUS_TRANSACTION",
                "product_category": None,
                "product_name": None,
                "supportive_guidance": {
                    "type": "VERIFY_TRANSACTION",
                    "action": "VERIFY_SUSPICIOUS_TRANSACTION",
                    "priority": "HIGH",
                },
                "suitability_rationale": "Commercial product recommendations are suspended until suspected unusual transaction activity is verified by the customer.",
            },
            "policy_reasons": [
                {
                    "code": "SUSPECTED_UNUSUAL_ACTIVITY",
                    "description": "Fraud score of 95 meets NeoBharat Prototype Safety Heuristic (>=65). All commercial products locked pending verification.",
                    "evidence": {"metric": "fraud_score", "value": 95, "threshold": 65},
                }
            ],
        },
    )
