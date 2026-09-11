"""Unit tests for Phase 4 semantic validation against authoritative context."""

import copy
import pytest
from backend.domain.phase4_validator import validate_semantic_output
from backend.tests.conftest import build_output, valid_rahul_output


def test_valid_rahul_semantic_passes(rahul):
    """Authoritative valid Rahul output must pass semantic validation."""
    output = valid_rahul_output()
    assert validate_semantic_output(output, rahul) is True


def test_valid_priya_semantic_passes(priya):
    """Authoritative valid Priya output must pass semantic validation."""
    output = build_output(
        response_type="RECOMMENDATION_EXPLANATION",
        message="Based on your strong savings habit and financial standing, an illustrative SIP is recommended.",
        decision_acknowledgement={"decision": "RECOMMEND", "action": "RECOMMEND"},
        evidence=[
            {"metric": "income", "value": 65000.0},
            {"metric": "net_monthly_surplus", "value": 44000.0},
            {"metric": "savings_trend", "value": "INCREASING"},
        ],
        next_step={"type": "INFORMATION", "label": "Review illustrative product terms"},
    )
    assert validate_semantic_output(output, priya) is True


def test_valid_arjun_semantic_passes(arjun):
    """Authoritative valid Arjun output must pass semantic validation."""
    output = build_output(
        response_type="FRAUD_VERIFICATION",
        message="This transaction appears unusual compared with your normal spending pattern. This does not confirm fraud. Please verify.",
        decision_acknowledgement={
            "decision": "VERIFY",
            "action": "VERIFY_SUSPICIOUS_TRANSACTION",
        },
        evidence=[
            {"metric": "fraud_score", "value": 95.0},
            {"metric": "monthly_spending", "value": 105700.0},
        ],
        next_step={"type": "VERIFY", "label": "Verify transaction activity"},
    )
    assert validate_semantic_output(output, arjun) is True


def test_non_dict_inputs_fail(rahul):
    """Non-dict output or context must fail semantic validation."""
    output = valid_rahul_output()
    assert validate_semantic_output(None, rahul) is False
    assert validate_semantic_output(output, None) is False
    assert validate_semantic_output("string", rahul) is False
    assert validate_semantic_output(output, 123) is False


def test_decision_flip_support_to_recommend_fails(rahul):
    """Flipping backend SUPPORT decision to RECOMMEND must be rejected."""
    output = valid_rahul_output(
        response_type="RECOMMENDATION_EXPLANATION",
        decision_acknowledgement={"decision": "RECOMMEND", "action": "RECOMMEND"},
        message="You are eligible for our premier personal loan product.",
        next_step={"type": "INFORMATION", "label": "Apply now"},
    )
    assert validate_semantic_output(output, rahul) is False


def test_decision_flip_verify_to_recommend_fails(arjun):
    """Flipping backend VERIFY decision to RECOMMEND must be rejected."""
    output = build_output(
        response_type="RECOMMENDATION_EXPLANATION",
        decision_acknowledgement={"decision": "RECOMMEND", "action": "RECOMMEND"},
        message="Great news! You can apply for a pre-approved credit card.",
    )
    assert validate_semantic_output(output, arjun) is False


def test_decision_flip_recommend_to_support_fails(priya):
    """Flipping backend RECOMMEND decision to SUPPORT must be rejected."""
    output = build_output(
        response_type="SUPPORT_GUIDANCE",
        decision_acknowledgement={"decision": "SUPPORT", "action": "REVIEW_UPCOMING_PAYMENTS"},
        message="Please review your upcoming payments.",
    )
    assert validate_semantic_output(output, priya) is False


def test_mismatched_action_fails(rahul):
    """Acknowledged action must align with backend decision."""
    output = valid_rahul_output(
        decision_acknowledgement={
            "decision": "SUPPORT",
            "action": "VERIFY_SUSPICIOUS_TRANSACTION",
        }
    )
    assert validate_semantic_output(output, rahul) is False


def test_evidence_value_mismatch_numeric(rahul):
    """Fabricated or mismatched numeric evidence values must be rejected."""
    output = valid_rahul_output(
        evidence=[
            {"metric": "financial_stress_score", "value": 20.0},  # True value is 72.0
            {"metric": "payment_risk_score", "value": 61.0},
        ]
    )
    assert validate_semantic_output(output, rahul) is False


