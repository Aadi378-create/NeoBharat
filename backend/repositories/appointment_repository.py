"""Appointment Repository for NeoBharat.

Handles CRUD operations on the 'appointments' collection in Firestore.
Decoupled from whether Firestore is live or using MockFirestoreClient.
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional
import uuid

from backend.integrations.firebase_client import get_firestore_client

logger = logging.getLogger(__name__)
COLLECTION_NAME = "appointments"


def create_appointment(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new appointment record in Firestore.

    Args:
        data: Appointment dictionary containing required fields.

    Returns:
        Dict[str, Any]: The saved appointment record including generated appointment_id and timestamps.
    """
    db = get_firestore_client()
    now_iso = datetime.now(timezone.utc).isoformat()

    appointment_id = data.get("appointment_id") or f"apt-{uuid.uuid4().hex[:8]}"

    record = {
        "id": appointment_id,
        "appointment_id": appointment_id,
        "customer_id": int(data["customer_id"]),
        "customer_name": str(data.get("customer_name", "")),
        "advisor_type": str(data.get("advisor_type", "FINANCIAL_ADVISOR")),
        "reason": str(data.get("reason", "GENERAL_CONSULTATION")),
        "recommended_action": str(data.get("recommended_action", "REVIEW")),
        "date": str(data["date"]),
        "time": str(data["time"]),
        "duration_minutes": int(data.get("duration_minutes", 30)),
        "language": str(data.get("language", "English")).upper(),
        "status": str(data.get("status", "SCHEDULED")).upper(),
        "notes": str(data.get("notes", "")),
        "created_at": now_iso,
        "updated_at": now_iso,
    }

    db.collection(COLLECTION_NAME).document(appointment_id).set(record)
    logger.info("Created appointment %s for customer %s.", appointment_id, record["customer_id"])
    return record


def get_appointment_by_id(appointment_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve an appointment by its ID.

    Args:
        appointment_id: Unique string identifier.

    Returns:
        Optional[Dict[str, Any]]: Appointment dictionary if found, else None.
    """
    db = get_firestore_client()
    doc = db.collection(COLLECTION_NAME).document(appointment_id).get()
    if not doc.exists:
        return None
    return doc.to_dict()


def get_appointments_by_customer(customer_id: int) -> List[Dict[str, Any]]:
    """Retrieve all appointments booked for a specific customer.

    Args:
        customer_id: Integer ID of customer in SQLite.

    Returns:
        List[Dict[str, Any]]: List of appointment dictionaries.
    """
    db = get_firestore_client()
    query = db.collection(COLLECTION_NAME).where("customer_id", "==", int(customer_id))
    docs = query.stream()

    results = []
    for doc in docs:
        d = doc.to_dict()
        if d:
            results.append(d)

    # Sort descending by date and time
    results.sort(key=lambda x: (x.get("date", ""), x.get("time", "")), reverse=True)
    return results


def update_appointment(appointment_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update fields of an existing appointment.

    Args:
        appointment_id: Appointment identifier.
        updates: Dictionary of fields to update.

    Returns:
        Optional[Dict[str, Any]]: Updated appointment or None if not found.
    """
    db = get_firestore_client()
    ref = db.collection(COLLECTION_NAME).document(appointment_id)
    doc = ref.get()
    if not doc.exists:
        return None

    clean_updates = {k: v for k, v in updates.items() if k not in ("appointment_id", "created_at")}
    clean_updates["updated_at"] = datetime.now(timezone.utc).isoformat()

    ref.update(clean_updates)
    updated_doc = ref.get()
    return updated_doc.to_dict()


def delete_appointment(appointment_id: str) -> bool:
    """Delete or cancel an appointment from Firestore.

    Args:
        appointment_id: Appointment identifier.

    Returns:
        bool: True if deleted successfully, False if not found.
    """
    db = get_firestore_client()
    ref = db.collection(COLLECTION_NAME).document(appointment_id)
    doc = ref.get()
    if not doc.exists:
        return False

    ref.delete()
    logger.info("Deleted appointment %s.", appointment_id)
    return True
