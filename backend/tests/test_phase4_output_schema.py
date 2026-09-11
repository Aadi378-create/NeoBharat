"""Unit tests for Phase 4 LLM output schema validation."""

import copy
import pytest
from backend.domain.phase4_validator import validate_output_schema
from backend.tests.conftest import build_output


def test_valid_default_output():
    """Default valid output payload must satisfy output schema."""
    output = build_output()
    assert validate_output_schema(output) is True


def test_valid_priya_output():
    """Valid recommendation explanation output must satisfy schema."""
    output = build_output(
        response_type="RECOMMENDATION_EXPLANATION",
        message="Based on your strong financial standing, an illustrative SIP product is suggested.",
        decision_acknowledgement={"decision": "RECOMMEND", "action": "RECOMMEND"},
        evidence=[
            {"metric": "income", "value": 65000.0},
            {"metric": "net_monthly_surplus", "value": 44000.0},
            {"metric": "savings_trend", "value": "INCREASING"},
        ],
        next_step={"type": "INFORMATION", "label": "Review illustrative product terms"},
    )
    assert validate_output_schema(output) is True


def test_valid_arjun_output():
    """Valid fraud verification output must satisfy schema."""
    output = build_output(
        response_type="FRAUD_VERIFICATION",
        message="This transaction appears unusual compared with your normal spending pattern. Please verify.",
        decision_acknowledgement={
            "decision": "VERIFY",
            "action": "VERIFY_SUSPICIOUS_TRANSACTION",
        },
        evidence=[
            {"metric": "fraud_score", "value": 95.0},
            {"metric": "monthly_spending", "value": 105700.0},
        ],
        next_step={"type": "VERIFY", "label": "Verify transaction"},
    )
    assert validate_output_schema(output) is True


def test_non_dict_output():
    """Non-dictionary outputs must return False."""
    assert validate_output_schema(None) is False
    assert validate_output_schema("invalid") is False
    assert validate_output_schema(999) is False
    assert validate_output_schema([]) is False


def test_missing_contract_version():
    """Missing contract_version must fail validation."""
    data = build_output()
    del data["contract_version"]
    assert validate_output_schema(data) is False


def test_invalid_contract_version():
    """Unsupported contract_version must fail validation."""
    data = build_output(contract_version="2.0")
    assert validate_output_schema(data) is False


@pytest.mark.parametrize(
    "field",
    [
        "contract_version",
        "response_type",
        "message",
        "decision_acknowledgement",
        "evidence",
        "next_step",
        "safety",
    ],
)
def test_missing_required_top_level_fields(field):
    """Missing any required top-level field must fail validation."""
    data = build_output()
    del data[field]
    assert validate_output_schema(data) is False


def test_invalid_response_type_enum():
    """Disallowed response_type must fail validation."""
    data = build_output(response_type="LOAN_OFFER")
    assert validate_output_schema(data) is False


def test_invalid_decision_acknowledgement_decision():
    """Disallowed decision outcome must fail validation."""
    data = build_output(
        decision_acknowledgement={"decision": "APPROVED", "action": "RECOMMEND"}
    )
    assert validate_output_schema(data) is False


def test_invalid_decision_acknowledgement_action():
    """Disallowed action enum must fail validation."""
    data = build_output(
        decision_acknowledgement={"decision": "SUPPORT", "action": "INSTANT_DISBURSAL"}
    )
    assert validate_output_schema(data) is False


def test_evidence_more_than_five_items():
    """Evidence exceeding maxItems=5 must fail validation."""
    data = build_output(
        evidence=[
            {"metric": "income", "value": 50000.0},
            {"metric": "monthly_spending", "value": 30000.0},
            {"metric": "current_emi", "value": 10000.0},
            {"metric": "emi_ratio", "value": 20.0},
            {"metric": "net_monthly_surplus", "value": 10000.0},
            {"metric": "financial_stress_score", "value": 25.0},
        ]
    )
    assert validate_output_schema(data) is False


def test_invalid_evidence_metric():
    """Evidence with unknown or disallowed metric must fail validation."""
    data = build_output(
        evidence=[{"metric": "credit_bureau_score", "value": 750}]
    )
    assert validate_output_schema(data) is False


def test_invalid_next_step_type():
    """Disallowed next_step type must fail validation."""
    data = build_output(
        next_step={"type": "APPLY_NOW", "label": "Apply for loan"}
    )
    assert validate_output_schema(data) is False


def test_invalid_safety_decision_maker():
    """Safety field indicating LLM made financial decision must fail validation."""
    data = build_output(
        safety={"financial_decision_made_by": "LLM", "llm_role": "EXPLANATION_ONLY"}
    )
    assert validate_output_schema(data) is False


def test_invalid_safety_llm_role():
    """Safety field indicating autonomous LLM role must fail validation."""
    data = build_output(
        safety={
            "financial_decision_made_by": "DETERMINISTIC_ENGINE",
            "llm_role": "AUTONOMOUS_AGENT",
        }
    )
    assert validate_output_schema(data) is False


def test_extra_top_level_property():
    """Extra unexpected properties in output must fail validation."""
    data = build_output(unauthorized_field="malicious_payload")
    assert validate_output_schema(data) is False


def test_extra_safety_property():
    """Extra properties in safety object must fail validation."""
    data = build_output()
    data["safety"]["bypass_allowed"] = True
    assert validate_output_schema(data) is False
