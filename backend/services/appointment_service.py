"""Appointment Service for NeoBharat.

Orchestrates appointment workflows tied to the authoritative Decision Engine:
- SUPPORT decision (Rahul) -> Financial Advisor / Debt Restructuring consultation.
- VERIFY decision (Arjun) -> Security Specialist / Fraud Support consultation.
- RECOMMEND decision (Priya) -> Wealth Planning (voluntary, not aggressively pushed).

Performs strict validation and manages prototype advisor availability.
"""

from datetime import datetime, date
import logging
import re
from typing import Any, Dict, List, Optional

from backend.domain.decision_engine import evaluate_decision
from backend.domain.financial_metrics import calculate_financial_profile
from backend.repositories.appointment_repository import (
    create_appointment as repo_create,
    delete_appointment as repo_delete,
    get_appointment_by_id,
    get_appointments_by_customer,
    update_appointment as repo_update,
)
from backend.repositories.customer_repository import get_customer_by_id
from backend.repositories.transaction_repository import (
    get_all_transactions_for_customer_ordered,
)
from backend.services.guardian_service import evaluate_guardian

logger = logging.getLogger(__name__)

# Prototype advisor availability schedule
PROTOTYPE_SLOTS = ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]

VALID_ADVISOR_TYPES = {
    "FINANCIAL_ADVISOR",
    "SECURITY_SPECIALIST",
    "CREDIT_COUNSELOR",
    "WEALTH_PLANNER",
}

VALID_STATUSES = {"SCHEDULED", "COMPLETED", "CANCELLED"}

VALID_REASONS = {
    "FINANCIAL_STRESS",
    "FRAUD_VERIFICATION",
    "DEBT_RESTRUCTURING",
    "WEALTH_PLANNING",
    "REVIEW_UPCOMING_PAYMENTS",
    "GENERAL_CONSULTATION",
}


def get_available_slots(target_date: str, advisor_type: str = "FINANCIAL_ADVISOR") -> Dict[str, Any]:
    """Retrieve prototype advisor availability slots for a specific date.

    Labelled clearly as 'Prototype Advisor Availability'.

    Args:
        target_date: Date string 'YYYY-MM-DD'.
        advisor_type: One of VALID_ADVISOR_TYPES.

    Returns:
        Dict[str, Any]: Available slots and prototype notice.
    """
    validate_date_format(target_date)

    # In a full multi-tenant system we would query existing bookings for that advisor on that date.
    return {
        "date": target_date,
        "advisor_type": advisor_type,
        "available_slots": list(PROTOTYPE_SLOTS),
        "duration_minutes": 30,
        "notice": "Prototype Advisor Availability — Demonstration Schedule Only",
    }


