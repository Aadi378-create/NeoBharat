"""Integration tests for Customer Onboarding, Transaction Logging, and Firestore Sync.

Verifies:
1. Citizen onboarding via POST /api/customers.
2. Consent enforcement and input validation.
3. Prototype transaction logging via POST /api/customers/<id>/transactions.
4. Deterministic profile and Guardian evaluation on new customers (with 0 and with N transactions).
5. Dynamic customer list updates.
6. SAKHI conversational support for new customers.
7. Customer data isolation (does not alter Rahul, Priya, or Arjun).
"""

import json
import pytest
import tempfile
import os

from backend.app import create_app
from backend.integrations.firebase_client import get_firestore_client, reset_mock_firestore


@pytest.fixture
def client():
    """Create Flask test client with test configuration."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    try:
        app = create_app({"TESTING": True, "DATABASE_PATH": db_path})
        with app.test_client() as client:
            yield client
    finally:
        try:
            os.unlink(db_path)
        except OSError:
            pass


def test_customer_onboarding_success(client):
    """Test successful onboarding of a new citizen (Amit Sharma)."""
    payload = {
        "phone": "9999999999", "pin": "123456", "name": "Amit Sharma",
        "age": 34,
        "language": "hi",
        "monthly_income": 35000.0,
        "monthly_emi": 5000.0,
        "consent": True,
    }

    resp = client.post("/api/customers", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()

    assert data["name"] == "Amit Sharma"
    assert data["language"] == "hi"
    assert data["monthly_income"] == 35000.0
    assert data["monthly_emi"] == 5000.0
    assert data["id"] is not None
    customer_id = data["id"]

    # Verify customer appears in list of all customers
    list_resp = client.get("/api/customers")
    assert list_resp.status_code == 200
    all_customers = list_resp.get_json()
    customer_ids = [c["id"] for c in all_customers]
    assert customer_id in customer_ids

    # Verify customer exists in Firestore
    db = get_firestore_client()
    doc = db.collection("customers").document(str(customer_id)).get()
    assert doc.exists
    doc_dict = doc.to_dict()
    assert doc_dict["name"] == "Amit Sharma"
    assert doc_dict["consent"] is True


def test_customer_onboarding_validation_failures(client):
    """Test DPDP consent enforcement and input validation."""
    # 1. Missing DPDP Consent
    resp1 = client.post(
        "/api/customers",
        json={"phone": "9999999999", "pin": "123456", "name": "No Consent Citizen", "monthly_income": 40000.0, "consent": False},
    )
    assert resp1.status_code == 400
    assert "consent" in resp1.get_json()["error"].lower()

    # 2. Missing name
    resp2 = client.post(
        "/api/customers",
        json={"phone": "9999999999", "pin": "123456", "name": "   ", "monthly_income": 40000.0, "consent": True},
    )
    assert resp2.status_code == 400
    assert "name" in resp2.get_json()["error"].lower()

    # 3. Missing monthly income
    resp3 = client.post(
        "/api/customers",
        json={"phone": "9999999999", "pin": "123456", "name": "Valid Name", "consent": True},
    )
    assert resp3.status_code == 400
    assert "monthly_income" in resp3.get_json()["error"].lower()

    # 4. Negative monthly income
    resp4 = client.post(
        "/api/customers",
        json={"phone": "9999999999", "pin": "123456", "name": "Valid Name", "monthly_income": -100.0, "consent": True},
    )
    assert resp4.status_code == 400
    assert "non-negative" in resp4.get_json()["error"].lower()


def test_new_customer_with_zero_transactions(client):
    """Test deterministic profile, Guardian, and recommendation for new customer with 0 transactions."""
    # Onboard
    onboard_resp = client.post(
        "/api/customers",
        json={
            "phone": "9999999999", "pin": "123456", "name": "Kavita Patel",
            "age": 28,
            "language": "en",
            "monthly_income": 50000.0,
            "monthly_emi": 0.0,
            "consent": True,
        },
    )
    assert onboard_resp.status_code == 201
    cid = onboard_resp.get_json()["id"]

    # 1. Profile with 0 transactions
    prof_resp = client.get(f"/api/customers/{cid}/profile")
    assert prof_resp.status_code == 200
    prof = prof_resp.get_json()
    assert prof["income"] == 50000.0
    assert prof["monthly_spending"] == 0.0
    assert prof["estimated_savings"] == 50000.0
    assert prof["spending_trend"] == "STABLE"

    # 2. Guardian with 0 transactions: No fabricated fraud or fake risk
    guard_resp = client.get(f"/api/customers/{cid}/guardian")
    assert guard_resp.status_code == 200
    guard = guard_resp.get_json()
    assert guard["status"] == "NO_ACTION"
    assert guard["scores"]["fraud_score"] == 0
    assert guard["scores"]["financial_stress_score"] == 0

    # 3. Recommendation with 0 transactions
    rec_resp = client.get(f"/api/customers/{cid}/recommendation")
    assert rec_resp.status_code == 200
    rec = rec_resp.get_json()
    assert "decision" in rec
    assert rec["grievance"]["available"] is True


def test_transaction_logging_and_subsequent_profile(client):
    """Test logging prototype transactions and verifying updated deterministic profile."""
    # Onboard
    onboard_resp = client.post(
        "/api/customers",
        json={
            "phone": "9999999999", "pin": "123456", "name": "Rajesh Verma",
            "age": 42,
            "language": "hi",
            "monthly_income": 40000.0,
            "monthly_emi": 8000.0,
            "consent": True,
        },
    )
    cid = onboard_resp.get_json()["id"]

    # Add Salary Credit
    tx1_resp = client.post(
        f"/api/customers/{cid}/transactions",
        json={
            "amount": 40000.0,
            "type": "CREDIT",
            "category": "SALARY",
            "merchant": "Employer Payroll",
            "status": "SUCCESS",
        },
    )
    assert tx1_resp.status_code == 201
    tx1 = tx1_resp.get_json()
    assert tx1["id"] is not None
    assert tx1["amount"] == 40000.0

    # Add Grocery Debit
    tx2_resp = client.post(
        f"/api/customers/{cid}/transactions",
        json={
            "amount": 3500.0,
            "type": "DEBIT",
            "category": "FOOD",
            "merchant": "Local Kirana",
            "status": "SUCCESS",
        },
    )
    assert tx2_resp.status_code == 201

    # Add EMI Debit
    tx3_resp = client.post(
        f"/api/customers/{cid}/transactions",
        json={
            "amount": 8000.0,
            "type": "DEBIT",
            "category": "EMI",
            "merchant": "Home Finance Bank",
            "status": "SUCCESS",
        },
    )
    assert tx3_resp.status_code == 201

    # Check transactions list
    tx_list_resp = client.get(f"/api/customers/{cid}/transactions")
    assert tx_list_resp.status_code == 200
    txns = tx_list_resp.get_json()
    assert len(txns) == 3

    # Check updated deterministic profile
    prof_resp = client.get(f"/api/customers/{cid}/profile")
    assert prof_resp.status_code == 200
    prof = prof_resp.get_json()
    assert prof["income"] == 40000.0
    assert prof["monthly_spending"] == 11500.0  # 3500 + 8000
    assert prof["emi"] == 8000.0
    assert prof["discretionary_spending"] == 3500.0
    assert prof["estimated_savings"] == 28500.0  # 40000 - 11500


def test_transaction_logging_validation_failures(client):
    """Test validation errors when logging transactions."""
    # Non-existent customer
    resp1 = client.post(
        "/api/customers/99999/transactions",
        json={"amount": 500.0, "type": "DEBIT", "category": "FOOD"},
    )
    assert resp1.status_code == 404

    # Onboard valid customer
    onboard_resp = client.post(
        "/api/customers",
        json={"phone": "9999999999", "pin": "123456", "name": "Test User", "monthly_income": 20000.0, "consent": True},
    )
    cid = onboard_resp.get_json()["id"]

    # Invalid amount
    resp2 = client.post(
        f"/api/customers/{cid}/transactions",
        json={"amount": -50.0, "type": "DEBIT", "category": "FOOD"},
    )
    assert resp2.status_code == 400

    # Invalid type
    resp3 = client.post(
        f"/api/customers/{cid}/transactions",
        json={"amount": 100.0, "type": "UNKNOWN", "category": "FOOD"},
    )
    assert resp3.status_code == 400

    # Invalid category
    resp4 = client.post(
        f"/api/customers/{cid}/transactions",
        json={"amount": 100.0, "type": "DEBIT", "category": "CRYPTO_GAMBLING"},
    )
    assert resp4.status_code == 400


def test_sakhi_chat_for_new_customer(client):
    """Test SAKHI conversation with new customer using authoritative backend context."""
    onboard_resp = client.post(
        "/api/customers",
        json={
            "phone": "9999999999",
            "pin": "123456",
            "name": "Amit Sharma",
            "age": 34,
            "language": "hi",
            "monthly_income": 35000.0,
            "monthly_emi": 5000.0,
            "consent": True,
        },
    )
    cid = onboard_resp.get_json()["id"]

    chat_payload = {
        "customer_id": cid,
        "message": "नमस्ते सखी, मेरा मासिक खर्च और बचत क्या है?",
    }

    resp = client.post("/api/chat", json=chat_payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "natural_language_explanation" in data or "message" in data
    message_text = data.get("natural_language_explanation") or data.get("message")
    assert len(message_text) > 0


def test_customer_isolation(client):
    """Verify that onboarding and logging transactions for a new customer does not affect seed personas."""
    # Check seed customers 1, 2, 3
    r1 = client.get("/api/customers/1").get_json()
    r2 = client.get("/api/customers/2").get_json()
    r3 = client.get("/api/customers/3").get_json()
    assert r1["name"] == "Rahul"
    assert r2["name"] == "Priya"
    assert r3["name"] == "Arjun"

    # Onboard customer 4
    onboard_resp = client.post(
        "/api/customers",
        json={"phone": "9999999999", "pin": "123456", "name": "New Person", "monthly_income": 60000.0, "consent": True},
    )
    new_cid = onboard_resp.get_json()["id"]

    # Log high debit on customer 4
    client.post(
        f"/api/customers/{new_cid}/transactions",
        json={"amount": 40000.0, "type": "DEBIT", "category": "SHOPPING"},
    )

    # Verify Rahul's profile remains untouched
    rahul_prof = client.get("/api/customers/1/profile").get_json()
    assert rahul_prof["income"] == 45000.0
    assert rahul_prof["emi"] == 14000.0
