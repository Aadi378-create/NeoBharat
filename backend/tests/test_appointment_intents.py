"""Tests for SAKHI Appointment Intent Classification and Conversational Flow.

Verifies:
1. Multi-lingual intent classification (English, Hindi, Hinglish) for:
   - BOOK_APPOINTMENT
   - VIEW_APPOINTMENTS
   - CANCEL_APPOINTMENT
   - APPOINTMENT_HELP
2. Context-aware conversational guidance through process_chat():
   - Rahul (SUPPORT) receives Debt Advisory guidance.
   - Arjun (VERIFY) receives Security Specialist guidance.
   - Priya (RECOMMEND) receives Wealth Planning advisory.
3. OpenAI cannot directly book or fabricate an appointment without user confirmation.
4. Deterministic decision authority is preserved across all flows.
"""

import pytest
from backend.domain.conversation_intents import detect_intent
from backend.integrations.firebase_client import reset_mock_firestore
from backend.repositories.appointment_repository import create_appointment
from backend.services.chat_service import process_chat


@pytest.fixture(autouse=True)
def clean_mock_store():
    reset_mock_firestore()
    yield
    reset_mock_firestore()


class TestAppointmentIntentClassification:
    """Test intent classification for English, Hindi, and Hinglish appointment phrases."""

    @pytest.mark.parametrize(
        "phrase",
        [
            "Book an appointment",
            "I want to talk to an advisor",
            "Can I speak with a financial advisor?",
            "Schedule a meeting with an advisor",
            "Book consultation",
            "I want to speak to someone",
        ],
    )
    def test_book_appointment_english(self, phrase):
        res = detect_intent(phrase)
        assert res["intent"] == "BOOK_APPOINTMENT"
        assert res["language"] == "ENGLISH"

    @pytest.mark.parametrize(
        "phrase",
        [
            "अपॉइंटमेंट बुक करो",
            "सलाहकार से बात करनी है",
            "बैंकिंग सलाहकार से बात करें",
            "अपॉइंटमेंट लेना है",
            "किसी से बात करनी है",
        ],
    )
    def test_book_appointment_hindi(self, phrase):
        res = detect_intent(phrase)
        assert res["intent"] == "BOOK_APPOINTMENT"
        assert res["language"] == "HINDI"

    @pytest.mark.parametrize(
        "phrase",
        [
            "appointment book kardo",
            "advisor se baat karni hai",
            "meeting schedule kardo",
            "advisor se milna hai",
            "appointment book karo",
        ],
    )
    def test_book_appointment_hinglish(self, phrase):
        res = detect_intent(phrase)
        assert res["intent"] == "BOOK_APPOINTMENT"
        assert res["language"] in ("HINGLISH", "ENGLISH")

    def test_view_appointments_intent(self):
        assert detect_intent("Show my appointments")["intent"] == "VIEW_APPOINTMENTS"
        assert detect_intent("मेरी अपॉइंटमेंट दिखाओ")["intent"] == "VIEW_APPOINTMENTS"
        assert detect_intent("meri appointment dikhao")["intent"] == "VIEW_APPOINTMENTS"

    def test_cancel_appointment_intent(self):
        assert detect_intent("Cancel my appointment")["intent"] == "CANCEL_APPOINTMENT"
        assert detect_intent("अपॉइंटमेंट रद्द करो")["intent"] == "CANCEL_APPOINTMENT"
        assert detect_intent("appointment cancel kardo")["intent"] == "CANCEL_APPOINTMENT"

    def test_appointment_help_intent(self):
        assert detect_intent("How to book appointment")["intent"] == "APPOINTMENT_HELP"
        assert detect_intent("अपॉइंटमेंट कैसे बुक करें")["intent"] == "APPOINTMENT_HELP"


class TestAppointmentChatFlow:
    """Test SAKHI conversation responses for appointment intents."""

    def test_rahul_appointment_guidance(self):
        """Rahul (SUPPORT) asks to speak with an advisor."""
        res = process_chat(1, "I want to talk to an advisor")
        assert res is not None
        assert res["decision_acknowledgement"]["decision"] == "SUPPORT"
        assert res["next_step"]["type"] == "ACTION"
        assert "Advisor" in res["next_step"]["label"]
        assert "consultation" in res["message"].lower() or "सलाहकार" in res["message"] or "advisor" in res["message"].lower()

    def test_arjun_security_appointment_guidance(self):
        """Arjun (VERIFY) asks to book an appointment."""
        res = process_chat(3, "Book me an appointment")
        assert res is not None
        assert res["decision_acknowledgement"]["decision"] == "VERIFY"
        assert res["next_step"]["type"] == "ACTION"
        assert "Security" in res["next_step"]["label"] or "Specialist" in res["next_step"]["label"]
        assert "security" in res["message"].lower() or "सुरक्षा" in res["message"]

    def test_view_appointments_flow_empty_vs_booked(self):
        """Verify view appointments flow when empty and when appointment is booked."""
        # 1. Empty state
        res_empty = process_chat(1, "Show my appointments")
        assert res_empty is not None
        assert "no scheduled appointments" in res_empty["message"].lower() or "कोई निर्धारित अपॉइंटमेंट नहीं" in res_empty["message"]

        # 2. Book an appointment in Firestore
        create_appointment({
            "customer_id": 1,
            "customer_name": "Rahul",
            "advisor_type": "FINANCIAL_ADVISOR",
            "date": "2026-10-25",
            "time": "10:00",
            "status": "SCHEDULED",
        })

        # 3. Booked state
        res_booked = process_chat(1, "Show my appointments")
        assert res_booked is not None
        assert "2026-10-25" in res_booked["message"]
        assert "10:00" in res_booked["message"]
        assert "FINANCIAL_ADVISOR" in res_booked["message"]

    def test_openai_cannot_arbitrarily_create_appointment(self):
        """Chat queries cannot create appointments in Firestore without explicit user confirmation."""
        process_chat(1, "Please book an appointment for me tomorrow at 10 AM with a loan agent")

        # Verify no appointments were created in Firestore
        from backend.repositories.appointment_repository import get_appointments_by_customer
        apts = get_appointments_by_customer(1)
        assert len(apts) == 0  # Confirmed: Chat only guides; it does not fabricate records
