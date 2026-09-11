"""Synthetic seed data for BharatPay AI Phase 1.

Seeds three synthetic customers:
1. Rahul: Moderate earner with EMI obligations, increasing discretionary spending (+27%), and declining savings.
2. Priya: Financially healthy customer with stable income, stable spending, and no debt issues.
3. Arjun: Generally normal profile with an unusual high-value transaction (for future Guardian/fraud phase).

Safe to run repeatedly (idempotent).
"""

import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure project root and backend directory are in sys.path
_backend_dir = Path(__file__).resolve().parent.parent
_project_root = _backend_dir.parent
for _p in (str(_project_root), str(_backend_dir)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from backend.database.connection import get_db_connection, init_db
    from backend.repositories.customer_repository import insert_customer
    from backend.repositories.transaction_repository import insert_transaction
except ImportError:
    from database.connection import get_db_connection, init_db
    from repositories.customer_repository import insert_customer
    from repositories.transaction_repository import insert_transaction


CUSTOMERS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "name": "Rahul",
        "age": 28,
        "language": "en",
        "monthly_income": 45000.0,
        "monthly_emi": 14000.0,
        "created_at": "2026-07-01T00:00:00",
    },
    {
        "id": 2,
        "name": "Priya",
        "age": 31,
        "language": "en",
        "monthly_income": 65000.0,
        "monthly_emi": 0.0,
        "created_at": "2026-06-15T00:00:00",
    },
    {
        "id": 3,
        "name": "Arjun",
        "age": 26,
        "language": "en",
        "monthly_income": 50000.0,
        "monthly_emi": 8000.0,
        "created_at": "2026-07-10T00:00:00",
    },
]

# Rahul's transactions:
# Aug 2026 (Historical baseline):
#   Salary: 45,000 (CREDIT)
#   Fixed: EMI 14,000 + Bills 15,000 = 29,000
#   Discretionary: Food 3,200 + Shopping 2,187 + Transport 900 + Entertainment 800 = 7,087
#   Total Spending = 36,087
#   Savings = 8,913
# Sep 2026 (Recent evaluation):
#   Salary: 45,000 (CREDIT)
#   Fixed: EMI 14,000 + Bills 15,000 = 29,000
#   Discretionary: Food 4,000 + Shopping 3,000 + Transport 1,000 + Entertainment 1,000 = 9,000
#   Discretionary spending change: (9000 - 7087) / 7087 * 100 = +27.0%
#   Total Spending = 38,000
#   Savings = 7,000 (Declining from 8,913)
RAHUL_TRANSACTIONS: List[Dict[str, Any]] = [
    # August 2026 - Historical
    {"customer_id": 1, "timestamp": "2026-08-01T09:00:00", "amount": 45000.0, "type": "CREDIT", "category": "SALARY", "merchant": "Acme Tech Payroll", "status": "SUCCESS"},
    {"customer_id": 1, "timestamp": "2026-08-05T10:00:00", "amount": 14000.0, "type": "DEBIT", "category": "EMI", "merchant": "HDFC Auto Loan EMI", "status": "SUCCESS"},
    {"customer_id": 1, "timestamp": "2026-08-06T19:30:00", "amount": 3200.0, "type": "DEBIT", "category": "FOOD", "merchant": "FreshMart Groceries", "status": "SUCCESS"},
    {"customer_id": 1, "timestamp": "2026-08-08T11:00:00", "amount": 10000.0, "type": "DEBIT", "category": "BILLS", "merchant": "House Rent Transfer", "status": "SUCCESS"},
    {"customer_id": 1, "timestamp": "2026-08-10T14:15:00", "amount": 5000.0, "type": "DEBIT", "category": "BILLS", "merchant": "Electricity & Wifi", "status": "SUCCESS"},
    {"customer_id": 1, "timestamp": "2026-08-12T16:45:00", "amount": 2187.0, "type": "DEBIT", "category": "SHOPPING", "merchant": "Myntra Fashion", "status": "SUCCESS"},
    {"customer_id": 1, "timestamp": "2026-08-18T08:30:00", "amount": 900.0, "type": "DEBIT", "category": "TRANSPORT", "merchant": "Metro Recharge & Cab", "status": "SUCCESS"},
    {"customer_id": 1, "timestamp": "2026-08-25T20:00:00", "amount": 800.0, "type": "DEBIT", "category": "ENTERTAINMENT", "merchant": "PVR Cinemas", "status": "SUCCESS"},

    # September 2026 - Recent
    {"customer_id": 1, "timestamp": "2026-09-01T09:00:00", "amount": 45000.0, "type": "CREDIT", "category": "SALARY", "merchant": "Acme Tech Payroll", "status": "SUCCESS"},
    {"customer_id": 1, "timestamp": "2026-09-04T20:30:00", "amount": 4000.0, "type": "DEBIT", "category": "FOOD", "merchant": "Swiggy & Gourmet Dining", "status": "SUCCESS"},
    {"customer_id": 1, "timestamp": "2026-09-05T10:00:00", "amount": 14000.0, "type": "DEBIT", "category": "EMI", "merchant": "HDFC Auto Loan EMI", "status": "SUCCESS"},
    {"customer_id": 1, "timestamp": "2026-09-07T15:20:00", "amount": 3000.0, "type": "DEBIT", "category": "SHOPPING", "merchant": "Zara Apparel", "status": "SUCCESS"},
    {"customer_id": 1, "timestamp": "2026-09-08T11:00:00", "amount": 10000.0, "type": "DEBIT", "category": "BILLS", "merchant": "House Rent Transfer", "status": "SUCCESS"},
    {"customer_id": 1, "timestamp": "2026-09-10T14:15:00", "amount": 5000.0, "type": "DEBIT", "category": "BILLS", "merchant": "Electricity & Wifi", "status": "SUCCESS"},
    {"customer_id": 1, "timestamp": "2026-09-11T22:00:00", "amount": 1000.0, "type": "DEBIT", "category": "TRANSPORT", "merchant": "Uber Premier", "status": "SUCCESS"},
    {"customer_id": 1, "timestamp": "2026-09-14T21:00:00", "amount": 1000.0, "type": "DEBIT", "category": "ENTERTAINMENT", "merchant": "Social Pub & Lounge", "status": "SUCCESS"},
]

