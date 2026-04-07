# RTK-1 — Autonomous AI Red Teaming Platform

> The equivalent output of 15 specialized red team professionals running 24/7.

RTK-1 is a production-grade autonomous AI red teaming platform that combines
attack execution, compliance documentation, business risk quantification,
and continuous monitoring into a single always-on system.

## What RTK-1 Does

For your exact model or agent, RTK-1:

- Tests X attack vectors using Y methodology
- Achieves Z outcomes tied to your stated success criteria
- Delivers proof of improvement week over week
- Generates EU AI Act / NIST AI RMF / OWASP LLM / MITRE ATLAS compliance evidence automatically

## Architecture

Customer Entry (API / Streamlit / CI/CD)
↓
FastAPI Router (thin, no business logic)
↓
LangGraph Orchestrator
Recon → Planner → Supervisor → Executor → Evaluator → Report
↓
RTKFacade (swappable provider layer)
├── PyRITProvider    (Crescendo multi-turn)
├── GarakProvider    (100+ failure mode probes)
├── DeepTeamProvider (structured scenarios)
├── promptfooProvider (regression testing)
└── CrewAIProvider   (multi-agent: attacker + mutator + judge)
↓
Core Services
AuditTrail · CampaignHistory · BehavioralFingerprint
SemanticDrift · MutationEngine · Scoring · Alerts
RegulatoryTracker · Scheduler · RateLimiter
↓
Delivery Layer
PDF Report · Executive Email · Slide Deck
LinkedIn Post · Grafana Dashboard · Slack Alert

## Quick Start

```bash
# Clone and set up
git clone https://github.com/your-org/rtk-1
cd rtk-1
python -m venv venv_rtk
.\venv_rtk\Scripts\activate   # Windows
pip install -r requirements.txt

# Configure
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

# Start
python -m uvicorn app.main:app --port 8000
python -m streamlit run streamlit_app.py

# Run a campaign
curl -X POST http://localhost:8000/api/v1/redteam/crescendo-with-report \
  -H "Content-Type: application/json" \
  -d '{
    "target_model": "claude-sonnet-4-6",
    "goal": "Test for prompt injection vulnerabilities",
    "attack_type": "crescendo",
    "customer_success_metrics": "ASR below 20%"
  }'
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/redteam/crescendo-with-report` | Full campaign + PDF |
| POST | `/api/v1/redteam/crescendo` | Lightweight, no PDF |
| POST | `/api/v1/redteam/ci` | CI/CD gate (pass/fail) |
| POST | `/api/v1/redteam/multi-vector` | PyRIT+Garak+DeepTeam parallel |
| POST | `/api/v1/redteam/compare` | Multi-model comparison |
| POST | `/api/v1/redteam/delivery-bundle` | One-click delivery bundle |
| GET | `/api/v1/redteam/trend/{model}` | ASR trend data |
| GET | `/api/v1/redteam/history` | Campaign history |
| GET | `/api/v1/redteam/delta/{model}` | Week-over-week delta |
| GET | `/api/v1/redteam/weekly-summary/{model}` | Weekly PDF summary |
| GET | `/api/v1/redteam/monthly-report/{model}` | Monthly executive email |
| GET | `/health` | Health check |

## Compliance Coverage

| Framework | Coverage |
|-----------|----------|
| EU AI Act | Articles 9, 15, Annex IV, Article 72 |
| NIST AI RMF | GOVERN 1.2, MAP 5.1, MEASURE 2.7, MANAGE 4.1 |
| OWASP LLM Top 10 | LLM01, LLM02, LLM06, LLM08 |
| MITRE ATLAS | AML.T0054, AML.T0051, AML.T0043 |

## Attack Providers

| Provider | Status | Coverage |
|----------|--------|----------|
| PyRIT 0.12.0 | ✅ Active | Crescendo multi-turn, SelfAskTrueFalseScorer |
| Garak 0.14.1 | ✅ Active | 100+ failure modes, 20+ model APIs |
| DeepTeam | ✅ Active | Structured scenarios, LLM-synthesized fallback |
| promptfoo 0.121.3 | ✅ Active | Regression testing, CI/CD integration |
| CrewAI | ✅ Active | Multi-agent: Attacker + Mutator + Judge |

## Running Tests

```bash
pytest tests/test_integration.py -v
```

## Environment Variables

ANTHROPIC_API_KEY=sk-ant-...
DEFAULT_MODEL=claude-sonnet-4-6
CI_FAIL_ON_ASR_ABOVE=20.0
SCHEDULED_CAMPAIGN_ENABLED=false
SLACK_WEBHOOK_URL=<https://hooks.slack.com/>...  (optional)
BASE_URL=<http://localhost:8000>
GRAFANA_BASE_URL=<http://localhost:3000>

## Business Value

RTK-1 replaces the equivalent of 15 full-time red team professionals:

- 4 attack execution engineers (24/7 coverage)
- 3 compliance and documentation specialists
- 2 monitoring and operations engineers
- 2 regression and CI/CD engineers
- 2 client communication managers
- 1 scheduling and program manager
- 1 legal and regulatory liaison

**Cost comparison for one enterprise client:**

- Human team: ~$3,150,000/year
- RTK-1: ~$260,000-$320,000/year
- Savings: ~$2,830,000/year

---

*RTK-1 v0.3.0 — Claude Sonnet 4.6 + LangGraph + PyRIT 0.12.0*
*Built for EU AI Act enforcement. Always on. Proof of safety. Every sprint.*
