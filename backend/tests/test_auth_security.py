import pytest
import json
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
            client.environ_base["HTTP_X_REAL_AUTH"] = "1"
            yield client
    finally:
        try:
            os.unlink(db_path)
        except OSError:
            pass

def test_auth_valid_login(client):
    # Setup test customer
    client.post("/api/customers", json={
        "name": "Auth Test", "phone": "1112223333", "pin": "123456", 
        "monthly_income": 5000, "age": 25, "language": "en", "consent": True
    })
    
    res = client.post("/api/auth/login", json={"phone": "1112223333", "pin": "123456"})
    assert res.status_code == 200
    data = res.get_json()
    assert "pin_hash" not in data["customer"]
    assert "pin" not in data["customer"]

def test_auth_invalid_logins(client):
    client.post("/api/customers", json={
        "name": "Auth Test 2", "phone": "1112223333", "pin": "123456", 
        "monthly_income": 5000, "age": 25, "language": "en", "consent": True
    })

    # Wrong PIN
    assert client.post("/api/auth/login", json={"phone": "1112223333", "pin": "654321"}).status_code == 401
    
    # Wrong Phone
    assert client.post("/api/auth/login", json={"phone": "0000000000", "pin": "123456"}).status_code == 401
    
    # Missing PIN
    assert client.post("/api/auth/login", json={"phone": "1112223333"}).status_code == 400
    
    # 5-digit PIN
    assert client.post("/api/auth/login", json={"phone": "1112223333", "pin": "12345"}).status_code == 401
    
    # 7-digit PIN
    assert client.post("/api/auth/login", json={"phone": "1112223333", "pin": "1234567"}).status_code == 401
    
    # Alphabetic PIN
    assert client.post("/api/auth/login", json={"phone": "1112223333", "pin": "abcdef"}).status_code == 401

def test_idor_blocked(client):
    # Create two customers
    res1 = client.post("/api/customers", json={
        "name": "User 1", "phone": "1111111111", "pin": "111111", 
        "monthly_income": 1000, "age": 20, "language": "en", "consent": True
    })
    id1 = res1.get_json()["id"]

    res2 = client.post("/api/customers", json={
        "name": "User 2", "phone": "2222222222", "pin": "222222", 
        "monthly_income": 2000, "age": 20, "language": "en", "consent": True
    })
    id2 = res2.get_json()["id"]

    # Login as User 1
    client.post("/api/auth/login", json={"phone": "1111111111", "pin": "111111"})

    # Try to access User 2's profile
    res = client.get(f"/api/customers/{id2}/profile")
    assert res.status_code == 403
    
    # Try to access User 2's transactions
    res = client.get(f"/api/customers/{id2}/transactions")
    assert res.status_code == 403

def test_cross_customer_transaction_blocked(client):
    # Create two customers
    res1 = client.post("/api/customers", json={"name": "User 1", "phone": "1111111111", "pin": "111111", "monthly_income": 1000, "age": 20, "language": "en", "consent": True})
    id1 = res1.get_json()["id"]
    res2 = client.post("/api/customers", json={"name": "User 2", "phone": "2222222222", "pin": "222222", "monthly_income": 2000, "age": 20, "language": "en", "consent": True})
    id2 = res2.get_json()["id"]

    # Login as User 1
    client.post("/api/auth/login", json={"phone": "1111111111", "pin": "111111"})

    # Attack: User 1 creates a transaction for User 2
    res = client.post(f"/api/customers/{id2}/transactions", json={"amount": 100, "type": "DEBIT", "category": "FOOD"})
    assert res.status_code == 403

def test_sakhi_isolation(client):
    res1 = client.post("/api/customers", json={"name": "User 1", "phone": "1111111111", "pin": "111111", "monthly_income": 1000, "age": 20, "language": "en", "consent": True})
    id1 = res1.get_json()["id"]
    res2 = client.post("/api/customers", json={"name": "User 2", "phone": "2222222222", "pin": "222222", "monthly_income": 2000, "age": 20, "language": "en", "consent": True})
    id2 = res2.get_json()["id"]

    client.post("/api/auth/login", json={"phone": "1111111111", "pin": "111111"})

    # Try to chat on behalf of User 2
    res = client.post("/api/chat", json={"customer_id": id2, "message": "What is my balance?"})
    assert res.status_code == 403

def test_auth_session(client):
    res1 = client.post("/api/customers", json={"name": "User 1", "phone": "1111111111", "pin": "111111", "monthly_income": 1000, "age": 20, "language": "en", "consent": True})
    id1 = res1.get_json()["id"]

    # Access without login -> 401
    assert client.get(f"/api/customers/{id1}").status_code == 401

    # Login -> 200
    client.post("/api/auth/login", json={"phone": "1111111111", "pin": "111111"})
    assert client.get(f"/api/customers/{id1}").status_code == 200

    # Logout
    client.post("/api/auth/logout")

    # Access without login -> 401
    assert client.get(f"/api/customers/{id1}").status_code == 401
