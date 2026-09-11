-- SQLite Schema for BharatPay AI

CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    language TEXT DEFAULT 'en',
    monthly_income REAL,
    monthly_emi REAL,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    amount REAL NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('CREDIT', 'DEBIT')),
    category TEXT NOT NULL CHECK(category IN ('SALARY', 'FOOD', 'SHOPPING', 'TRANSPORT', 'BILLS', 'EMI', 'ENTERTAINMENT', 'INVESTMENT', 'HEALTH', 'OTHER')),
    merchant TEXT,
    status TEXT DEFAULT 'SUCCESS' CHECK(status IN ('SUCCESS', 'FAILED', 'PENDING')),
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_transactions_customer_id ON transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_customer_timestamp ON transactions(customer_id, timestamp);
