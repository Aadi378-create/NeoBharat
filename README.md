# NeoBharat (BharatPay AI)
> *"Your bank that understands you, not just your transactions."*

[![Backend Tests](https://img.shields.io/badge/Backend%20Tests-368%20passed-3DDC9D?style=flat-square)](#testing)
[![Frontend Tests](https://img.shields.io/badge/Frontend%20Tests-16%20passed-3DDC9D?style=flat-square)](#testing)
[![Build Status](https://img.shields.io/badge/Vite%20Build-Passing-3DDC9D?style=flat-square)](#testing)
[![Hackathon](https://img.shields.io/badge/HackOut26-DAIICT-F79646?style=flat-square)](#overview)

---

## 1. What NeoBharat Is

**NeoBharat** is a prototype AI-assisted banking platform designed to protect customers rather than exploit their vulnerabilities. Traditional digital lending systems frequently optimize for loan disbursement volume, pushing high-interest credit lines to users under acute financial stress.

NeoBharat introduces a responsible alternative grounded in the principle: **"Backend decides. AI explains."**

> *"NeoBharat doesn't optimize for selling more products. It optimizes for making the right financial decision for the customer."*

By combining deterministic financial and risk engines with a strictly governed conversational explanation layer, NeoBharat identifies when a customer needs budgeting support, when they have a genuine surplus for systematic investing, or when an unusual transaction warrants proactive verification.

---

## 2. Problem Statement

1. **Predatory Lending Loops:** Algorithmic credit distribution often targets individuals during sudden cash flow crunches, leading to severe debt traps and default cycles.
2. **Opaque Scoring Systems:** Customers receive automated rejections or approvals without transparent, actionable explanations of the underlying metrics.
3. **Premature Fraud Panic:** Traditional rule engines either abruptly lock customer accounts or accuse users of fraud before verifying unusual transactions, inducing panic and operational friction.
4. **Unconstrained Generative AI Risks:** Generative LLMs placed directly in financial decision loops hallucinate terms, make unauthorized loan commitments, and violate regulatory safety standards.

---

## 3. Core Innovation: "Backend Decides. AI Explains."

NeoBharat decouples **deterministic financial decision-making** from **conversational explanation**:

```
+-------------------------------------------------------------+
|               SQLITE DETERMINISTIC FINANCIAL CORE           |
|  * Verified Transaction Analysis (Income, Spending, EMI)     |
|  * 4-Score Financial Guardian (Stress, Risk, Fraud, Change) |
|  * Deterministic Decision Engine (Debt Capacity, Guardrails)|
+------------------------------+------------------------------+
                               | Authoritative Context
                               v
+-------------------------------------------------------------+
|              LANGGRAPH CONVERSATION ORCHESTRATOR            |
|  * Multi-Turn State Machine (Intent, Language, Strategy)    |
|  * Context-Aware Appointment Routing & Booking Management   |
|  * Multi-Lingual Classification (English, Hindi, Hinglish)  |
+------------------------------+------------------------------+
                               | Filtered Payload
                               v
+-------------------------------------------------------------+
|              GROQ HIGH-SPEED EXPLANATION LAYER              |
|  * Model: openai/gpt-oss-120b (via Groq OpenAI-compat API)  |
|  * EXPLANATION_ONLY role (Zero authority to alter decisions)|
|  * Non-crashing graceful fallback when offline/unconfigured |
+------------------------------+------------------------------+
                               | Structured JSON
                               v
+-------------------------------------------------------------+
|               SAFETY VALIDATION GATE (PHASE 4)              |
|  * JSON Schema Draft 2020-12 Contract Verification          |
|  * Semantic Rules: Blocks credit pitches, prohibits claiming|
|    confirmed fraud, forbids unauthorized authority claims   |
+------------------------------+------------------------------+
                               | Verified Safe Output
                               v
+-------------------------------------------------------------+
|              FIRESTORE CLOUD APPLICATION STATE              |
|  * Multi-turn dialog history & appointment records          |
|  * Zero financial calculations (MockFirestore fallback)     |
+------------------------------+------------------------------+
                               | JSON over REST API
                               v
+-------------------------------------------------------------+
|                 MODERN REACT + VITE DASHBOARD               |
|  * Presentation-only UI with zero client calculations       |
|  * Persona Switcher (Rahul, Priya, Arjun)                   |
|  * Integrated SAKHI AI Assistant & Appointment Modal        |
+-------------------------------------------------------------+
```

- **SQLite = Financial Truth:** All risk scoring, affordability calculations, and recommendation decisions are computed by deterministic Python engines using verified transaction data.
- **Firestore = Application State:** Multi-turn conversational memory, appointment records, and session history are persisted in Firestore (with seamless local thread-safe `MockFirestoreClient` fallback when credentials are not configured).
- **LangGraph = Conversation Orchestration:** Directs dialog flow, classifies intents, manages appointment booking logic, and ensures customer context isolation.
- **Groq = Fast Explanation Layer:** Provides ultra-fast explanations using `openai/gpt-oss-120b` strictly in an `EXPLANATION_ONLY` capacity.
- **Safety Gate = Formal Enforcement:** Validates schema and semantic safety before any output is returned to the citizen.
- **Frontend = Presentation:** Modern React + Vite UI with full accessibility, bilingual support, and zero hardcoded credentials.

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

4. **(Optional) Configure Groq LLM Provider:**
   To enable live dynamic LLM explanations powered by Groq:
   ```powershell
   # Windows (PowerShell)
   $env:LLM_PROVIDER="groq"
   $env:GROQ_API_KEY="gsk_your_groq_api_key_here"
   $env:GROQ_MODEL="openai/gpt-oss-120b"

   # Linux / macOS
   export LLM_PROVIDER="groq"
   export GROQ_API_KEY="gsk_your_groq_api_key_here"
   export GROQ_MODEL="openai/gpt-oss-120b"
   ```
   > **Deterministic Fallback:** An external API key is **not required** to run or test the system. When unset, NeoBharat activates its verified deterministic fallback engine with zero crashes.

5. **Start Flask Backend Server:**
   ```bash
   .venv\Scripts\python.exe -m flask --app backend.app run --host 127.0.0.1 --port 5000
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
   *Frontend starts at `http://localhost:5173` (automatically proxying `/api/*` calls to the Flask backend on port 5000).*

4. **Build for Production:**
   ```bash
   npm run build
   ```
   *Generates optimized production bundle in `frontend/dist` in < 1 second.*

---

## 13. Testing & Verification

### Run All Backend Tests (Pytest)
```bash
.venv\Scripts\python.exe -m pytest -q
```
**Verified Result:** `368 passed in < 2 seconds` across 17 test suites covering deterministic metrics, guardian scoring, decision rules, Phase 4 schemas, LangGraph state machine, Groq provider resolution, and MockFirestore persistence.

### Run All Frontend Tests (Vitest)
```bash
cd frontend
npm test -- --run
```
**Verified Result:** `16 passed` covering customer persona transitions, guardian card calculations, and safety rules.

### Run Production Build Verification
```bash
cd frontend
npm run build
```
**Verified Result:** Built in < 1s with zero errors.

---

## 14. 10-Minute Live Demo Walkthrough

| Time | Stage | Action & Talking Points |
| :--- | :--- | :--- |
| **0:00–1:00** | **Problem Statement** | "Traditional banking apps ask: *What can we sell you?* NeoBharat asks: *What does this customer actually need right now?*" Introduce the decoupled architecture: **Backend decides. AI explains.** |
| **1:00–2:30** | **Rahul (Financial Stress)** | Select Rahul. Income ₹45k, spending ₹38k, EMI ₹14k, surplus ₹7k. Guardian triggers `ATTENTION_NEEDED` (Stress 72, Payment Risk 61). Decision is strictly **SUPPORT**; predatory credit is completely suppressed. |
| **2:30–4:00** | **SAKHI Conversational AI** | Open SAKHI. Ask *"Why didn't you recommend a loan?"* → SAKHI explains cashflow metrics. Ask in Hinglish: *"loan kyu nahi recommend kiya?"* → SAKHI responds naturally in Hinglish grounded in authoritative context. |
| **4:00–5:00** | **Appointment Booking** | Click *"Book Debt & Budgeting Advisor (30 mins)"* or ask SAKHI *"I want to talk to an advisor"*. Select date/time slot. Confirm booking. Persisted cleanly in application state without altering financial truth. |
| **5:00–6:30** | **Priya (Disciplined Wealth)** | Switch to Priya. Income ₹65k, spending ₹21k, zero debt, surplus ₹44k. Decision is **RECOMMEND** for Systematic Wealth Builder SIP. Zero aggressive appointment pushing. |
| **6:30–8:00** | **Arjun (Suspicious Anomaly)** | Switch to Arjun. Flagged ₹85,000 transaction at Luxury Watch Boutique (02:15 AM). Decision is **VERIFY**. Safety rule strictly enforced: *Never claim confirmed fraud until citizen verifies*. SAKHI guides security audit. |
| **8:00–9:00** | **Architecture Pitch** | **SQLite** = Financial Truth; **Firestore** = Application State; **LangGraph** = Orchestration; **Groq** = High-speed Explanation Layer. |
| **9:00–10:00** | **Responsible AI & Closing** | Emphasize safety gates, dark pattern prevention, and consumer welfare: *"NeoBharat doesn't optimize for selling more products. It optimizes for making the right financial decision for the customer."* |

---

## 15. Regulatory & Prototype Disclaimers

- **Illustrative Prototype Only:** NeoBharat is an academic and hackathon prototype built for **HackOut'26 at DAIICT**.
- **No Regulatory Endorsement:** Mentions of "RBI-aligned principles" refer to design heuristics inspired by public consumer protection guidelines; NeoBharat is not licensed or endorsed by the Reserve Bank of India.
- **No Real Financial Transactions:** Products such as the "Systematic Wealth Builder SIP" are illustrative prototype concepts and do not constitute investment advice or actual financial offerings.
