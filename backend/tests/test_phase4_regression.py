"""Regression tests verifying Phase 1-3 decisions remain authoritative and immutable in Phase 4."""

import copy
import pytest
from backend.domain.phase4_validator import (
    generate_deterministic_fallback,
    validate_input_schema,
    validate_output_schema,
    validate_semantic_output,
)
from backend.services.recommendation_service import evaluate_recommendation_by_id
from backend.tests.conftest import valid_rahul_output


def test_phase3_authoritative_decisions_remain():
    """Verify that Phase 3 decision outcomes for Rahul, Priya, and Arjun remain intact.

    Rahul -> SUPPORT
    Priya -> RECOMMEND
    Arjun -> VERIFY
    """
    rahul_phase3 = evaluate_recommendation_by_id(1)
    assert rahul_phase3["decision"] == "SUPPORT"

    priya_phase3 = evaluate_recommendation_by_id(2)
    assert priya_phase3["decision"] == "RECOMMEND"

    arjun_phase3 = evaluate_recommendation_by_id(3)
    assert arjun_phase3["decision"] == "VERIFY"


def test_phase4_validation_does_not_mutate_authoritative_context(rahul, priya, arjun):
    """Verify that Phase 4 validation consumes authoritative contexts without mutating them."""
    for ctx in (rahul, priya, arjun):
        ctx_snapshot = copy.deepcopy(ctx)
        valid_input = validate_input_schema(ctx)
        assert valid_input is True

        fallback = generate_deterministic_fallback(ctx)
        valid_sem = validate_semantic_output(fallback, ctx)
        assert valid_sem is True

        # Context must not be altered in any way
        assert ctx == ctx_snapshot


def test_phase4_fallback_preserves_authoritative_decisions(rahul, priya, arjun):
    """Verify deterministic fallback preserves decisions for all authoritative contexts."""
    rahul_fb = generate_deterministic_fallback(rahul)
    assert rahul_fb["decision_acknowledgement"]["decision"] == "SUPPORT"
    assert rahul_fb["decision_acknowledgement"]["action"] == "REVIEW_UPCOMING_PAYMENTS"
    assert validate_output_schema(rahul_fb) is True
    assert validate_semantic_output(rahul_fb, rahul) is True

    priya_fb = generate_deterministic_fallback(priya)
    assert priya_fb["decision_acknowledgement"]["decision"] == "RECOMMEND"
    assert priya_fb["decision_acknowledgement"]["action"] == "RECOMMEND"
    assert validate_output_schema(priya_fb) is True
    assert validate_semantic_output(priya_fb, priya) is True

    arjun_fb = generate_deterministic_fallback(arjun)
    assert arjun_fb["decision_acknowledgement"]["decision"] == "VERIFY"
    assert arjun_fb["decision_acknowledgement"]["action"] == "VERIFY_SUSPICIOUS_TRANSACTION"
    assert validate_output_schema(arjun_fb) is True
    assert validate_semantic_output(arjun_fb, arjun) is True


def test_phase4_blocks_attempt_to_alter_authoritative_decision(rahul):
    """Verify that an output cannot alter the authoritative backend decision."""
    output = valid_rahul_output()
    # Output acknowledging SUPPORT is valid
    assert validate_semantic_output(output, rahul) is True

    # Altering the acknowledged decision to RECOMMEND must be rejected
    tampered_output = copy.deepcopy(output)
    tampered_output["decision_acknowledgement"]["decision"] = "RECOMMEND"
    tampered_output["decision_acknowledgement"]["action"] = "RECOMMEND"
    tampered_output["response_type"] = "RECOMMENDATION_EXPLANATION"
    assert validate_semantic_output(tampered_output, rahul) is False
