"""OpenAI Integration Client for NeoBharat Explanation Layer (Phase 5).

Provides a secure, non-crashing interface to OpenAI's Chat Completions API.
The LLM acts strictly as an EXPLANATION_ONLY layer. All financial calculations
and decisions are made prior to invoking this module by deterministic engines.
"""

import json
import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the explanation layer for NeoBharat.

The deterministic financial engine has already made the financial decision.
Your job is ONLY to explain that decision clearly and empathetically.

Strict Guidelines:
1. Never change the decision outcome. The decision acknowledge MUST match context.
2. Never invent financial facts or metrics.
3. Never invent product terms, fees, APR, interest rates, or investment returns.
4. Never provide unsupported financial figures or approval odds.
5. Never claim regulatory (RBI) or bank pre-approval.
6. Never classify suspicious activity as confirmed fraud, theft, or hacking.
7. If credit is blocked in context, never promote, encourage, or recommend taking a loan or credit card.
8. Never override the safety metadata:
   "financial_decision_made_by": "DETERMINISTIC_ENGINE"
   "llm_role": "EXPLANATION_ONLY"

Your output must be a valid JSON object strictly conforming to the following structure:
{
  "contract_version": "1.0",
  "response_type": "SUPPORT_GUIDANCE" | "RECOMMENDATION_EXPLANATION" | "FRAUD_VERIFICATION" | "FINANCIAL_GUIDANCE" | "FALLBACK",
  "message": "<your clear, empathetic explanation>",
  "decision_acknowledgement": {
    "decision": "<must match decision_context.decision exactly>",
    "action": "<must match decision_context.recommendation.action exactly>"
  },
  "evidence": [
    {"metric": "<metric_name>", "value": <exact_value_from_context>}
  ],
  "next_step": {
    "type": "NONE" | "ACTION" | "INFORMATION" | "VERIFY",
    "label": "<actionable or informational step>"
  },
  "safety": {
    "financial_decision_made_by": "DETERMINISTIC_ENGINE",
    "llm_role": "EXPLANATION_ONLY"
  }
}
"""

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TIMEOUT_SECONDS = 15.0


def is_openai_available() -> bool:
    """Check whether an OpenAI API key is configured in the environment."""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    return bool(api_key)


def get_configured_model() -> str:
    """Retrieve configured OpenAI model from environment or fallback to default."""
    return os.environ.get("OPENAI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL


def generate_explanation(
    payload: Dict[str, Any],
    client: Optional[Any] = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> Optional[Dict[str, Any]]:
    """Invoke the OpenAI API to generate an explanation for a pre-computed financial decision.

    Args:
        payload: Full Phase 4 LLM input payload.
        client: Optional pre-configured OpenAI client (useful for unit testing / mocking).
        timeout: Request timeout in seconds.

    Returns:
        Optional[Dict[str, Any]]: Parsed JSON dictionary from the model response,
        or None if the API call fails, times out, or credentials are not configured.
    """
    if client is None:
        if not is_openai_available():
            logger.warning("OpenAI API key not set in environment. Skipping LLM generation.")
            return None
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        except Exception as e:
            logger.error("Failed to initialize OpenAI client: %s", type(e).__name__)
            return None

    model = get_configured_model()

    try:
        user_prompt = (
            f"Here is the authoritative financial and decision context:\n\n"
            f"{json.dumps(payload, indent=2)}\n\n"
            f"Please provide the structured explanation adhering strictly to the required schema."
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            timeout=timeout,
        )

        choice = response.choices[0]
        content = choice.message.content
        if not content:
            logger.warning("OpenAI returned an empty content string.")
            return None

        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            logger.warning("Parsed OpenAI response is not a JSON dictionary.")
            return None

        return parsed

    except Exception as e:
        # Catch network errors, timeouts, rate limits, json decoding errors, etc.
        logger.error("Error communicating with OpenAI API: %s: %s", type(e).__name__, str(e))
        return None
