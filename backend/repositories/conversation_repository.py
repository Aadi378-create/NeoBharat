"""Conversation State Repository for NeoBharat.

Stores multi-turn conversational history and LangGraph state variables
in the 'conversations' Firestore collection.
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional

from backend.integrations.firebase_client import get_firestore_client

logger = logging.getLogger(__name__)
COLLECTION_NAME = "conversations"


def save_conversation_state(customer_id: int, state: Dict[str, Any]) -> None:
    """Save the persistent conversational state machine for a customer.

    Args:
        customer_id: SQLite customer ID.
        state: Dictionary holding conversation variables (current intent, confirmation state, etc.).
    """
    db = get_firestore_client()
    now_iso = datetime.now(timezone.utc).isoformat()
    doc_ref = db.collection(COLLECTION_NAME).document(str(customer_id))

    record = {
        "customer_id": int(customer_id),
        "state": state,
        "updated_at": now_iso,
    }
    doc_ref.set(record, merge=True)


def get_conversation_state(customer_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve the saved conversation state for a customer.

    Args:
        customer_id: SQLite customer ID.

    Returns:
        Optional[Dict[str, Any]]: The state dictionary if present.
    """
    db = get_firestore_client()
    doc = db.collection(COLLECTION_NAME).document(str(customer_id)).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    return data.get("state") if data else None


def append_conversation_turn(
    customer_id: int,
    user_message: str,
    response_message: str,
    intent: Optional[str] = None,
    decision: Optional[str] = None,
) -> None:
    """Append a dialog turn to the customer's history.

    Args:
        customer_id: SQLite customer ID.
        user_message: Input text from the citizen.
        response_message: Output text from SAKHI / OpenAI.
        intent: Detected intent.
        decision: Authoritative decision context.
    """
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(str(customer_id))
    doc = doc_ref.get()

    now_iso = datetime.now(timezone.utc).isoformat()
    turns = []
    if doc.exists:
        d = doc.to_dict()
        if d and "turns" in d:
            turns = d["turns"]

    turn_record = {
        "timestamp": now_iso,
        "user_message": user_message,
        "response_message": response_message,
        "intent": intent,
        "decision": decision,
    }
    turns.append(turn_record)

    # Keep last 20 turns to prevent unbounded document size
    if len(turns) > 20:
        turns = turns[-20:]

    doc_ref.set(
        {
            "customer_id": int(customer_id),
            "turns": turns,
            "last_updated": now_iso,
        },
        merge=True,
    )


def get_conversation_turns(customer_id: int) -> List[Dict[str, Any]]:
    """Get the recent conversation turns for a customer.

    Args:
        customer_id: SQLite customer ID.

    Returns:
        List[Dict[str, Any]]: List of turns.
    """
    db = get_firestore_client()
    doc = db.collection(COLLECTION_NAME).document(str(customer_id)).get()
    if not doc.exists:
        return []
    d = doc.to_dict()
    return d.get("turns", []) if d else []


def clear_conversation(customer_id: int) -> None:
    """Clear conversation history and state for a customer.

    Args:
        customer_id: SQLite customer ID.
    """
    db = get_firestore_client()
    db.collection(COLLECTION_NAME).document(str(customer_id)).delete()
