"""In-Memory Conversation Context Store for NeoBharat (Phase 7).

Tracks lightweight server-side conversational state per customer to enable
accurate resolution of follow-up queries (e.g. 'Why?', 'What should I do?').

Guarantees:
- Minimal state: strictly stores last_intent, last_topic, last_language, last_decision, last_response_type.
- Zero raw transactions, credit card numbers, or PII stored.
- Context never overrides authoritative financial metrics or decisions.
"""

from typing import Any, Dict, Optional

# Thread-safe in-memory store: customer_id -> context dictionary
_CONVERSATION_STORE: Dict[int, Dict[str, Any]] = {}


def get_conversation_context(customer_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve the recent conversational context for a given customer ID."""
    if not isinstance(customer_id, int):
        return None
    return _CONVERSATION_STORE.get(customer_id)


def update_conversation_context(
    customer_id: int,
    intent: str,
    language: str,
    response_type: str,
    decision: str,
    topic: str,
) -> None:
    """Update conversation context after processing a user query.

    Args:
        customer_id: The customer ID.
        intent: Detected intent string (e.g. 'WHY_NO_LOAN').
        language: Detected language ('ENGLISH', 'HINDI', 'HINGLISH').
        response_type: The Phase 4 response_type enum.
        decision: Authoritative decision ('SUPPORT', 'RECOMMEND', 'VERIFY').
        topic: Intent topic group ('LOAN', 'FRAUD', 'INVESTMENTS', etc.).
    """
    if not isinstance(customer_id, int):
        return

    _CONVERSATION_STORE[customer_id] = {
        "customer_id": customer_id,
        "last_intent": intent,
        "last_language": language,
        "last_response_type": response_type,
        "last_decision": decision,
        "last_topic": topic,
    }


def clear_conversation_context(customer_id: Optional[int] = None) -> None:
    """Clear conversational context for a customer, or all customers if None."""
    if customer_id is None:
        _CONVERSATION_STORE.clear()
    else:
        _CONVERSATION_STORE.pop(customer_id, None)
