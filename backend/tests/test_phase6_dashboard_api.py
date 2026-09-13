"""Phase 6A Route and Integration Tests for NeoBharat Dashboard API.

Verifies:
1. GET /api/customers returns seeded customer records.
2. GET /api/customers/<id> returns individual customer records and 404 for unknown.
3. GET /api/customers/<id>/profile returns pre-calculated financial metrics and 404 for unknown.
4. GET /api/customers/<id>/guardian returns pre-evaluated Guardian state and 404 for unknown.
5. GET /api/customers/<id>/recommendation returns pre-evaluated Phase 3 decisions and 404 for unknown.
6. Semantic verification of Rahul (SUPPORT), Priya (RECOMMEND), and Arjun (VERIFY).
"""

import pytest
from backend.app import create_app
from backend.data.seed_data import seed_database


@pytest.fixture
def test_client():
    """Create a test client using the application factory with seeded data."""
    import tempfile, os
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    try:
        app = create_app({"TESTING": True, "DATABASE_PATH": db_path})
        seed_database(db_path)
        with app.test_client() as client:
            yield client
    finally:
        try:
            os.unlink(db_path)
        except OSError:
            pass


# =========================================================================
# 1. Customer Selector Endpoint (GET /api/customers)
# =========================================================================

def test_get_customers_list(test_client):
    """GET /api/customers returns HTTP 200 and includes seeded customers Rahul, Priya, Arjun."""
    resp = test_client.get("/api/customers")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) >= 3

    customer_map = {c["id"]: c for c in data}
    assert 1 in customer_map
    assert customer_map[1]["name"] == "Rahul"
    assert 2 in customer_map
    assert customer_map[2]["name"] == "Priya"
    assert 3 in customer_map
    assert customer_map[3]["name"] == "Arjun"


# =========================================================================
# 2. Individual Customer Endpoint (GET /api/customers/<id>)
# =========================================================================

