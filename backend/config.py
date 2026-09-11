"""Configuration module for BharatPay AI backend."""

import os
from pathlib import Path

# Base directory for backend
BACKEND_DIR = Path(__file__).resolve().parent

# Database configuration
DATABASE_PATH = os.environ.get("DATABASE_PATH", str(BACKEND_DIR / "bharatpay.db"))