def test_evidence_value_mismatch_categorical(rahul):
    """Fabricated or mismatched categorical evidence values must be rejected."""
    output = valid_rahul_output(
        evidence=[
            {"metric": "spending_trend", "value": "DECLINING"},  # True value is INCREASING
        ]
    )
    assert validate_semantic_output(output, rahul) is False


def test_evidence_unknown_metric(rahul):
    """Unknown metric in evidence must be rejected."""
    output = valid_rahul_output(
        evidence=[
            {"metric": "income", "value": 45000.0},
        ]
    )
    # income is valid, but let's test a metric not in context
    output["evidence"].append({"metric": "credit_score", "value": 800.0})
    # Since output schema validates this first, it should return False
    assert validate_semantic_output(output, rahul) is False


def test_credit_promotion_blocked_for_rahul(rahul):
    """When credit is blocked, direct personal loan recommendations must be rejected."""
    output = valid_rahul_output(
        message="You should apply for a personal loan to help manage your existing monthly expenses."
    )
    assert validate_semantic_output(output, rahul) is False


def test_credit_card_promotion_blocked_for_rahul(rahul):
    """When credit is blocked, credit card recommendations must be rejected."""
    output = valid_rahul_output(
        message="Consider using a credit card to handle cash flow challenges."
    )
    assert validate_semantic_output(output, rahul) is False


def test_indirect_credit_recommendation_blocked(rahul):
    """When credit is blocked, subtle or indirect borrowing suggestions must be rejected."""
    phrases = [
        "You could consider borrowing a little more to smooth out upcoming bills.",
        "We recommend taking a loan to bridge your budget shortfall.",
        "You might be eligible for a loan if you act now.",
        "You can bridge the gap with credit until your next salary.",
    ]
    for phrase in phrases:
        output = valid_rahul_output(message=phrase)
        assert validate_semantic_output(output, rahul) is False, f"Failed to reject: {phrase}"


def test_safety_metadata_tampering_rejected(rahul):
    """Tampering with safety provenance metadata must be rejected."""
    output = valid_rahul_output(
        safety={"financial_decision_made_by": "LLM", "llm_role": "EXPLANATION_ONLY"}
    )
    assert validate_semantic_output(output, rahul) is False


@pytest.mark.parametrize(
    "acceptable_credit_phrase",
    [
        "Your current credit obligations are already elevated.",
        "I wouldn't recommend taking another loan right now.",
        "Additional borrowing is not suitable right now.",
    ],
)
def test_credit_discouragement_and_discussion_accepted_for_rahul(rahul, acceptable_credit_phrase):
    """Legitimate non-promotional discussions and discouragement of credit must remain acceptable."""
    output = valid_rahul_output(message=acceptable_credit_phrase)
    assert validate_semantic_output(output, rahul) is True


@pytest.mark.parametrize(
    "promotional_phrase",
    [
        "You should take a personal loan.",
        "Consider applying for a credit card.",
        "Borrow a little more to manage the gap.",
    ],
)
def test_targeted_credit_promotions_rejected(rahul, promotional_phrase):
    """Targeted credit promotions must be strictly rejected when credit is blocked."""
    output = valid_rahul_output(message=promotional_phrase)
    assert validate_semantic_output(output, rahul) is False


@pytest.mark.parametrize(
    "factual_percentage_phrase",
    [
        "Your spending increased by 27%.",
        "Your EMI is about 31.1% of your income.",
    ],
)
def test_ordinary_percentage_statements_accepted(rahul, factual_percentage_phrase):
    """Ordinary factual percentage explanations must remain valid."""
    output = valid_rahul_output(message=factual_percentage_phrase)
    assert validate_semantic_output(output, rahul) is True


def test_factual_rbi_disclosure_reference_accepted(priya):
    """Ordinary informational references to RBI regulations must remain valid."""
    output = build_output(
        response_type="RECOMMENDATION_EXPLANATION",
        decision_acknowledgement={"decision": "RECOMMEND", "action": "RECOMMEND"},
        message="RBI regulations require applicable disclosures. We recommend reviewing this illustrative product.",
        evidence=[
            {"metric": "income", "value": 65000.0},
            {"metric": "net_monthly_surplus", "value": 44000.0},
            {"metric": "savings_trend", "value": "INCREASING"},
        ],
        next_step={"type": "INFORMATION", "label": "Review illustrative terms"},
    )
    assert validate_semantic_output(output, priya) is True