def get_advisor_recommendation_for_customer(customer_id: int) -> Dict[str, Any]:
    """Check customer's authoritative decision and return appropriate appointment context.

    Returns context-aware advisor type and reason based strictly on backend truth:
    - SUPPORT -> FINANCIAL_ADVISOR (FINANCIAL_STRESS / REVIEW_UPCOMING_PAYMENTS)
    - VERIFY -> SECURITY_SPECIALIST (FRAUD_VERIFICATION)
    - RECOMMEND -> WEALTH_PLANNER (Optional)
    """
    customer = get_customer_by_id(customer_id)
    if not customer:
        raise ValueError(f"Customer with ID {customer_id} not found.")

    transactions = get_all_transactions_for_customer_ordered(customer_id, order="ASC")
    guardian = evaluate_guardian(customer, transactions)
    profile = calculate_financial_profile(transactions, customer)
    decision = evaluate_decision(guardian, profile, customer)
    decision_outcome = decision.get("outcome") if isinstance(decision, dict) else decision

    if decision_outcome == "SUPPORT":
        return {
            "should_offer": True,
            "advisor_type": "FINANCIAL_ADVISOR",
            "recommended_advisor_type": "FINANCIAL_ADVISOR",
            "reason": "FINANCIAL_STRESS",
            "recommended_reason": "Elevated debt burden and rising expenses. Recommended session focuses on debt management and budgeting.",
            "recommended_action": "REVIEW_UPCOMING_PAYMENTS",
            "suggested_action": "Review upcoming payments and optimize budget",
            "title": "Debt & Budgeting Advisory",
            "advisor_title": "Debt & Budgeting Advisory",
            "title_hindi": "वित्तीय तनाव एवं बजट परामर्श",
            "urgency": "HIGH",
            "recommended_duration_minutes": 30,
            "message": "A 30-minute zero-penalty session with a dedicated banking advisor to review expenses and upcoming EMIs.",
        }
    elif decision_outcome == "VERIFY":
        return {
            "should_offer": True,
            "advisor_type": "SECURITY_SPECIALIST",
            "recommended_advisor_type": "SECURITY_SPECIALIST",
            "reason": "FRAUD_VERIFICATION",
            "recommended_reason": "High-risk anomaly alert: unusual transaction detected. Immediate security audit recommended.",
            "recommended_action": "VERIFY_SUSPICIOUS_TRANSACTION",
            "suggested_action": "Verify transaction authenticity and secure account",
            "title": "Fraud & Security Investigation Support",
            "advisor_title": "Fraud & Security Specialist",
            "title_hindi": "धोखाधड़ी एवं सुरक्षा जांच सहायता",
            "urgency": "HIGH",
            "recommended_duration_minutes": 15,
            "message": "Speak with a cyber-fraud specialist regarding recent unusual account transactions.",
        }
    elif decision_outcome == "RECOMMEND":
        return {
            "should_offer": False,  # Responsible AI: Do not aggressively push appointments on healthy accounts
            "advisor_type": "WEALTH_PLANNER",
            "recommended_advisor_type": "WEALTH_PLANNER",
            "reason": "WEALTH_PLANNING",
            "recommended_reason": "Healthy surplus and zero debt. Advisory available for systematic long-term wealth building.",
            "recommended_action": "RECOMMEND",
            "suggested_action": "Explore disciplined micro-SIP and growth options",
            "title": "Voluntary Wealth Planning Consultation",
            "advisor_title": "Wealth & Investment Planner",
            "title_hindi": "ऐच्छिक वेल्थ प्लानिंग परामर्श",
            "urgency": "MEDIUM",
            "recommended_duration_minutes": 45,
            "message": "Optional wealth management consultation available on request.",
        }
    else:
        return {
            "should_offer": False,
            "advisor_type": "FINANCIAL_ADVISOR",
            "recommended_advisor_type": "FINANCIAL_ADVISOR",
            "reason": "GENERAL_CONSULTATION",
            "recommended_reason": "General account services and inquiries.",
            "recommended_action": "NO_ACTION",
            "suggested_action": "General inquiries",
            "title": "General Banking Inquiries",
            "advisor_title": "General Banking Inquiries",
            "title_hindi": "सामान्य बैंकिंग सहायता",
            "urgency": "LOW",
            "recommended_duration_minutes": 15,
            "message": "General banking assistance.",
        }


