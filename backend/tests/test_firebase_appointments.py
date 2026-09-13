"""Unit and Integration Tests for Firebase & Financial Advisor Appointment System.

Verifies:
1. MockFirestoreClient operations (CRUD, where filtering, stream, limit).
2. Appointment repository (create, get, customer isolation, update, delete).
3. Appointment service validation (invalid customer, invalid date, invalid time, invalid duration, invalid type/reason).
4. Context-aware advisor recommendations for Rahul, Priya, and Arjun.
5. Appointment REST API endpoints (GET, POST, PATCH, DELETE, availability).
"""

import pytest
from backend.app import create_app
from backend.integrations.firebase_client import (
    MockFirestoreClient,
    get_firestore_client,
    reset_mock_firestore,
)
from backend.repositories.appointment_repository import (
    create_appointment,
    delete_appointment,
    get_appointment_by_id,
    get_appointments_by_customer,
    update_appointment,
)
from backend.services.appointment_service import (
    book_appointment,
    cancel_appointment,
    get_advisor_recommendation_for_customer,
    get_available_slots,
    reschedule_appointment,
)


@pytest.fixture(autouse=True)
def clean_mock_store():
    """Reset mock store before and after each test."""
    reset_mock_firestore()
    yield
    reset_mock_firestore()


@pytest.fixture
def client():
    """Create a Flask test client."""
    app = create_app({"TESTING": True})
    with app.test_client() as c:
        yield c


class TestMockFirestore:
    """Test suite for MockFirestoreClient fidelity."""

    def test_mock_document_crud(self):
        client = MockFirestoreClient()
        col = client.collection("test_col")

        # Create
        col.document("doc1").set({"phone": "9999999999", "pin": "123456", "name": "Test", "count": 42})

        # Read
        doc = col.document("doc1").get()
        assert doc.exists is True
        assert doc.to_dict() == {"phone": "9999999999", "pin": "123456", "name": "Test", "count": 42}

        # Update
        col.document("doc1").update({"count": 43})
        assert col.document("doc1").get().to_dict()["count"] == 43

        # Delete
        col.document("doc1").delete()
        assert col.document("doc1").get().exists is False

    def test_mock_query_filtering(self):
        client = MockFirestoreClient()
        col = client.collection("records")

        col.document("r1").set({"user_id": 1, "status": "ACTIVE", "score": 90})
        col.document("r2").set({"user_id": 1, "status": "PENDING", "score": 70})
        col.document("r3").set({"user_id": 2, "status": "ACTIVE", "score": 85})

        # Filter by user_id
        q1 = col.where("user_id", "==", 1).stream()
        assert len(q1) == 2

        # Filter by user_id and status
        q2 = col.where("user_id", "==", 1).where("status", "==", "ACTIVE").stream()
        assert len(q2) == 1
        assert q2[0].to_dict()["score"] == 90


class TestAppointmentRepository:
    """Test suite for appointment_repository functions."""

    def test_create_and_retrieve_appointment(self):
        data = {
            "customer_id": 1,
            "customer_name": "Rahul",
            "advisor_type": "FINANCIAL_ADVISOR",
            "reason": "FINANCIAL_STRESS",
            "date": "2026-10-15",
            "time": "10:00",
            "duration_minutes": 30,
            "status": "SCHEDULED",
        }
        created = create_appointment(data)
        assert created["appointment_id"].startswith("apt-")
        assert created["customer_id"] == 1
        assert created["status"] == "SCHEDULED"

        fetched = get_appointment_by_id(created["appointment_id"])
        assert fetched is not None
        assert fetched["customer_name"] == "Rahul"

    def test_customer_appointment_isolation(self):
        create_appointment({
            "customer_id": 1,
            "customer_name": "Rahul",
            "date": "2026-10-15",
            "time": "10:00",
        })
        create_appointment({
            "customer_id": 2,
            "customer_name": "Priya",
            "date": "2026-10-16",
            "time": "14:00",
        })

        rahul_apts = get_appointments_by_customer(1)
        priya_apts = get_appointments_by_customer(2)

        assert len(rahul_apts) == 1
        assert rahul_apts[0]["customer_name"] == "Rahul"
        assert len(priya_apts) == 1
        assert priya_apts[0]["customer_name"] == "Priya"

    def test_update_and_delete_appointment(self):
        created = create_appointment({
            "customer_id": 1,
            "date": "2026-10-15",
            "time": "10:00",
        })
        apt_id = created["appointment_id"]

        updated = update_appointment(apt_id, {"status": "CANCELLED"})
        assert updated["status"] == "CANCELLED"

        deleted = delete_appointment(apt_id)
        assert deleted is True
        assert get_appointment_by_id(apt_id) is None


