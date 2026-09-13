import pytest
import tempfile
import os
from backend.app import create_app
from backend.database.connection import get_db_connection

@pytest.fixture
def client():
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

def test_insufficient_data_new_user(client):
    # Create disposable customer
    res = client.post("/api/customers", json={"name": "New User", "phone": "5555555555", "pin": "123456", "monthly_income": 3000, "age": 20, "language": "en", "consent": True})
    cust_id = res.get_json()["id"]

    # Login
    client.post("/api/auth/login", json={"phone": "5555555555", "pin": "123456"})

    # Check initial profile
    p1 = client.get(f"/api/customers/{cust_id}/profile").get_json()
    assert p1["income"] == 3000.0
    assert p1["monthly_spending"] == 0.0
    assert p1["estimated_savings"] == 3000.0

    # Add 500 DEBIT
    client.post(f"/api/customers/{cust_id}/transactions", json={"amount": 500, "type": "DEBIT", "category": "FOOD"})
    p2 = client.get(f"/api/customers/{cust_id}/profile").get_json()
    assert p2["monthly_spending"] == 500.0
    assert p2["estimated_savings"] == 2500.0
    assert p2["income"] == 3000.0 # Unchanged

    # Add 1000 CREDIT SALARY
    client.post(f"/api/customers/{cust_id}/transactions", json={"amount": 1000, "type": "CREDIT", "category": "SALARY"})
    p3 = client.get(f"/api/customers/{cust_id}/profile").get_json()
    assert p3["income"] == 1000.0 # Because calculated income takes over
    assert p3["estimated_savings"] == 500.0

def test_transaction_validation(client):
    res = client.post("/api/customers", json={"name": "Txn Valid", "phone": "5555555555", "pin": "123456", "monthly_income": 3000, "age": 20, "language": "en", "consent": True})
    cust_id = res.get_json()["id"]
    client.post("/api/auth/login", json={"phone": "5555555555", "pin": "123456"})

    # Invalid amount
    assert client.post(f"/api/customers/{cust_id}/transactions", json={"amount": -100, "type": "DEBIT", "category": "FOOD"}).status_code == 400
    assert client.post(f"/api/customers/{cust_id}/transactions", json={"amount": "abc", "type": "DEBIT", "category": "FOOD"}).status_code == 400

    # Invalid type
    assert client.post(f"/api/customers/{cust_id}/transactions", json={"amount": 100, "type": "INVALID_TYPE", "category": "FOOD"}).status_code == 400

    # Success case
    assert client.post(f"/api/customers/{cust_id}/transactions", json={"amount": 100, "type": "DEBIT", "category": "FOOD"}).status_code == 201
