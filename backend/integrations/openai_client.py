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
9. Answer the user's specific intent directly, rather than providing a generic response.
10. Respond in the requested language (English, Hindi in Devanagari script, or natural Hinglish in Latin script as detected).

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

DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_TIMEOUT_SECONDS = 15.0


def get_llm_provider() -> str:
    """Determine the active LLM provider ('groq' or 'openai').

    Priority:
    1. Explicit LLM_PROVIDER environment variable ('groq' or 'openai').
    2. Auto-detection: if GROQ_API_KEY is present -> 'groq'.
    3. Auto-detection: if OPENAI_API_KEY is present -> 'openai'.
    4. Default: 'groq'.
    """
    explicit = os.environ.get("LLM_PROVIDER", "").strip().lower()
    if explicit in ("groq", "openai"):
        return explicit
    if os.environ.get("GROQ_API_KEY", "").strip():
        return "groq"
    if os.environ.get("OPENAI_API_KEY", "").strip():
        return "openai"
    return "groq"


def is_llm_available() -> bool:
    """Check whether the active LLM provider has an API key configured."""
    provider = get_llm_provider()
    if provider == "groq":
        return bool(os.environ.get("GROQ_API_KEY", "").strip())
    return bool(os.environ.get("OPENAI_API_KEY", "").strip())


def is_openai_available() -> bool:
    """Backward-compatible alias for existing tests and consumers."""
    provider = get_llm_provider()
    if provider == "openai":
        return bool(os.environ.get("OPENAI_API_KEY", "").strip())
    return is_llm_available()


def get_configured_model() -> str:
    """Retrieve configured model for the active provider."""
    provider = get_llm_provider()
    if provider == "groq":
        return os.environ.get("GROQ_MODEL", DEFAULT_GROQ_MODEL).strip() or DEFAULT_GROQ_MODEL
    return os.environ.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL).strip() or DEFAULT_OPENAI_MODEL


def get_llm_client() -> Optional[Any]:
    """Initialize and return the OpenAI-compatible client for the active provider."""
    provider = get_llm_provider()
    if not is_llm_available():
        logger.warning(f"{provider.upper()} API key not set in environment. Skipping LLM generation.")
        return None

    try:
        from openai import OpenAI
        if provider == "groq":
            api_key = os.environ.get("GROQ_API_KEY", "").strip()
            base_url = os.environ.get("GROQ_BASE_URL", GROQ_BASE_URL).strip()
            return OpenAI(api_key=api_key, base_url=base_url)
        else:
            api_key = os.environ.get("OPENAI_API_KEY", "").strip()
            return OpenAI(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to initialize {provider.upper()} client: %s", type(e).__name__)
        return None


def generate_explanation(
    payload: Dict[str, Any],
    client: Optional[Any] = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    intent_obj: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Invoke the active LLM API (Groq primary, OpenAI fallback) to explain a pre-computed decision.

    Args:
        payload: Full Phase 4 LLM input payload.
        client: Optional pre-configured client (useful for unit testing / mocking).
        timeout: Request timeout in seconds.
        intent_obj: Optional Phase 7 intent detection result dictionary.

    Returns:
        Optional[Dict[str, Any]]: Parsed JSON dictionary from the model response,
        or None if the API call fails, times out, or credentials are not configured.
    """
    provider = get_llm_provider()

    if client is None:
        client = get_llm_client()
        if client is None:
            return None

    model = get_configured_model()

    try:
        prompt_lines = [
            "Here is the authoritative financial and decision context:\n",
            json.dumps(payload, indent=2),
            "\n",
        ]
        if intent_obj:
            intent = intent_obj.get("intent", "WHY_THIS_DECISION")
            lang = intent_obj.get("language", "ENGLISH")
            strat = intent_obj.get("response_strategy", "EXPLANATION")
            prompt_lines.append(
                f"Conversational Direction:\n"
                f"- Detected User Intent: {intent}\n"
                f"- User Language: {lang}\n"
                f"- Response Strategy: {strat}\n"
                f"- Instructions: Answer the user's specific intent directly and empathetically using the detected language "
                f"({lang}: English, Hindi in Devanagari script, or natural Hinglish in Latin script as detected). "
                f"Ground all statements strictly in the authoritative context above."
            )
        else:
            prompt_lines.append("Please provide the structured explanation adhering strictly to the required schema.")

        user_prompt = "\n".join(prompt_lines)

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
            logger.warning("%s returned an empty content string.", provider.upper())
            return None

        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            logger.warning("Parsed %s response is not a JSON dictionary.", provider.upper())
            return None

        return parsed

    except Exception as e:
        # Catch network errors, timeouts, rate limits, json decoding errors, etc.
        logger.error("Error communicating with %s API: %s: %s", provider.upper(), type(e).__name__, str(e))
        return None