class TestAppointmentServiceValidation:
    """Test suite for strict business logic validation."""

    def test_book_appointment_valid(self):
        apt = book_appointment(1, {
            "date": "2026-10-20",
            "time": "11:00",
            "advisor_type": "FINANCIAL_ADVISOR",
            "reason": "FINANCIAL_STRESS",
            "duration_minutes": 30,
        })
        assert apt["customer_id"] == 1
        assert apt["status"] == "SCHEDULED"
        assert apt["date"] == "2026-10-20"

    def test_book_appointment_invalid_customer(self):
        with pytest.raises(ValueError, match="does not exist"):
            book_appointment(9999, {
                "date": "2026-10-20",
                "time": "11:00",
            })

    def test_book_appointment_invalid_date(self):
        with pytest.raises(ValueError, match="Invalid date format"):
            book_appointment(1, {
                "date": "20-10-2026",  # wrong format
                "time": "11:00",
            })

    def test_book_appointment_invalid_time(self):
        with pytest.raises(ValueError, match="Invalid time format"):
            book_appointment(1, {
                "date": "2026-10-20",
                "time": "invalid_time",
            })

    def test_book_appointment_invalid_duration(self):
        with pytest.raises(ValueError, match="Invalid duration_minutes"):
            book_appointment(1, {
                "date": "2026-10-20",
                "time": "11:00",
                "duration_minutes": 120,  # exceeds maximum 60
            })

    def test_book_appointment_invalid_advisor_type(self):
        with pytest.raises(ValueError, match="Invalid advisor_type"):
            book_appointment(1, {
                "date": "2026-10-20",
                "time": "11:00",
                "advisor_type": "UNKNOWN_SALESMAN",
            })

    def test_cancel_and_reschedule(self):
        apt = book_appointment(1, {
            "date": "2026-10-20",
            "time": "11:00",
        })
        apt_id = apt["appointment_id"]

        rescheduled = reschedule_appointment(apt_id, "2026-10-21", "14:00")
        assert rescheduled["date"] == "2026-10-21"
        assert rescheduled["time"] == "14:00"

        cancelled = cancel_appointment(apt_id, reason="Citizen request")
        assert cancelled["status"] == "CANCELLED"
        assert "Citizen request" in cancelled["notes"]

    def test_context_aware_advisor_recommendations(self):
        # Rahul -> SUPPORT -> FINANCIAL_ADVISOR / FINANCIAL_STRESS
        rahul_rec = get_advisor_recommendation_for_customer(1)
        assert rahul_rec["should_offer"] is True
        assert rahul_rec["advisor_type"] == "FINANCIAL_ADVISOR"
        assert rahul_rec["reason"] == "FINANCIAL_STRESS"

        # Priya -> RECOMMEND -> WEALTH_PLANNER (Voluntary, should_offer is False)
        priya_rec = get_advisor_recommendation_for_customer(2)
        assert priya_rec["should_offer"] is False
        assert priya_rec["advisor_type"] == "WEALTH_PLANNER"

        # Arjun -> VERIFY -> SECURITY_SPECIALIST / FRAUD_VERIFICATION
        arjun_rec = get_advisor_recommendation_for_customer(3)
        assert arjun_rec["should_offer"] is True
        assert arjun_rec["advisor_type"] == "SECURITY_SPECIALIST"
        assert arjun_rec["reason"] == "FRAUD_VERIFICATION"


class TestAppointmentRoutesAPI:
    """Test suite for HTTP REST API routes."""

    def test_get_availability_route(self, client):
        res = client.get("/api/appointments/availability?date=2026-10-20")
        assert res.status_code == 200
        data = res.get_json()
        assert "available_slots" in data
        assert len(data["available_slots"]) == 6
        assert "Prototype Advisor Availability" in data["notice"]

    def test_book_appointment_route_success(self, client):
        payload = {
            "date": "2026-10-25",
            "time": "10:00",
            "advisor_type": "FINANCIAL_ADVISOR",
            "reason": "FINANCIAL_STRESS",
            "duration_minutes": 30,
            "language": "HINDI",
        }
        res = client.post("/api/customers/1/appointments", json=payload)
        assert res.status_code == 201
        data = res.get_json()
        assert data["customer_id"] == 1
        assert data["status"] == "SCHEDULED"
        assert data["language"] == "HINDI"

    def test_book_appointment_route_validation_error(self, client):
        payload = {
            "date": "invalid-date",
            "time": "10:00",
        }
        res = client.post("/api/customers/1/appointments", json=payload)
        assert res.status_code == 400
        assert "error" in res.get_json()

    def test_get_customer_appointments_route(self, client):
        # Book one appointment for Rahul
        client.post("/api/customers/1/appointments", json={
            "date": "2026-10-25",
            "time": "10:00",
        })

        res = client.get("/api/customers/1/appointments")
        assert res.status_code == 200
        data = res.get_json()
        assert len(data) == 1
        assert data[0]["customer_id"] == 1

        # Customer 2 should have 0 appointments
        res2 = client.get("/api/customers/2/appointments")
        assert res2.status_code == 200
        assert len(res2.get_json()) == 0

    def test_patch_and_delete_routes(self, client):
        post_res = client.post("/api/customers/1/appointments", json={
            "date": "2026-10-25",
            "time": "10:00",
        })
        apt_id = post_res.get_json()["appointment_id"]

        # Patch (cancel)
        patch_res = client.patch(f"/api/appointments/{apt_id}", json={"status": "CANCELLED"})
        assert patch_res.status_code == 200
        assert patch_res.get_json()["status"] == "CANCELLED"

        # Delete
        del_res = client.delete(f"/api/appointments/{apt_id}")
        assert del_res.status_code == 200

        # Get should now show cancelled or 404
        get_res = client.get(f"/api/appointments/{apt_id}")
        assert get_res.status_code == 404 or get_res.get_json()["status"] == "CANCELLED"
