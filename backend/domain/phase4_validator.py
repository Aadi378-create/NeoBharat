"""Phase 4 Deterministic Safety and Validation Layer for NeoBharat.

Public Interface:
- validate_input_schema(payload: dict) -> bool
- validate_output_schema(payload: dict) -> bool
- validate_semantic_output(output: dict, context: dict) -> bool
- generate_deterministic_fallback(context: dict) -> dict
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import jsonschema
from jsonschema import Draft202012Validator

_SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"
_INPUT_SCHEMA_PATH = _SCHEMAS_DIR / "phase4_llm_input.schema.json"
_OUTPUT_SCHEMA_PATH = _SCHEMAS_DIR / "phase4_llm_output.schema.json"

_input_validator: Optional[Draft202012Validator] = None
_output_validator: Optional[Draft202012Validator] = None


def _get_input_validator() -> Draft202012Validator:
    global _input_validator
    if _input_validator is None:
        with open(_INPUT_SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema = json.load(f)
        _input_validator = Draft202012Validator(schema)
    return _input_validator


def _get_output_validator() -> Draft202012Validator:
    global _output_validator
    if _output_validator is None:
        with open(_OUTPUT_SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema = json.load(f)
        _output_validator = Draft202012Validator(schema)
    return _output_validator


def validate_input_schema(payload: dict) -> bool:
    """Validate a payload against backend/schemas/phase4_llm_input.schema.json.

    Args:
        payload: Input dictionary to validate.

    Returns:
        bool: True only if the payload conforms to the schema, False otherwise.
    """
    if not isinstance(payload, dict):
        return False
    try:
        validator = _get_input_validator()
        return validator.is_valid(payload)
    except Exception:
        return False


def validate_output_schema(payload: dict) -> bool:
    """Validate a payload against backend/schemas/phase4_llm_output.schema.json.

    Args:
        payload: Output dictionary to validate.

    Returns:
        bool: True only if the payload conforms to the schema, False otherwise.
    """
    if not isinstance(payload, dict):
        return False
    try:
        validator = _get_output_validator()
        return validator.is_valid(payload)
    except Exception:
        return False


# Action compatibility mapping by authoritative decision
EXPECTED_ACTIONS = {
    "SUPPORT": {
        "SUPPORT",
        "REVIEW_UPCOMING_PAYMENTS",
    },
    "VERIFY": {
        "VERIFY",
        "VERIFY_SUSPICIOUS_TRANSACTION",
    },
    "RECOMMEND": {
        "RECOMMEND",
    },
    "NO_RECOMMENDATION": {
        "NO_RECOMMENDATION",
    },
}

# 6. Credit promotion vs. discouragement patterns
_DISCOURAGEMENT_PATTERN = re.compile(
    r"\b(wouldn't|would\s+not|don't|do\s+not|not|never|shouldn't|should\s+not|cannot|can't)\s+(recommend|suggest|advise|take|opt|apply|borrow|consider)\b"
    r"|\b(not\s+suitable|unsuitable|not\s+advisable|inadvisable|avoid|refrain|against\s+(taking|borrowing))\b",
    re.IGNORECASE,
)

_CREDIT_PROMOTION_PATTERNS = [
    # (take|apply for|borrow|consider|use|get|increase|raise) + (loan|credit card|credit limit|borrowing|debt)
    re.compile(
        r"\b(take|taking|apply\s+for|applying\s+for|borrow|borrowing|consider|use|using|get|getting|increase|increasing|raise|raising)\b.{0,30}\b(personal\s+loan|loan|loans|credit\s+card|credit\s+cards|credit\s+limit|borrowing|debt)\b",
        re.IGNORECASE,
    ),
    # Reverse ordering: (loan|credit card|credit limit|borrowing) + (could help|can help|is an option|might help|to manage)
    re.compile(
        r"\b(personal\s+loan|loan|loans|credit\s+card|credit\s+limit|borrowing)\b.{0,25}\b(could\s+help|can\s+help|is\s+an\s+option|might\s+help|to\s+manage|to\s+bridge)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bborrow(ing)?\s+(a\s+little\s+more|more|money|funds)\b", re.IGNORECASE),
    re.compile(r"\bhigher\s+credit\s+limit\b", re.IGNORECASE),
    re.compile(r"\bbridge\s+the\s+gap\s+with\s+(credit|borrowing|a\s+loan|a\s+credit\s+card)\b", re.IGNORECASE),
    re.compile(r"\b(eligible|pre-approved|approved)\s+for\s+(a\s+)?(loan|credit|credit\s+card)\b", re.IGNORECASE),
    re.compile(r"\b(small|instant|new)\s+(personal\s+)?loan\b", re.IGNORECASE),
    re.compile(r"\badditional\s+credit\b", re.IGNORECASE),
]

# 7. Confirmed fraud language (suspected fraud is not confirmed fraud)
_CONFIRMED_FRAUD_PATTERNS = [
    re.compile(r"definitely\s+fraudulent", re.IGNORECASE),
    re.compile(r"fraud\s+(has\s+been\s+)?confirmed", re.IGNORECASE),
    re.compile(r"confirmed\s+fraud", re.IGNORECASE),
    re.compile(r"definitely\s+(been\s+)?hacked", re.IGNORECASE),
    re.compile(r"account\s+(has\s+been\s+)?hacked", re.IGNORECASE),
    re.compile(r"someone\s+else\s+definitely\s+made", re.IGNORECASE),
    re.compile(r"card\s+(has\s+been\s+)?stolen", re.IGNORECASE),
    re.compile(r"stolen\s+card", re.IGNORECASE),
]

# 8. Fabricated financial claims (APR, interest rates, fees, guaranteed returns, odds)
_FABRICATED_FINANCIAL_PATTERNS = [
    re.compile(r"\bapr\s+(of\s+)?\d+(\.\d+)?%?\b", re.IGNORECASE),
    re.compile(r"\b\d+(\.\d+)?%\s*(apr|interest(\s+rate)?)\b", re.IGNORECASE),
    re.compile(r"\b(annual\s+)?fee\s+is\s+₹?\d+", re.IGNORECASE),
    re.compile(r"\b\d+(\.\d+)?%\s*(annual\s+)?returns?\b", re.IGNORECASE),
    re.compile(r"\b\d+%\s*chance\s+of\s+approval\b", re.IGNORECASE),
    re.compile(r"\bguaranteed\s+(to\s+receive|approval|to\s+get)\b", re.IGNORECASE),
    re.compile(r"\bsafely\s+add\s+a\s+₹?\d+[\d,]*\s*emi\b", re.IGNORECASE),
    re.compile(r"\bcredit\s+score\s+(is|of)\s+\d+\b", re.IGNORECASE),
    re.compile(r"\bcibil\s+score\s+(is|of)\s+\d+\b", re.IGNORECASE),
]

# 9. Coercive or dark-pattern phrases
_COERCIVE_PATTERNS = [
    re.compile(r"lose\s+the\s+opportunity(\s+forever)?", re.IGNORECASE),
    re.compile(r"must\s+take\s+this\s+loan", re.IGNORECASE),
    re.compile(r"(act|apply)\s+now\s+before\s+.*disappears", re.IGNORECASE),
    re.compile(r"before\s+(this\s+)?.*disappears", re.IGNORECASE),
    re.compile(r"only\s+chance\s+to\s+get\s+approved", re.IGNORECASE),
    re.compile(r"disappears\s+forever", re.IGNORECASE),
    re.compile(r"you\s+will\s+regret\s+it", re.IGNORECASE),
]

# 10. Unsupported RBI / bank authority approval claims
_AUTHORITY_CLAIM_PATTERNS = [
    re.compile(r"rbi\s+(has\s+)?approved\s+(your|the|this)?\s*(loan)?", re.IGNORECASE),
    re.compile(r"rbi\s+already\s+approved", re.IGNORECASE),
    re.compile(r"rbi\s+says\s+you\s+are\s+eligible", re.IGNORECASE),
    re.compile(r"rbi\s+certified", re.IGNORECASE),
    re.compile(r"(your\s+)?bank\s+has\s+already\s+approved", re.IGNORECASE),
    re.compile(r"bank\s+already\s+approved\s+me", re.IGNORECASE),
    re.compile(r"already\s+approved\s+for\s+(a\s+)?₹?\d+", re.IGNORECASE),
]


def _is_credit_blocked(context: dict) -> bool:
    """Check whether credit is blocked according to NeoBharat Prototype Safety Heuristics."""
    guardian = context.get("guardian_context", {})
    scores = guardian.get("scores", {})
    financial = context.get("financial_context", {})

    stress = float(scores.get("financial_stress_score", 0))
    risk = float(scores.get("payment_risk_score", 0))
    fraud = float(scores.get("fraud_score", 0))
    emi_ratio = float(financial.get("emi_ratio", 0))
    surplus = float(financial.get("net_monthly_surplus", 0))

    return (
        stress >= 60.0
        or risk >= 60.0
        or fraud >= 65.0
        or emi_ratio > 35.0
        or surplus <= 0.0
    )


def validate_semantic_output(output: dict, context: dict) -> bool:
    """Validate an LLM response against the authoritative deterministic Phase 3 context.

    Enforces the strict 10-step semantic validation order:
    1. Schema validity
    2. Safety metadata
    3. Decision consistency
    4. Action consistency
    5. Evidence truth
    6. Credit safety gate
    7. Fraud language
    8. Fabricated financial claims
    9. Coercive/dark-pattern language
    10. Unsupported RBI/bank approval claims

    Args:
        output: The LLM output dictionary.
        context: The authoritative Phase 3 context dictionary.

    Returns:
        bool: True if semantically valid and safe, False otherwise.
    """
    if not isinstance(output, dict) or not isinstance(context, dict):
        return False

    # 1. Schema validity
    if not validate_output_schema(output):
        return False

    # 2. Safety metadata
    safety = output.get("safety", {})
    if safety.get("financial_decision_made_by") != "DETERMINISTIC_ENGINE":
        return False
    if safety.get("llm_role") != "EXPLANATION_ONLY":
        return False

    # 3. Decision consistency
    context_decision = context.get("decision_context", {}).get("decision")
    output_decision = output.get("decision_acknowledgement", {}).get("decision")
    if context_decision != output_decision:
        return False

    # 4. Action consistency
    output_action = output.get("decision_acknowledgement", {}).get("action")
    allowed_actions = EXPECTED_ACTIONS.get(context_decision)
    if not allowed_actions or output_action not in allowed_actions:
        return False

    # 5. Evidence truth
    financial_ctx = context.get("financial_context", {})
    guardian_scores = context.get("guardian_context", {}).get("scores", {})

    authoritative_metrics: Dict[str, Any] = {
        "income": financial_ctx.get("income"),
        "monthly_spending": financial_ctx.get("monthly_spending"),
        "current_emi": financial_ctx.get("current_emi"),
        "emi_ratio": financial_ctx.get("emi_ratio"),
        "net_monthly_surplus": financial_ctx.get("net_monthly_surplus"),
        "spending_trend": financial_ctx.get("spending_trend"),
        "spending_change_pct": financial_ctx.get("spending_change_pct"),
        "savings_trend": financial_ctx.get("savings_trend"),
        "financial_stress_score": guardian_scores.get("financial_stress_score"),
        "payment_risk_score": guardian_scores.get("payment_risk_score"),
        "fraud_score": guardian_scores.get("fraud_score"),
        "behaviour_change_score": guardian_scores.get("behaviour_change_score"),
    }

    for item in output.get("evidence", []):
        metric = item.get("metric")
        val = item.get("value")

        if metric not in authoritative_metrics:
            return False

        auth_val = authoritative_metrics[metric]
        if auth_val is None:
            return False

        # Compare values
        if isinstance(auth_val, (int, float)):
            try:
                if abs(float(val) - float(auth_val)) > 0.05:
                    return False
            except (ValueError, TypeError):
                return False
        else:
            if str(val).strip().upper() != str(auth_val).strip().upper():
                return False

    message = output.get("message", "")

    # 6. Credit safety gate
    if _is_credit_blocked(context):
        sentences = re.split(r"[.!?;\n]+", message)
        for sentence in sentences:
            s_clean = sentence.strip()
            if not s_clean:
                continue
            # Legitimate discouragement or advice against borrowing is permitted
            if _DISCOURAGEMENT_PATTERN.search(s_clean):
                continue
            # Rejection of credit promotion or encouragement
            for pattern in _CREDIT_PROMOTION_PATTERNS:
                if pattern.search(s_clean):
                    return False

    # 7. Fraud language
    for pattern in _CONFIRMED_FRAUD_PATTERNS:
        if pattern.search(message):
            return False

    # 8. Fabricated financial claims
    for pattern in _FABRICATED_FINANCIAL_PATTERNS:
        if pattern.search(message):
            return False

    # 9. Coercive/dark-pattern language
    for pattern in _COERCIVE_PATTERNS:
        if pattern.search(message):
            return False

    # 10. Unsupported RBI/bank approval claims
    for pattern in _AUTHORITY_CLAIM_PATTERNS:
        if pattern.search(message):
            return False

    return True


def generate_deterministic_fallback(context: dict) -> dict:
    """Generate a safe, deterministic response without an LLM.

    The returned object strictly satisfies phase4_llm_output.schema.json.

    Args:
        context: Authoritative Phase 3 context dictionary.

    Returns:
        dict: Safe fallback response conforming to output schema.
    """
    decision_ctx = context.get("decision_context", {})
    decision = decision_ctx.get("decision", "SUPPORT")
    recommendation = decision_ctx.get("recommendation", {})
    action = recommendation.get("action", "REVIEW_UPCOMING_PAYMENTS")

    financial = context.get("financial_context", {})
    scores = context.get("guardian_context", {}).get("scores", {})

    evidence: List[Dict[str, Any]] = []

    if decision == "VERIFY":
        response_type = "FRAUD_VERIFICATION"
        message = (
            "This transaction appears unusual compared with your normal spending pattern. "
            "This does not confirm fraud. Please verify whether you made it."
        )
        ack_action = "VERIFY_SUSPICIOUS_TRANSACTION"
        next_step = {
            "type": "VERIFY",
            "label": "Verify recent transaction activity",
        }
        if "fraud_score" in scores:
            evidence.append({"metric": "fraud_score", "value": scores["fraud_score"]})
        if "monthly_spending" in financial:
            evidence.append({"metric": "monthly_spending", "value": financial["monthly_spending"]})

    elif decision == "SUPPORT":
        response_type = "SUPPORT_GUIDANCE"
        message = (
            "Your recent financial activity shows spending and savings shifts. "
            "To support your financial wellbeing, please review your upcoming payments and commitments."
        )
        ack_action = "REVIEW_UPCOMING_PAYMENTS"
        next_step = {
            "type": "ACTION",
            "label": "Review upcoming payments and expenses",
        }
        if "financial_stress_score" in scores:
            evidence.append({"metric": "financial_stress_score", "value": scores["financial_stress_score"]})
        if "payment_risk_score" in scores:
            evidence.append({"metric": "payment_risk_score", "value": scores["payment_risk_score"]})
        if "current_emi" in financial:
            evidence.append({"metric": "current_emi", "value": financial["current_emi"]})
        if "net_monthly_surplus" in financial:
            evidence.append({"metric": "net_monthly_surplus", "value": financial["net_monthly_surplus"]})

    elif decision == "RECOMMEND":
        response_type = "RECOMMENDATION_EXPLANATION"
        prod_name = recommendation.get("product_name") or "suitable financial product"
        message = (
            f"Based on your disciplined savings trend and healthy financial standing, "
            f"{prod_name} is presented for your review."
        )
        ack_action = "RECOMMEND"
        next_step = {
            "type": "INFORMATION",
            "label": "Review illustrative product details",
        }
        if "income" in financial:
            evidence.append({"metric": "income", "value": financial["income"]})
        if "net_monthly_surplus" in financial:
            evidence.append({"metric": "net_monthly_surplus", "value": financial["net_monthly_surplus"]})
        if "savings_trend" in financial:
            evidence.append({"metric": "savings_trend", "value": financial["savings_trend"]})

    else:  # NO_RECOMMENDATION
        response_type = "FINANCIAL_GUIDANCE"
        message = (
            "At this time, no commercial banking product provides a clear additional benefit "
            "for your financial situation without adding unnecessary financial obligations."
        )
        ack_action = "NO_RECOMMENDATION"
        next_step = {
            "type": "NONE",
            "label": "No action required",
        }
        if "financial_stress_score" in scores:
            evidence.append({"metric": "financial_stress_score", "value": scores["financial_stress_score"]})
        if "net_monthly_surplus" in financial:
            evidence.append({"metric": "net_monthly_surplus", "value": financial["net_monthly_surplus"]})

    return {
        "contract_version": "1.0",
        "response_type": response_type,
        "message": message,
        "decision_acknowledgement": {
            "decision": decision,
            "action": ack_action,
        },
        "evidence": evidence[:5],
        "next_step": next_step,
        "safety": {
            "financial_decision_made_by": "DETERMINISTIC_ENGINE",
            "llm_role": "EXPLANATION_ONLY",
        },
    }