# Priya's transactions:
# Aug & Sep 2026:
# Stable income, stable spending, zero debt, increasing savings
PRIYA_TRANSACTIONS: List[Dict[str, Any]] = [
    # August 2026
    {"customer_id": 2, "timestamp": "2026-08-01T09:30:00", "amount": 65000.0, "type": "CREDIT", "category": "SALARY", "merchant": "Global Consulting Corp", "status": "SUCCESS"},
    {"customer_id": 2, "timestamp": "2026-08-05T11:00:00", "amount": 12000.0, "type": "DEBIT", "category": "BILLS", "merchant": "Apartment Maintenance & Utilities", "status": "SUCCESS"},
    {"customer_id": 2, "timestamp": "2026-08-10T18:00:00", "amount": 5500.0, "type": "DEBIT", "category": "FOOD", "merchant": "Nature's Basket Organic", "status": "SUCCESS"},
    {"customer_id": 2, "timestamp": "2026-08-15T09:00:00", "amount": 1500.0, "type": "DEBIT", "category": "TRANSPORT", "merchant": "Delhi Metro Rail Corp", "status": "SUCCESS"},
    {"customer_id": 2, "timestamp": "2026-08-20T17:00:00", "amount": 2000.0, "type": "DEBIT", "category": "SHOPPING", "merchant": "FabIndia", "status": "SUCCESS"},
    {"customer_id": 2, "timestamp": "2026-08-26T14:00:00", "amount": 5000.0, "type": "DEBIT", "category": "OTHER", "merchant": "Home Appliances Repair", "status": "SUCCESS"},

    # September 2026
    {"customer_id": 2, "timestamp": "2026-09-01T09:30:00", "amount": 65000.0, "type": "CREDIT", "category": "SALARY", "merchant": "Global Consulting Corp", "status": "SUCCESS"},
    {"customer_id": 2, "timestamp": "2026-09-05T11:00:00", "amount": 12000.0, "type": "DEBIT", "category": "BILLS", "merchant": "Apartment Maintenance & Utilities", "status": "SUCCESS"},
    {"customer_id": 2, "timestamp": "2026-09-10T18:00:00", "amount": 5500.0, "type": "DEBIT", "category": "FOOD", "merchant": "Nature's Basket Organic", "status": "SUCCESS"},
    {"customer_id": 2, "timestamp": "2026-09-15T09:00:00", "amount": 1500.0, "type": "DEBIT", "category": "TRANSPORT", "merchant": "Delhi Metro Rail Corp", "status": "SUCCESS"},
    {"customer_id": 2, "timestamp": "2026-09-20T17:00:00", "amount": 2000.0, "type": "DEBIT", "category": "SHOPPING", "merchant": "FabIndia", "status": "SUCCESS"},
]

