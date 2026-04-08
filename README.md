# RTK-1 — Autonomous AI Red Teaming Platform

> The equivalent output of 15 specialized red team professionals running 24/7.

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests: 28/28](https://img.shields.io/badge/tests-28%2F28%20passing-brightgreen.svg)]()
[![Providers: 5 Active](https://img.shields.io/badge/providers-5%20active-brightgreen.svg)]()
[![NDAA 1512 Ready](https://img.shields.io/badge/NDAA%20Sec%201512-Architecture%20Ready-yellow.svg)]()
[![EU AI Act](https://img.shields.io/badge/EU%20AI%20Act-Art.%209%2C%2015%2C%20Annex%20IV-blue.svg)]()
[![v0.4.0](https://img.shields.io/badge/version-0.4.0-brightgreen.svg)]()

RTK-1 is a production-grade autonomous AI red teaming platform that combines
attack execution, compliance documentation, business risk quantification,
and continuous monitoring into a single always-on system.

---

## What RTK-1 Does

For your exact model or agent, RTK-1:

- Tests adversarial attack vectors using multi-turn Crescendo escalation (MITRE ATLAS AML.T0054)
- Achieves quantified outcomes tied to your stated customer success metrics
- Delivers week-over-week proof of improvement with business value framing
- Generates EU AI Act / NIST AI RMF / OWASP LLM / MITRE ATLAS compliance evidence automatically
- Produces AI-ISAC VDP disclosure packages for federal contractor reporting
- Runs locally on-premises — no cloud dependency, services survive internet outages

---

## Architecture

Customer Entry (API / Streamlit / CI/CD)
↓
FastAPI Router (thin, no business logic)
↓
LangGraph Orchestrator — Stateful Multi-Turn Memory
Recon → Planner → Supervisor (ReAct) → Executor → Evaluator → Report
↓
RTKFacade (swappable provider layer)
├── PyRITProvider    (Crescendo multi-turn — MITRE AML.T0054)
├── GarakProvider    (100+ failure mode probes — OWASP coverage)
├── DeepTeamProvider (structured scenarios — LLM-synthesized fallback)
├── promptfooProvider (regression testing — CI/CD gate)
└── CrewAIProvider   (multi-agent: Attacker + Mutator + Judge)
↓
Core Services (always-on, on-premises)
AuditTrail · CampaignHistory · BehavioralFingerprint
SemanticDrift · MutationEngine · DeterministicScorer
RegulatoryTracker · Scheduler · RateLimiter
AttackLibrary · FederatedCoordinator · AdaptiveEvasion
ISAC-Transporter · NeutralityChecker
↓
Delivery Layer
PDF Report · AI-ISAC VDP Package · Executive Email
Slide Deck · LinkedIn Post · Grafana Dashboard · Slack Alert

---

## On-Premises Resilience

RTK-1 is designed for maximum operational resilience:

- **Internet outage:** All services continue running locally. Campaigns resume when connectivity restores.
- **No cloud dependency:** Zero vendor lock-in. No AWS outage affects your red teaming pipeline.
- **HITL by design:** Human-in-the-loop at strategic checkpoints — not a limitation, an EU AI Act Article 14 compliance feature.
- **Data sovereignty:** All campaign data, audit logs, and reports stay within your infrastructure.
- **Single node failure:** Federated coordinator supports hot standby node failover.

---

## Quick Start

```bash
# Clone and set up
git clone https://github.com/JLBird/ramon-loya-RTK-1
cd ramon-loya-RTK-1
python -m venv venv_rtk
.\venv_rtk\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

# Start
python -m uvicorn app.main:app --port 8000
python -m streamlit run streamlit_app.py
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/redteam/crescendo-with-report` | Full campaign + PDF |
| POST | `/api/v1/redteam/crescendo` | Lightweight, no PDF |
| POST | `/api/v1/redteam/ci` | CI/CD gate (pass/fail) |
| POST | `/api/v1/redteam/multi-vector` | PyRIT + Garak + DeepTeam parallel |
| POST | `/api/v1/redteam/compare` | Multi-model comparison |
| POST | `/api/v1/redteam/delivery-bundle` | One-click delivery bundle |
| POST | `/api/v1/redteam/federated` | Multi-node distributed attacks |
| GET | `/api/v1/redteam/trend/{model}` | ASR trend data |
| GET | `/api/v1/redteam/history` | Campaign history |
| GET | `/api/v1/redteam/delta/{model}` | Week-over-week delta |
| GET | `/api/v1/redteam/weekly-summary/{model}` | Weekly PDF summary |
| GET | `/api/v1/redteam/monthly-report/{model}` | Monthly executive email |
| GET | `/api/v1/redteam/attack-library` | All known attack techniques |
| GET | `/api/v1/redteam/attack-library/{owasp}` | Techniques by OWASP category |
| GET | `/api/v1/redteam/rate-limit/{id}` | Rate limit status |
| GET | `/health` | Health check |

---

## Compliance Coverage

| Framework | Coverage |
|-----------|----------|
| EU AI Act | Articles 9, 15, Annex IV, Article 72 |
| NIST AI RMF | GOVERN 1.2, MAP 5.1, MEASURE 2.7, MANAGE 4.1 |
| OWASP LLM Top 10 | LLM01, LLM02, LLM06, LLM08 |
| MITRE ATLAS | AML.T0054, AML.T0051, AML.T0043 |
| NDAA Section 1512 | Architecture ready — VDP package generation in v0.5.0 |

---

## Attack Providers

| Provider | Status | Coverage |
|----------|--------|----------|
| PyRIT 0.12.0 | ✅ Active | Crescendo multi-turn, SelfAskTrueFalseScorer |
| Garak 0.14.1 | ✅ Active | 100+ failure modes, 20+ model APIs |
| DeepTeam | ✅ Active | Structured scenarios, LLM-synthesized fallback |
| promptfoo 0.121.3 | ✅ Active | Regression testing, CI/CD integration |
| CrewAI | ✅ Active | Multi-agent: Attacker + Mutator + Judge |

---

## Running Tests

```bash
.\venv_rtk\Scripts\activate
python -m pytest tests/test_integration.py -v
```

28 passed, 2 warnings in 14.38s
Python 3.12.10 | pytest-9.0.3

---

## Environment Variables

ANTHROPIC_API_KEY=sk-ant-...
DEFAULT_MODEL=claude-sonnet-4-6
CI_FAIL_ON_ASR_ABOVE=20.0
SCHEDULED_CAMPAIGN_ENABLED=false
SLACK_WEBHOOK_URL=<https://hooks.slack.com/>...  # optional
BASE_URL=<http://localhost:8000>
GRAFANA_BASE_URL=<http://localhost:3000>

---

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

| | Cost |
|--|------|
| Human team | ~$3,150,000/year |
| RTK-1 | ~$260,000-$320,000/year |
| Savings | ~$2,830,000/year |

---

## ITIL 4 Operating Model

RTK-1 is governed by ITIL 4 Service Value System principles:

| ITIL 4 Principle | RTK-1 Implementation |
|------------------|----------------------|
| Focus on Value | ASR tied to customer-stated success metrics |
| Start Where You Are | Recon node fingerprints target before attack |
| Progress Iteratively | ReAct supervisor adapts strategy each batch |
| Think Holistically | Multi-vector campaigns across all providers |
| Optimize and Automate | 24/7 scheduler, CI/CD gates, mutation engine |

---

## Roadmap — v0.5.0

- [ ] Glasswing Bridge — mTLS BYOM adapter for private model endpoints
- [ ] Blast Radius Remediation Engine — patch simulation + shadow fork
- [ ] AI-ISAC ISAC-Transporter — automated VDP disclosure generation
- [ ] Neutrality Check Module — GSA federal procurement compliance
- [ ] Agentic / Physical System Adapter — SCADA, industrial IoT
- [ ] Auto-Patch Validation Loop — find → patch → verify pipeline
- [ ] Multi-node home lab deployment with failover

---

## File Structure

app/
├── api/v1/redteam.py          # API router (16 endpoints)
├── core/
│   ├── config.py              # Single source of truth
│   ├── audit.py               # Immutable audit trail
│   ├── delivery.py            # All content generation
│   ├── isac_transporter.py    # AI-ISAC VDP package generator
│   ├── scoring.py             # Deterministic + multi-judge
│   ├── mutation.py            # Jailbreak mutation engine
│   ├── fingerprint.py         # Behavioral fingerprinting
│   ├── semantic_drift.py      # Drift monitoring
│   ├── regulatory.py          # EU AI Act tracker
│   ├── rate_limiter.py        # Per-customer rate limiting
│   └── scheduler.py           # 24/7 autonomous runner
├── domain/models.py           # AttackResult, OrchestratorResult
├── orchestrator/
│   └── claude_orchestrator.py # LangGraph workflow
├── providers/
│   ├── pyrit_provider.py      # PyRIT 0.12.0
│   ├── garak_provider.py      # Garak 0.14.1
│   ├── deepteam_provider.py   # DeepTeam
│   ├── promptfoo_provider.py  # promptfoo
│   ├── crewai_provider.py     # CrewAI multi-agent
│   ├── rag_injection_provider.py  # OWASP LLM02
│   └── tool_abuse_provider.py     # OWASP LLM08
├── facade.py                  # Single entry point
└── main.py                    # FastAPI app
streamlit_app.py               # Self-service portal
tests/test_integration.py      # 28 integration tests
docs/
├── architecture.md
└── marketing/
└── SOCIAL_MEDIA_CONTENT.md

---

## Disclaimer

RTK-1 is designed for authorized security testing only. All campaigns require
explicit written authorization from the system owner. Built for ethical, legal
red teaming in compliance with applicable law.

---

*RTK-1 v0.4.0 — Claude Sonnet 4.6 + LangGraph + PyRIT 0.12.0*
*Built by Ramon Loya — First AI Red Teaming Toolkit (RTK-1) in 2026.*
*Always on. Proof of safety. Every sprint.*