def book_appointment(customer_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and book a financial-advisor appointment for a customer.

    Args:
        customer_id: Integer ID of customer in SQLite.
        payload: Input dictionary with date, time, advisor_type, reason, etc.

    Returns:
        Dict[str, Any]: The booked appointment record.

    Raises:
        ValueError: If any validation rule fails.
    """
    # 1. Customer existence validation
    customer = get_customer_by_id(customer_id)
    if not customer:
        raise ValueError(f"Customer with ID {customer_id} does not exist.")

    # 2. Date validation
    date_str = str(payload.get("date", "")).strip()
    validate_date_format(date_str)

    # 3. Time slot validation
    time_str = str(payload.get("time", "")).strip()
    if not time_str:
        raise ValueError("Appointment time slot is required.")
    if time_str not in PROTOTYPE_SLOTS:
        raise ValueError(f"Invalid time format or unavailable time slot '{time_str}'. Allowed prototype slots: {PROTOTYPE_SLOTS}")

    # Duplicate booking prevention
    existing_customer_apts = get_appointments_by_customer(customer_id)
    for apt in existing_customer_apts:
        if apt.get("status") == "SCHEDULED" and apt.get("date") == date_str and apt.get("time") == time_str:
            raise ValueError(f"An active appointment is already scheduled on {date_str} at {time_str}.")

    # 4. Duration validation
    duration = payload.get("duration_minutes", 30)
    try:
        duration = int(duration)
        if duration not in (15, 30, 45, 60):
            raise ValueError()
    except (ValueError, TypeError):
        raise ValueError("Invalid duration_minutes. Must be one of 15, 30, 45, or 60 minutes.")

    # 5. Advisor type validation
    advisor_type = str(payload.get("advisor_type", "FINANCIAL_ADVISOR")).strip().upper()
    if advisor_type not in VALID_ADVISOR_TYPES:
        raise ValueError(f"Invalid advisor_type '{advisor_type}'. Supported: {sorted(list(VALID_ADVISOR_TYPES))}")

    # 6. Reason validation (supports predefined enum reasons and custom citizen notes)
    raw_reason = str(payload.get("reason", "GENERAL_CONSULTATION")).strip()
    if not raw_reason:
        reason = "GENERAL_CONSULTATION"
    elif raw_reason.upper() in VALID_REASONS:
        reason = raw_reason.upper()
    else:
        reason = raw_reason[:200]

    # 7. Status validation
    status = str(payload.get("status", "SCHEDULED")).strip().upper()
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Supported: {sorted(list(VALID_STATUSES))}")

    # 8. Construct clean record (no sensitive financial data exposed)
    appointment_data = {
        "customer_id": customer_id,
        "customer_name": customer.get("name", f"Customer {customer_id}"),
        "advisor_type": advisor_type,
        "reason": reason,
        "recommended_action": str(payload.get("recommended_action", "REVIEW")),
        "date": date_str,
        "time": time_str,
        "duration_minutes": duration,
        "language": str(payload.get("language", customer.get("language", "English"))).upper(),
        "status": status,
        "notes": str(payload.get("notes", "")).strip(),
    }

    return repo_create(appointment_data)


def list_customer_appointments(customer_id: int) -> List[Dict[str, Any]]:
    """Retrieve all appointments for a given customer."""
    customer = get_customer_by_id(customer_id)
    if not customer:
        raise ValueError(f"Customer with ID {customer_id} does not exist.")
    return get_appointments_by_customer(customer_id)


def get_appointment(appointment_id: str) -> Optional[Dict[str, Any]]:
    """Get appointment by ID."""
    return get_appointment_by_id(appointment_id)


VALID_TRANSITIONS = {
    "SCHEDULED": {"COMPLETED", "CANCELLED"},
    "COMPLETED": set(),  # Terminal state
    "CANCELLED": set(),  # Terminal state
}


def update_appointment_status(appointment_id: str, new_status: str, notes: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Transition an appointment's status, verifying state transition legality."""
    apt = get_appointment_by_id(appointment_id)
    if not apt:
        return None
    current_status = apt.get("status", "SCHEDULED")
    new_status_upper = new_status.strip().upper()
    if new_status_upper not in VALID_STATUSES:
        raise ValueError(f"Invalid status '{new_status_upper}'. Supported: {sorted(list(VALID_STATUSES))}")
    if new_status_upper != current_status and new_status_upper not in VALID_TRANSITIONS.get(current_status, set()):
        raise ValueError(f"Invalid appointment status transition from '{current_status}' to '{new_status_upper}'.")
    updates = {"status": new_status_upper}
    if notes:
        updates["notes"] = notes
    return repo_update(appointment_id, updates)


def cancel_appointment(appointment_id: str, reason: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Cancel an appointment and record the cancellation reason."""
    apt = get_appointment_by_id(appointment_id)
    if not apt:
        return None
    current_status = apt.get("status", "SCHEDULED")
    if current_status == "CANCELLED":
        return apt
    if current_status == "COMPLETED":
        raise ValueError("Cannot cancel an already completed appointment.")
    updates = {"status": "CANCELLED"}
    if reason:
        updates["notes"] = f"Cancelled: {reason}"
    return repo_update(appointment_id, updates)


def reschedule_appointment(
    appointment_id: str, new_date: str, new_time: str
) -> Optional[Dict[str, Any]]:
    """Reschedule date and time of an existing appointment."""
    apt = get_appointment_by_id(appointment_id)
    if not apt:
        return None
    if apt.get("status") in ("CANCELLED", "COMPLETED"):
        raise ValueError(f"Cannot reschedule an appointment in {apt.get('status')} state.")

    validate_date_format(new_date)
    if new_time not in PROTOTYPE_SLOTS:
        raise ValueError(f"Invalid or unavailable time slot '{new_time}'. Allowed prototype slots: {PROTOTYPE_SLOTS}")

    return repo_update(appointment_id, {"date": new_date, "time": new_time, "status": "SCHEDULED"})


def validate_date_format(date_str: str) -> None:
    """Validate that date_str is a valid YYYY-MM-DD date."""
    if not date_str:
        raise ValueError("Appointment date is required.")
    try:
        parsed = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Invalid date format '{date_str}'. Expected 'YYYY-MM-DD'.")