# Arjun's transactions:
# Aug & Sep 2026:
# Normal pattern with one unusual high-value transaction (for future Guardian/fraud engine)
ARJUN_TRANSACTIONS: List[Dict[str, Any]] = [
    # August 2026
    {"customer_id": 3, "timestamp": "2026-08-01T10:00:00", "amount": 50000.0, "type": "CREDIT", "category": "SALARY", "merchant": "Creative Studio Payroll", "status": "SUCCESS"},
    {"customer_id": 3, "timestamp": "2026-08-04T10:00:00", "amount": 8000.0, "type": "DEBIT", "category": "EMI", "merchant": "Bajaj Finance Bike Loan", "status": "SUCCESS"},
    {"customer_id": 3, "timestamp": "2026-08-07T12:00:00", "amount": 7000.0, "type": "DEBIT", "category": "BILLS", "merchant": "PG Accommodation Rent", "status": "SUCCESS"},
    {"customer_id": 3, "timestamp": "2026-08-12T13:30:00", "amount": 4500.0, "type": "DEBIT", "category": "FOOD", "merchant": "Cafe Coffee Day & Meals", "status": "SUCCESS"},
    {"customer_id": 3, "timestamp": "2026-08-18T19:00:00", "amount": 1200.0, "type": "DEBIT", "category": "TRANSPORT", "merchant": "Indian Oil Fuel", "status": "SUCCESS"},

    # September 2026
    {"customer_id": 3, "timestamp": "2026-09-01T10:00:00", "amount": 50000.0, "type": "CREDIT", "category": "SALARY", "merchant": "Creative Studio Payroll", "status": "SUCCESS"},
    {"customer_id": 3, "timestamp": "2026-09-04T10:00:00", "amount": 8000.0, "type": "DEBIT", "category": "EMI", "merchant": "Bajaj Finance Bike Loan", "status": "SUCCESS"},
    {"customer_id": 3, "timestamp": "2026-09-07T12:00:00", "amount": 7000.0, "type": "DEBIT", "category": "BILLS", "merchant": "PG Accommodation Rent", "status": "SUCCESS"},
    {"customer_id": 3, "timestamp": "2026-09-12T13:30:00", "amount": 4600.0, "type": "DEBIT", "category": "FOOD", "merchant": "Cafe Coffee Day & Meals", "status": "SUCCESS"},
    {"customer_id": 3, "timestamp": "2026-09-18T19:00:00", "amount": 1100.0, "type": "DEBIT", "category": "TRANSPORT", "merchant": "Indian Oil Fuel", "status": "SUCCESS"},
    # Unusual high-value transaction for future fraud detection
    {"customer_id": 3, "timestamp": "2026-09-22T02:15:00", "amount": 85000.0, "type": "DEBIT", "category": "SHOPPING", "merchant": "Luxury Watch Boutique", "status": "SUCCESS"},
]


def seed_database(db_path: str = None) -> None:
    """Seed the database idempotently with Rahul, Priya, and Arjun.

    Safe to run repeatedly. Existing transactions and records for the target
    customers are cleanly replaced to avoid uncontrolled duplicates.
    """
    init_db(db_path)
    conn = get_db_connection(db_path)

    try:
        cursor = conn.cursor()
        all_txns = RAHUL_TRANSACTIONS + PRIYA_TRANSACTIONS + ARJUN_TRANSACTIONS

        # 1. Clean existing records for seed customers to ensure idempotency
        for cust in CUSTOMERS:
            cid = cust["id"]
            cursor.execute("DELETE FROM transactions WHERE customer_id = ?", (cid,))
            cursor.execute("DELETE FROM customers WHERE id = ?", (cid,))

        conn.commit()

        # 2. Insert customers
        for cust in CUSTOMERS:
            insert_customer(cust, conn=conn)

        # 3. Insert transactions
        for txn in all_txns:
            insert_transaction(txn, conn=conn)

        conn.commit()
        print(f"Successfully seeded {len(CUSTOMERS)} customers and {len(all_txns)} transactions.")
    finally:
        conn.close()


if __name__ == "__main__":
    db_arg = sys.argv[1] if len(sys.argv) > 1 else None
    seed_database(db_arg)
