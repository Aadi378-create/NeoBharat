"""Unit tests for Phase 4 LLM input schema validation."""

import copy
import pytest
from backend.domain.phase4_validator import validate_input_schema
from backend.tests.conftest import build_input


def test_valid_rahul_input(rahul):
    """Authoritative Rahul context must satisfy input schema."""
    assert validate_input_schema(rahul) is True


def test_valid_priya_input(priya):
    """Authoritative Priya context must satisfy input schema."""
    assert validate_input_schema(priya) is True


def test_valid_arjun_input(arjun):
    """Authoritative Arjun context must satisfy input schema."""
    assert validate_input_schema(arjun) is True


def test_non_dict_input():
    """Non-dictionary inputs must return False."""
    assert validate_input_schema(None) is False
    assert validate_input_schema("not a dict") is False
    assert validate_input_schema(12345) is False
    assert validate_input_schema([{"a": 1}]) is False


def test_missing_contract_version(rahul):
    """Missing contract_version must fail validation."""
    data = copy.deepcopy(rahul)
    del data["contract_version"]
    assert validate_input_schema(data) is False


def test_invalid_contract_version(rahul):
    """Unsupported contract_version must fail validation."""
    data = copy.deepcopy(rahul)
    data["contract_version"] = "2.0"
    assert validate_input_schema(data) is False


@pytest.mark.parametrize(
    "field",
    [
        "customer",
        "user_message",
        "financial_context",
        "guardian_context",
        "decision_context",
        "conversation_context",
    ],
)
def test_missing_required_sections(rahul, field):
    """Missing any top-level required section must fail validation."""
    data = copy.deepcopy(rahul)
    del data[field]
    assert validate_input_schema(data) is False


@pytest.mark.parametrize("field", ["id", "name", "preferred_language"])
def test_missing_customer_fields(rahul, field):
    """Missing required customer sub-fields must fail validation."""
    data = copy.deepcopy(rahul)
    del data["customer"][field]
    assert validate_input_schema(data) is False


def test_invalid_preferred_language(rahul):
    """Invalid language enum must fail validation."""
    data = copy.deepcopy(rahul)
    data["customer"]["preferred_language"] = "Hindi"
    assert validate_input_schema(data) is False


@pytest.mark.parametrize(
    "field",
    [
        "income",
        "monthly_spending",
        "current_emi",
        "emi_ratio",
        "net_monthly_surplus",
        "spending_trend",
        "spending_change_pct",
        "savings_trend",
    ],
)
def test_missing_financial_context_fields(rahul, field):
    """Missing any required financial_context metric must fail validation."""
    data = copy.deepcopy(rahul)
    del data["financial_context"][field]
    assert validate_input_schema(data) is False


def test_invalid_spending_trend_enum(rahul):
    """Invalid spending trend enum must fail validation."""
    data = copy.deepcopy(rahul)
    data["financial_context"]["spending_trend"] = "EXPLODING"
    assert validate_input_schema(data) is False


def test_invalid_savings_trend_enum(rahul):
    """Invalid savings trend enum must fail validation."""
    data = copy.deepcopy(rahul)
    data["financial_context"]["savings_trend"] = "DEPLETED"
    assert validate_input_schema(data) is False


@pytest.mark.parametrize(
    "score_field",
    [
        "financial_stress_score",
        "payment_risk_score",
        "fraud_score",
        "behaviour_change_score",
    ],
)
def test_missing_guardian_scores(rahul, score_field):
    """Missing any required guardian score must fail validation."""
    data = copy.deepcopy(rahul)
    del data["guardian_context"]["scores"][score_field]
    assert validate_input_schema(data) is False


def test_invalid_guardian_status_enum(rahul):
    """Invalid guardian status enum must fail validation."""
    data = copy.deepcopy(rahul)
    data["guardian_context"]["status"] = "PANIC_MODE"
    assert validate_input_schema(data) is False


def test_invalid_guardian_classification_enum(rahul):
    """Invalid guardian primary classification enum must fail validation."""
    data = copy.deepcopy(rahul)
    data["guardian_context"]["primary_classification"] = "UNKNOWN_RISK"
    assert validate_input_schema(data) is False


def test_invalid_decision_enum(rahul):
    """Invalid decision enum must fail validation."""
    data = copy.deepcopy(rahul)
    data["decision_context"]["decision"] = "APPROVED"
    assert validate_input_schema(data) is False


def test_invalid_product_category_enum(rahul):
    """Invalid product_category enum (e.g. personal_loan) must fail validation."""
    data = copy.deepcopy(rahul)
    data["decision_context"]["recommendation"]["product_category"] = "personal_loan"
    assert validate_input_schema(data) is False


def test_extra_top_level_property_rejected(rahul):
    """Extra top-level properties must be rejected."""
    data = copy.deepcopy(rahul)
    data["extra_unauthorized_key"] = 123
    assert validate_input_schema(data) is False


def test_extra_nested_property_rejected(rahul):
    """Extra nested properties must be rejected."""
    data = copy.deepcopy(rahul)
    data["financial_context"]["credit_score"] = 750
    assert validate_input_schema(data) is False
