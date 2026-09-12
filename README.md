# NeoBharat (BharatPay AI)
> *"Your bank that understands you, not just your transactions."*

[![Backend Tests](https://img.shields.io/badge/Backend%20Tests-317%20passed-3DDC9D?style=flat-square)](#testing)
[![Frontend Tests](https://img.shields.io/badge/Frontend%20Tests-12%20passed-3DDC9D?style=flat-square)](#testing)
[![Build Status](https://img.shields.io/badge/Vite%20Build-Passing-3DDC9D?style=flat-square)](#testing)
[![Hackathon](https://img.shields.io/badge/HackOut26-DAIICT-F79646?style=flat-square)](#overview)

---

## 1. What NeoBharat Is

**NeoBharat** is a prototype AI-assisted banking platform designed to protect customers rather than exploit their vulnerabilities. Traditional digital lending systems frequently optimize for loan disbursement volume, pushing high-interest credit lines to users under acute financial stress.

NeoBharat introduces a responsible alternative grounded in the principle: **"AI can choose NOT to sell."**

By combining deterministic financial and risk engines with a strictly governed conversational explanation layer, NeoBharat identifies when a customer needs budgeting support, when they have a genuine surplus for systematic investing, or when an unusual transaction warrants proactive verification.

---

## 2. Problem Statement

1. **Predatory Lending Loops:** Algorithmic credit distribution often targets individuals during sudden cash flow crunches, leading to severe debt traps and default cycles.
2. **Opaque Scoring Systems:** Customers receive automated rejections or approvals without transparent, actionable explanations of the underlying metrics.
3. **Premature Fraud Panic:** Traditional rule engines either abruptly lock customer accounts or accuse users of fraud before verifying unusual transactions, inducing panic and operational friction.
4. **Unconstrained Generative AI Risks:** Generative LLMs placed directly in financial decision loops hallucinate terms, make unauthorized loan commitments, and violate regulatory safety standards.

---

## 3. Core Innovation: "AI Can Choose NOT to Sell"

NeoBharat decouples **decision-making** from **conversational explanation**:

```
+--------------------------------------------------------+
|                   DETERMINISTIC LAYER                  |
|  * Transaction Analysis (Income, Spending, EMI)        |
|  * Financial Guardian (Stress, Risk, Fraud Scores)     |
|  * Recommendation Engine (Debt Capacity, Safety Gates) |
+---------------------------+----------------------------+
                            | Strict JSON Context
                            v
+--------------------------------------------------------+
|              SAFETY VALIDATION GATE (PHASE 4)          |
|  * JSON Schema Enforcement                             |
|  * Semantic Safety Rules (No hallucinated approvals,   |
|    no credit pitches when blocked, no confirmed fraud) |
+---------------------------+----------------------------+
                            | Validated Context
                            v
+--------------------------------------------------------+
|                 OPENAI EXPLANATION LAYER               |
|  * Clear, empathetic explanations                      |
|  * Non-crashing graceful fallback if API unavailable   |
+---------------------------+----------------------------+
                            | Validated JSON
                            v
+--------------------------------------------------------+
|                FRONTEND DASHBOARD (PHASE 6)            |
|  * Presentation-only display (Zero client calculations)|
|  * Clear visual distinction of SUPPORT vs RECOMMEND    |
+--------------------------------------------------------+
```

- **Deterministic Financial Engine Decides:** All risk scoring, affordability calculations, and recommendation decisions are computed by deterministic Python engines using verified transaction data.
- **Safety Gate Validates:** A formal validator ensures zero hallucination, strict schema conformance, and alignment with protective principles before any explanation reaches the user.
- **OpenAI Explains:** Large Language Models are restricted to an `EXPLANATION_ONLY` role. They have no authority to approve loans, alter scores, or pitch commercial credit.
- **Frontend Displays:** A React + Vite interface renders backend outputs with zero client-side financial calculations and zero exposed credentials.

---

## 4. Architectural Layers

The NeoBharat codebase is structured across distinct verified phases:

| Phase | Component | Responsibilities | Verified Tests |
| :--- | :--- | :--- | :--- |
| **Phase 1** | **Data & Foundation** | SQLite schema, idempotent seed data, transaction repositories, health check. | Baseline |
| **Phase 2** | **Metrics & Guardian** | Deterministic cash flow metrics, spending trend detection, 4-score Financial Guardian. | 54 tests |
| **Phase 3** | **Decision Engine** | Affordability calculations, safe incremental debt capacity, predatory lending blocks. | 38 tests |
| **Phase 4** | **Safety Validator** | Schema contracts, adversarial input rejection, semantic rule validation, deterministic fallback. | 86 tests |
| **Phase 5** | **Explanation Layer** | OpenAI chat completion client, prompt templates, 4000-char input validation, error recovery. | 35 tests |
| **Phase 6A** | **API Exposure** | Controlled REST endpoints (`/api/customers`, `/profile`, `/guardian`, `/recommendation`, `/chat`). | 17 tests |
| **Phase 6B** | **Dashboard UI** | React + Vite dashboard, HackOut'26 visual identity, hero Decision Card, responsive grid. | 12 tests |
| **Phase 7** | **Conversational Intelligence** | Intent classification, vernacular support (English, Hindi, Hinglish), context tracking, localized fallbacks. | 87 tests |

---

## 5. Deterministic Engine vs. LLM Separation

To guarantee mathematical accuracy and regulatory safety, NeoBharat maintains a strict separation of concerns:

- **What the Deterministic Engines Do:**
  - Calculate `income`, `monthly_spending`, `emi`, `emi_ratio`, and `net_monthly_surplus`.
  - Calculate `financial_stress_score`, `payment_risk_score`, `fraud_score`, and `behaviour_change_score` (0-100 scale).
  - Determine categorical decisions: `SUPPORT`, `RECOMMEND`, or `VERIFY`.
  - Lock predatory credit products whenever financial stress exceeds threshold (>= 60) or net surplus is negative.
- **What the LLM Does:**
  - Converts pre-computed context into clear, empathetic natural language.
  - Highlights specific evidence metrics already determined by the engine.
  - Suggests actionable next steps aligned with the engine's guidance.
- **What the LLM is Strictly Forbidden to Do:**
  - Make or modify loan decisions.
  - Alter risk scores or affordability numbers.
  - Invent APRs, interest rates, returns, or product terms.
  - Pitch credit when predatory lending is blocked.
  - Accuse the user of "confirmed fraud" or "theft".

---

## 6. Financial Guardian

The **Financial Guardian** operates as a proactive protective intelligence layer evaluating customer financial health:

- **Financial Stress Score (0-100):** Evaluates debt burden, discretionary expenditure shocks, and declining savings.
- **Payment Risk Score (0-100):** Measures upcoming EMI obligations relative to available liquidity.
- **Fraud / Anomaly Score (0-100):** Flags unusual transaction amounts deviating from personal historical baselines.
- **Behaviour Shift Score (0-100):** Identifies significant changes in spending or savings patterns over time.

---

## 7. Decision Engine & Affordability Rules

The Decision Engine enforces deterministic prototype safety heuristics:

1. **Affordability Ceiling:** Current EMI obligations cannot exceed 35% of monthly income.
2. **Safe Incremental Debt Capacity:** Calculated strictly from verified monthly surplus:
   $$\text{Incremental Debt Capacity} = \max(0, (\text{Income} \times 0.35) - \text{Current EMI})$$
   If net surplus is negative, incremental debt capacity is clamped to ₹0.
3. **Predatory Lending Safeguard:** When financial stress or payment risk reaches or exceeds 60, commercial credit offerings are locked, and the customer is routed to `SUPPORT`.

---

## 8. Fraud & Anomaly Handling: "Verify, Don't Accuse"

When unusual account activity occurs (e.g., an abrupt high-value transfer):
- The system issues a `VERIFY` decision.
- All commercial product recommendations are suspended.
- The user is prompted with supportive guidance to confirm or dispute the transaction.
- **Safety Rule:** Explanations and UI copy never assert "confirmed fraud" or "account hacked"; they describe the activity as "unusual compared with your normal history" pending customer verification.

---

## 9. Customer Personas (Synthetic Demonstration Data)

NeoBharat includes three synthetic personas demonstrating each core customer journey:

### Persona 1: Rahul (ID 1) - Support Over Selling
- **Profile:** Age 28, Gig Economy Worker
- **Income:** ₹45,000 / month | **Monthly Spending:** ₹38,000 (+27% discretionary spike)
- **Monthly EMI:** ₹14,000 (31.1% burden) | **Estimated Savings:** ₹7,000 (Declining trend)
- **Guardian Scores:** Stress: **72** | Payment Risk: **61** | Behaviour Shift: **72** | Fraud: **7**
- **Decision:** `SUPPORT` (Commercial credit locked; predatory lending blocked)
- **Journey:** Demonstrates **"AI That Chooses NOT to Sell"** - offers cash-flow review instead of pushing high-interest personal loans.

### Persona 2: Priya (ID 2) - Personalized Wealth Building
- **Profile:** Age 31, Salaried Professional
- **Income:** ₹65,000 / month | **Monthly Spending:** ₹21,000 (Disciplined budget)
- **Monthly EMI:** ₹0 (0.0% burden) | **Estimated Savings:** ₹44,000 (Healthy surplus)
- **Guardian Scores:** Stress: **0** | Payment Risk: **0** | Behaviour Shift: **18** | Fraud: **4**
- **Decision:** `RECOMMEND`
- **Product Offered:** `Illustrative Prototype Product: Systematic Wealth Builder SIP`
- **Journey:** Recognizes sustainable monthly savings surplus and presents low-risk systematic investment options with risk disclosures.

### Persona 3: Arjun (ID 3) - Proactive Safety Barrier
- **Profile:** Age 26, Small Business Owner
- **Income:** ₹50,000 / month | **Monthly Spending:** ₹105,700 (Unusual spike)
- **Monthly EMI:** ₹8,000 | **Estimated Savings:** -₹55,700 (Net deficit)
- **Guardian Scores:** Stress: **65** | Payment Risk: **50** | Behaviour Shift: **100** | Fraud: **95**
- **Decision:** `VERIFY` (Commercial products suspended)
- **Journey:** Detects an uncharacteristic ₹85,000 transaction. Suspends promotions and prompts Arjun to verify the transaction without panic.

---

## 10. Privacy & Safety Principles

- **RBI-Aligned Customer Protection:** Incorporates safe debt-to-income caps, explicit risk disclosures, and fair lending principles.
- **Data Minimization:** Chat API requests send strictly `customer_id` and `message`. No raw customer transaction tables or personal identifiers are passed to external models.
- **No Client-Side Secrets:** Zero OpenAI API keys or credentials exist in the client-side bundle. All external LLM communication occurs securely server-side.
- **Input Bounds Enforcement:** User chat prompts are constrained to 4,000 characters, validated independently on both frontend and backend before model processing.
- **Synthetic Data Disclaimer:** All customer names, account numbers, and transaction logs are purely synthetic prototype data created for evaluation.

---

## 11. Project Structure

```text
NeoBharat/
|-- backend/
|   |-- app.py                      # Flask app factory, route registration, health check
|   |-- config.py                   # Configuration and database path
|   |-- data/
|   |   `-- seed_data.py            # Idempotent synthetic dataset (Rahul, Priya, Arjun)
|   |-- database/
|   |   |-- connection.py           # SQLite connection manager
|   |   `-- schema.sql              # Database schema (customers, transactions)
|   |-- domain/
|   |   |-- financial_metrics.py    # Deterministic cash flow metrics
|   |   |-- behaviour.py            # Behavioral shifts and spending trends
|   |   |-- guardian.py             # 4-score Guardian intelligence engine
|   |   |-- decision_engine.py      # Affordability and recommendation safety gates
|   |   `-- phase4_validator.py     # Schema and semantic safety validation gate
|   |-- integrations/
|   |   `-- openai_client.py        # Secure OpenAI client with fallback handling
|   |-- repositories/
|   |   |-- customer_repository.py  # Customer database access
|   |   `-- transaction_repository.py # Transaction database access
|   |-- routes/
|   |   |-- chat_routes.py          # POST /api/chat endpoint with length validation
|   |   `-- dashboard_routes.py     # GET /api/customers/* endpoints (Phase 6A)
|   |-- schemas/                    # JSON Schema specifications for LLM I/O
|   |-- services/
|   |   `-- chat_service.py         # End-to-end safe explanation coordinator
|   `-- tests/                      # 230 comprehensive pytest suites
|-- frontend/
|   |-- index.html                  # Dashboard entry HTML
|   |-- package.json                # Frontend dependencies (React 18, Vite, Vitest)
|   |-- vite.config.js              # Vite configuration with /api reverse proxy
|   `-- src/
|       |-- main.jsx                # React root mount
|       |-- App.jsx                 # Main layout and stale-fetch protection
|       |-- index.css               # Design system tokens (HackOut 26 palette)
|       |-- api/
|       |   `-- client.js           # Frontend API client and contract validation
|       |-- components/
|       |   |-- Header.jsx          # Brand header and persona switcher
|       |   |-- DecisionCard.jsx    # Hero decision banner ("AI That Chooses NOT to Sell")
|       |   |-- FinancialOverview.jsx # Deterministic financial overview cards
|       |   |-- GuardianSection.jsx # 4 Guardian scorecards and risk factors
|       |   |-- ChatPanel.jsx       # Conversational explanation terminal
|       |   `-- Icons.jsx           # Clean SVG iconography
|       `-- test/
|           `-- dashboard.test.js   # 12 Vitest unit and contract tests
`-- requirements.txt                # Python backend dependencies
```

---

## 12. Getting Started & Setup Instructions

### Prerequisites
- **Python:** 3.10+ (tested on Python 3.14)
- **Node.js:** 18+ (tested on Node.js v24.13.0 with npm 11.6.2)
- **Git:** Version control

---

### Backend Setup

1. **Activate Virtual Environment:**
   ```powershell
   # Windows (PowerShell)
   .\.venv\Scripts\Activate.ps1

   # Linux / macOS
   source .venv/bin/activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize & Seed Database:**
   ```bash
   python -m backend.data.seed_data
   ```
   *Output: `Successfully seeded 3 customers and 44 transactions.`*

4. **(Optional) Configure OpenAI API Key:**
   To enable dynamic LLM explanations, set your API key in the environment:
   ```powershell
   # Windows (PowerShell)
   $env:OPENAI_API_KEY="your-openai-api-key"

   # Linux / macOS
   export OPENAI_API_KEY="your-openai-api-key"
   ```
   > **Note:** An API key is **not required** to run or test the system. When unset, NeoBharat gracefully activates its verified deterministic fallback engine with zero crashes.

5. **Start Flask Backend Server:**
   ```bash
   python backend/app.py
   ```
   *Backend starts at `http://127.0.0.1:5000` with health check at `/health`.*

---

### Frontend Setup

1. **Navigate to Frontend Directory:**
   ```bash
   cd frontend
   ```

2. **Install Node Dependencies:**
   ```bash
   npm install
   ```

3. **Start Development Server:**
   ```bash
   npm run dev
   ```
   *Frontend starts at `http://localhost:3000` (automatically proxying `/api` calls to the Flask backend).*

4. **Build for Production:**
   ```bash
   npm run build
   ```
   *Generates optimized production bundle in `frontend/dist`.*

---

## 13. Testing

### Run All Backend Tests (Pytest)
```bash
.venv\Scripts\python.exe -m pytest -q
```
**Expected Result:** `230 passed` across all 14 test suites in < 1 second.

### Run All Frontend Tests (Vitest)
```bash
cd frontend
npm run test
```
**Expected Result:** `12 passed` across all client contract and persona tests in < 1.5 seconds.

### Run Production Build Verification
```bash
cd frontend
npm run build
```
**Expected Result:** `build in ~900ms` with zero bundle errors or warnings.

---

## 14. Regulatory & Prototype Disclaimers

- **Illustrative Prototype Only:** NeoBharat is an academic and hackathon prototype submitted for **HackOut'26 at DAIICT**.
- **No Regulatory Endorsement:** Mentions of "RBI-aligned principles" refer to design heuristics inspired by public consumer protection guidelines; NeoBharat is not licensed or endorsed by the Reserve Bank of India.
- **No Real Financial Transactions:** Products such as the "Systematic Wealth Builder SIP" are illustrative prototype concepts and do not constitute investment advice or actual financial offerings.