def test_get_customer_by_id_rahul(test_client):
    """GET /api/customers/1 returns HTTP 200 and matches Rahul's seeded record."""
    resp = test_client.get("/api/customers/1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == 1
    assert data["name"] == "Rahul"
    assert data["age"] == 28
    assert data["monthly_income"] == 45000.0
    assert data["monthly_emi"] == 14000.0


def test_get_customer_by_id_priya(test_client):
    """GET /api/customers/2 returns HTTP 200 and matches Priya's seeded record."""
    resp = test_client.get("/api/customers/2")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == 2
    assert data["name"] == "Priya"
    assert data["age"] == 31
    assert data["monthly_income"] == 65000.0
    assert data["monthly_emi"] == 0.0


def test_get_customer_by_id_arjun(test_client):
    """GET /api/customers/3 returns HTTP 200 and matches Arjun's seeded record."""
    resp = test_client.get("/api/customers/3")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == 3
    assert data["name"] == "Arjun"
    assert data["age"] == 26
    assert data["monthly_income"] == 50000.0
    assert data["monthly_emi"] == 8000.0


def test_get_customer_by_id_not_found(test_client):
    """GET /api/customers/99999 returns HTTP 404 for unknown customer."""
    resp = test_client.get("/api/customers/99999")
    assert resp.status_code == 404
    data = resp.get_json()
    assert "not found" in data.get("error", "").lower()


# =========================================================================
# 3. Financial Profile Endpoint (GET /api/customers/<id>/profile)
# =========================================================================

def test_get_customer_profile_rahul(test_client):
    """GET /api/customers/1/profile returns Rahul's deterministic metrics without re-computation."""
    resp = test_client.get("/api/customers/1/profile")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["income"] == 45000.0
    assert data["monthly_spending"] == 38000.0
    assert data["fixed_expenses"] == 29000.0
    assert data["discretionary_spending"] == 9000.0
    assert data["emi"] == 14000.0
    assert data["emi_ratio"] == 31.1
    assert data["estimated_savings"] == 7000.0
    assert data["spending_trend"] == "INCREASING"
    assert data["spending_change_pct"] == 27.0
    assert data["savings_trend"] == "DECLINING"


def test_get_customer_profile_priya(test_client):
    """GET /api/customers/2/profile returns Priya's deterministic metrics without re-computation."""
    resp = test_client.get("/api/customers/2/profile")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["income"] == 65000.0
    assert data["monthly_spending"] == 21000.0
    assert data["fixed_expenses"] == 12000.0
    assert data["discretionary_spending"] == 9000.0
    assert data["emi"] == 0.0
    assert data["emi_ratio"] == 0.0
    assert data["estimated_savings"] == 44000.0
    assert data["spending_trend"] == "STABLE"
    assert data["spending_change_pct"] == 0.0
    assert data["savings_trend"] == "INCREASING"


def test_get_customer_profile_arjun(test_client):
    """GET /api/customers/3/profile returns Arjun's deterministic metrics without re-computation."""
    resp = test_client.get("/api/customers/3/profile")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["income"] == 50000.0
    assert data["monthly_spending"] == 105700.0
    assert data["fixed_expenses"] == 15000.0
    assert data["discretionary_spending"] == 90700.0
    assert data["emi"] == 8000.0
    assert data["emi_ratio"] == 16.0
    assert data["estimated_savings"] == -55700.0
    assert data["spending_trend"] == "INCREASING"
    assert data["spending_change_pct"] == 1491.2
    assert data["savings_trend"] == "DECLINING"


def test_get_customer_profile_not_found(test_client):
    """GET /api/customers/99999/profile returns HTTP 404 for unknown customer."""
    resp = test_client.get("/api/customers/99999/profile")
    assert resp.status_code == 404
    data = resp.get_json()
    assert "not found" in data.get("error", "").lower()


# =========================================================================
# 4. Guardian Assessment Endpoint (GET /api/customers/<id>/guardian)
# =========================================================================

def test_get_customer_guardian_rahul_semantic(test_client):
    """GET /api/customers/1/guardian semantically verifies Rahul's financial stress assessment."""
    resp = test_client.get("/api/customers/1/guardian")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["customer_id"] == 1
    assert data["status"] == "ATTENTION_NEEDED"
    assert data["classification"]["primary"] == "FINANCIAL_STRESS"
    assert data["scores"]["financial_stress_score"] == 72
    assert data["scores"]["payment_risk_score"] == 61
    assert data["scores"]["fraud_score"] == 7
    assert data["scores"]["behaviour_change_score"] == 72


def test_get_customer_guardian_priya_semantic(test_client):
    """GET /api/customers/2/guardian semantically verifies Priya's healthy financial standing."""
    resp = test_client.get("/api/customers/2/guardian")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["customer_id"] == 2
    assert data["status"] == "NO_ACTION"
    assert data["classification"]["primary"] == "HEALTHY_FINANCIAL_TREND"
    assert data["scores"]["financial_stress_score"] == 0
    assert data["scores"]["payment_risk_score"] == 0
    assert data["scores"]["fraud_score"] == 4
    assert data["scores"]["behaviour_change_score"] == 18


def test_get_customer_guardian_arjun_semantic(test_client):
    """GET /api/customers/3/guardian semantically verifies Arjun's fraud suspicion without confirmed fraud."""
    resp = test_client.get("/api/customers/3/guardian")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["customer_id"] == 3
    assert data["status"] == "URGENT_ACTION"
    assert data["classification"]["primary"] == "FRAUD_SUSPECTED"
    assert data["scores"]["fraud_score"] == 95
    assert data["scores"]["financial_stress_score"] == 65
    assert data["recommended_intervention"]["action"] == "VERIFY_SUSPICIOUS_TRANSACTION"

    # Confirmed fraud language must never appear
    summary = data["explanation"]["summary"].lower()
    assert "confirmed fraud" not in summary
    assert "definitely fraudulent" not in summary
    assert "hacked" not in summary


def test_get_customer_guardian_not_found(test_client):
    """GET /api/customers/99999/guardian returns HTTP 404 for unknown customer."""
    resp = test_client.get("/api/customers/99999/guardian")
    assert resp.status_code == 404
    data = resp.get_json()
    assert "not found" in data.get("error", "").lower()


# =========================================================================
# 5. Recommendation Endpoint (GET /api/customers/<id>/recommendation)
# =========================================================================

def test_get_customer_recommendation_rahul_semantic(test_client):
    """GET /api/customers/1/recommendation semantically verifies Rahul's SUPPORT outcome."""
    resp = test_client.get("/api/customers/1/recommendation")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["customer_id"] == 1
    assert data["decision"] == "SUPPORT"
    assert data["recommendation"]["action"] == "SUPPORT"
    assert data["recommendation"]["product_category"] is None
    assert data["recommendation"]["product_name"] is None
    assert data["recommendation"]["supportive_guidance"]["action"] == "REVIEW_UPCOMING_PAYMENTS"
    assert data["consumer_protection_metadata"]["predatory_lending_blocked"] is True


def test_get_customer_recommendation_priya_semantic(test_client):
    """GET /api/customers/2/recommendation semantically verifies Priya's RECOMMEND outcome."""
    resp = test_client.get("/api/customers/2/recommendation")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["customer_id"] == 2
    assert data["decision"] == "RECOMMEND"
    assert data["recommendation"]["action"] == "RECOMMEND"
    assert data["recommendation"]["product_category"] == "investment/SIP"
    assert "Systematic Wealth Builder SIP" in data["recommendation"]["product_name"]
    assert data["consumer_protection_metadata"]["predatory_lending_blocked"] is False


def test_get_customer_recommendation_arjun_semantic(test_client):
    """GET /api/customers/3/recommendation semantically verifies Arjun's VERIFY outcome."""
    resp = test_client.get("/api/customers/3/recommendation")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["customer_id"] == 3
    assert data["decision"] == "VERIFY"
    assert data["recommendation"]["action"] == "VERIFY"
    assert data["recommendation"]["product_category"] is None
    assert data["recommendation"]["product_name"] is None
    assert data["recommendation"]["supportive_guidance"]["action"] == "VERIFY_SUSPICIOUS_TRANSACTION"
    assert data["consumer_protection_metadata"]["predatory_lending_blocked"] is True


def test_get_customer_recommendation_not_found(test_client):
    """GET /api/customers/99999/recommendation returns HTTP 404 for unknown customer."""
    resp = test_client.get("/api/customers/99999/recommendation")
    assert resp.status_code == 404
    data = resp.get_json()
    assert "not found" in data.get("error", "").lower()
