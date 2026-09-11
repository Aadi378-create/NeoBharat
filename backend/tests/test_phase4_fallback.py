"""Unit tests for Phase 4 deterministic fallback generator."""

import pytest
from backend.domain.phase4_validator import (
    generate_deterministic_fallback,
    validate_output_schema,
    validate_semantic_output,
)
from backend.tests.conftest import build_input


def test_rahul_fallback_schema_and_semantic(rahul):
    """Fallback for Rahul must satisfy schema and semantic validation."""
    fallback = generate_deterministic_fallback(rahul)
    assert validate_output_schema(fallback) is True
    assert validate_semantic_output(fallback, rahul) is True


def test_rahul_fallback_fields(rahul):
    """Fallback for Rahul must match SUPPORT decision and actions."""
    fallback = generate_deterministic_fallback(rahul)
    assert fallback["contract_version"] == "1.0"
    assert fallback["response_type"] == "SUPPORT_GUIDANCE"
    assert fallback["decision_acknowledgement"]["decision"] == "SUPPORT"
    assert fallback["decision_acknowledgement"]["action"] == "REVIEW_UPCOMING_PAYMENTS"
    assert fallback["next_step"]["type"] == "ACTION"
    assert fallback["safety"]["financial_decision_made_by"] == "DETERMINISTIC_ENGINE"
    assert fallback["safety"]["llm_role"] == "EXPLANATION_ONLY"

    # Verify evidence contains real metrics
    metrics = {e["metric"]: e["value"] for e in fallback["evidence"]}
    assert metrics.get("financial_stress_score") == 72.0
    assert metrics.get("payment_risk_score") == 61.0


def test_arjun_fallback_schema_and_semantic(arjun):
    """Fallback for Arjun must satisfy schema and semantic validation."""
    fallback = generate_deterministic_fallback(arjun)
    assert validate_output_schema(fallback) is True
    assert validate_semantic_output(fallback, arjun) is True


def test_arjun_fallback_fields(arjun):
    """Fallback for Arjun must match VERIFY decision without claiming confirmed fraud."""
    fallback = generate_deterministic_fallback(arjun)
    assert fallback["response_type"] == "FRAUD_VERIFICATION"
    assert fallback["decision_acknowledgement"]["decision"] == "VERIFY"
    assert fallback["decision_acknowledgement"]["action"] == "VERIFY_SUSPICIOUS_TRANSACTION"
    assert fallback["next_step"]["type"] == "VERIFY"
    assert "does not confirm fraud" in fallback["message"].lower()

    metrics = {e["metric"]: e["value"] for e in fallback["evidence"]}
    assert metrics.get("fraud_score") == 95.0


def test_priya_fallback_schema_and_semantic(priya):
    """Fallback for Priya must satisfy schema and semantic validation."""
    fallback = generate_deterministic_fallback(priya)
    assert validate_output_schema(fallback) is True
    assert validate_semantic_output(fallback, priya) is True


def test_priya_fallback_fields(priya):
    """Fallback for Priya must match RECOMMEND decision."""
    fallback = generate_deterministic_fallback(priya)
    assert fallback["response_type"] == "RECOMMENDATION_EXPLANATION"
    assert fallback["decision_acknowledgement"]["decision"] == "RECOMMEND"
    assert fallback["decision_acknowledgement"]["action"] == "RECOMMEND"
    assert fallback["next_step"]["type"] == "INFORMATION"


def test_no_recommendation_fallback():
    """Fallback for a NO_RECOMMENDATION context must be valid."""
    no_rec_context = build_input(
        decision_context={
            "decision": "NO_RECOMMENDATION",
            "recommendation": {
                "action": "NO_RECOMMENDATION",
                "product_category": None,
                "product_name": None,
                "supportive_guidance": None,
                "suitability_rationale": "No suitable commercial product without adding risk.",
            },
            "policy_reasons": [],
        }
    )
    fallback = generate_deterministic_fallback(no_rec_context)
    assert validate_output_schema(fallback) is True
    assert validate_semantic_output(fallback, no_rec_context) is True
    assert fallback["response_type"] == "FINANCIAL_GUIDANCE"
    assert fallback["decision_acknowledgement"]["decision"] == "NO_RECOMMENDATION"
    assert fallback["next_step"]["type"] == "NONE"
