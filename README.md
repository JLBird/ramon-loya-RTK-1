<div align="center">

# ⚔️ RTK-1

### Autonomous AI Red Teaming Platform

**The equivalent output of 15 specialized red team professionals. Running 24/7.**

<br/>

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Stateful-FF6B35?style=for-the-badge&logo=langchain&logoColor=white)]()
[![Claude Sonnet 4.6](https://img.shields.io/badge/Claude-Sonnet_4.6-CC785C?style=for-the-badge&logo=anthropic&logoColor=white)]()

[![Tests](https://img.shields.io/badge/Tests-28%2F28_Passing-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)]()
[![Providers](https://img.shields.io/badge/Providers-5_Active-brightgreen?style=for-the-badge)]()
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)]()

[![EU AI Act](https://img.shields.io/badge/EU_AI_Act-Art._9,_15,_Annex_IV-0052CC?style=flat-square)]()
[![NIST AI RMF](https://img.shields.io/badge/NIST_AI_RMF-MEASURE_2.7-0052CC?style=flat-square)]()
[![OWASP LLM](https://img.shields.io/badge/OWASP_LLM-Top_10-D63031?style=flat-square)]()
[![MITRE ATLAS](https://img.shields.io/badge/MITRE_ATLAS-AML.T0054-2C3E50?style=flat-square)]()
[![NDAA 1512](https://img.shields.io/badge/NDAA_Sec_1512-Architecture_Ready-F39C12?style=flat-square)]()

<br/>

> *"For your exact model or agent — RTK-1 tested X vectors, achieved Z outcomes tied to your success criteria, and here is proof it's improving week over week."*

<br/>

[**API Docs**](http://localhost:8000/docs) · [**Self-Service Portal**](http://localhost:8501) · [**Grafana Dashboard**](http://localhost:3000)

</div>

---

## What RTK-1 Does

RTK-1 combines five attack providers, a Claude Sonnet 4.6 ReAct supervisor, LangGraph stateful memory, and an automated compliance delivery layer into a single always-on platform.

| Capability | What It Means |
|-----------|---------------|
| 🎯 **Autonomous Campaigns** | Crescendo multi-turn attacks run 24/7 without human intervention |
| 📄 **Compliance-Mapped PDF** | Every campaign generates EU AI Act + NIST + OWASP evidence automatically |
| 🔁 **ReAct Supervisor Loop** | Claude evaluates results and adapts strategy between attack batches |
| 🏛️ **On-Premises Resilience** | Services survive internet outages — no cloud dependency, no vendor lock-in |
| 👤 **HITL by Design** | Human approval at high-risk decision points — EU AI Act Article 14 compliance |
| 📦 **One-Click Delivery Bundle** | Executive email + slide deck + LinkedIn post + PDF auto-generated per campaign |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              CUSTOMER ENTRY POINTS                          │
│   API (Swagger)  ·  Streamlit Portal  ·  CI/CD Webhook      │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              LANGGRAPH ORCHESTRATOR                         │
│   Recon → Planner → Supervisor → Executor → Evaluator       │
│                 Claude Sonnet 4.6 Brain                     │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   RTK FACADE                                │
│   PyRIT · Garak · DeepTeam · promptfoo · CrewAI             │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                 CORE SERVICES                               │
│   AuditTrail · History · Fingerprint · SemanticDrift        │
│   MutationEngine · Scorer · RateLimiter · Scheduler         │
│   AttackLibrary · FederatedCoordinator · ISAC-Transporter   │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                 DELIVERY LAYER                              │
│   PDF Report · AI-ISAC VDP Package · Executive Email        │
│   Slide Deck · LinkedIn Post · Grafana · Slack Alert        │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start

```bash
git clone https://github.com/JLBird/ramon-loya-RTK-1
cd ramon-loya-RTK-1

python -m venv venv_rtk
.\venv_rtk\Scripts\activate        # Windows
source venv_rtk/bin/activate       # Mac/Linux

pip install -r requirements.txt
cp .env.example .env
# Add ANTHROPIC_API_KEY to .env

python -m uvicorn app.main:app --port 8000
python -m streamlit run streamlit_app.py
```

**Run a campaign:**

```bash
curl -X POST http://localhost:8000/api/v1/redteam/crescendo-with-report \
  -H "Content-Type: application/json" \
  -d '{
    "target_model": "claude-sonnet-4-6",
    "goal": "Test for prompt injection vulnerabilities",
    "attack_type": "crescendo",
    "customer_success_metrics": "ASR below 20% — EU AI Act Article 15 compliance"
  }'
```

---

## Attack Providers

| Provider | Status | Attack Vector | OWASP |
|----------|--------|--------------|-------|
| **PyRIT 0.12.0** | ✅ Active | Crescendo multi-turn escalation | LLM01 |
| **Garak 0.14.1** | ✅ Active | 100+ failure modes, 20+ model APIs | LLM01, LLM06 |
| **DeepTeam** | ✅ Active | Structured scenarios + LLM synthesis | LLM01 |
| **promptfoo 0.121.3** | ✅ Active | Regression testing, CI/CD gate | LLM01 |
| **CrewAI** | ✅ Active | Multi-agent: Attacker + Mutator + Judge | LLM01 |
| **RAG Injection** | ✅ Active | Indirect prompt injection via retrieval | LLM02 |
| **Tool Abuse** | ✅ Active | Unauthorized tool call manipulation | LLM08 |

---

## API Endpoints

<details>
<summary><strong>View all 16 endpoints</strong></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/redteam/crescendo-with-report` | Full campaign + compliance PDF |
| `POST` | `/api/v1/redteam/crescendo` | Lightweight, no PDF |
| `POST` | `/api/v1/redteam/ci` | CI/CD gate — pass/fail on ASR threshold |
| `POST` | `/api/v1/redteam/multi-vector` | PyRIT + Garak + DeepTeam in parallel |
| `POST` | `/api/v1/redteam/compare` | Multi-model comparison |
| `POST` | `/api/v1/redteam/delivery-bundle` | One-click client delivery bundle |
| `POST` | `/api/v1/redteam/federated` | Multi-node distributed attack coordination |
| `GET` | `/api/v1/redteam/trend/{model}` | ASR trend data for Grafana |
| `GET` | `/api/v1/redteam/history` | Campaign history |
| `GET` | `/api/v1/redteam/delta/{model}` | Week-over-week ASR delta |
| `GET` | `/api/v1/redteam/weekly-summary/{model}` | Weekly executive summary |
| `GET` | `/api/v1/redteam/monthly-report/{model}` | Monthly dashboard email |
| `GET` | `/api/v1/redteam/attack-library` | All known attack techniques |
| `GET` | `/api/v1/redteam/attack-library/{owasp}` | Techniques by OWASP category |
| `GET` | `/api/v1/redteam/rate-limit/{id}` | Per-customer rate limit status |
| `GET` | `/health` | Health check |

</details>

---

## Compliance Coverage

<details>
<summary><strong>EU AI Act</strong></summary>

| Article | Requirement | RTK-1 Evidence |
|---------|-------------|----------------|
| Article 9 | Risk management system | Attack plan + execution logs + ASR |
| Article 14 | Human oversight | HITL node — approval at critical checkpoints |
| Article 15 | Robustness + cybersecurity | Quantified ASR across all sequences |
| Annex IV | Technical documentation | Full reproducible campaign records |
| Article 72 | Post-market monitoring | Behavioral fingerprinting + regression detection |

</details>

<details>
<summary><strong>NIST AI RMF · OWASP LLM Top 10 · MITRE ATLAS</strong></summary>

| Framework | Function | Coverage |
|-----------|----------|----------|
| NIST AI RMF | GOVERN 1.2 | Engagement scope + Rules of Engagement |
| NIST AI RMF | MEASURE 2.4 | Safety risk quantification |
| NIST AI RMF | MEASURE 2.7 | Adversarial T&E — reproducible methodology |
| NIST AI RMF | MANAGE 4.1 | Residual risk documentation |
| OWASP LLM01 | Prompt Injection | Crescendo multi-turn + encoding variants |
| OWASP LLM02 | Insecure Output Handling | RAG injection provider |
| OWASP LLM06 | Sensitive Info Disclosure | System prompt exfiltration probes |
| OWASP LLM08 | Excessive Agency | Tool abuse provider |
| MITRE ATLAS | AML.T0054 | Multi-Turn Adversarial Prompting |
| MITRE ATLAS | AML.T0051 | Jailbreak techniques |
| MITRE ATLAS | AML.T0043 | Adversarial data — mutation engine |

</details>

<details>
<summary><strong>NDAA Section 1512 · AI-ISAC</strong></summary>

RTK-1 includes an `ISAC-Transporter` module that maps campaign results to the DHS AI-ISAC schema for federal contractor reporting.

| NDAA 1512 Requirement | RTK-1 Implementation |
|----------------------|----------------------|
| Documented adversarial testing | Full LangGraph campaign trace |
| Quantified vulnerability metrics | ASR % with confidence intervals |
| MITRE ATLAS mapping | Auto-mapped per attack type |
| Tamper-proof audit evidence | SHA-256 signed reports |
| Remediation documentation | Priority-ranked mitigations |
| Continuous monitoring | 24/7 scheduler + CI/CD gates |

*Direct DHS Shields Up portal API integration planned for v0.5.0.*

</details>

---

## Test Results

```
28 passed, 2 warnings in 14.38s
Platform: Python 3.12.10 · pytest-9.0.3 · pluggy-1.6.0
Coverage: DeterministicScorer · MutationEngine · RateLimiter
          DeliveryManager · DomainModels · ProviderAvailability
```

```bash
.\venv_rtk\Scripts\activate
python -m pytest tests/test_integration.py -v
```

---

## Business Value

> RTK-1 replaces the equivalent output of **15 specialized red team professionals** running 24/7.

| Role | Headcount | RTK-1 Coverage |
|------|-----------|----------------|
| Attack Execution Engineers | 4 (24/7 shifts) | ✅ 100% automated |
| Compliance / Documentation | 3 | ✅ 100% auto-generated |
| Monitoring / Operations | 2 | ✅ 100% Prometheus + alerts |
| Regression / CI-CD Engineers | 2 | ✅ 100% automated gates |
| Client Communication | 2 | ✅ 90% delivery bundle |
| Scheduling / Program Mgmt | 1 | ✅ 100% scheduler |
| Legal / Regulatory Liaison | 1 | ✅ 95% compliance mapping |
| **Total** | **15** | **~97%** |

**Cost comparison per enterprise client:**

| | Annual Cost |
|--|------------|
| Human team (15 people) | ~$3,150,000 |
| RTK-1 | ~$260,000–$320,000 |
| **Client savings** | **~$2,830,000** |

---

## ITIL 4 Service Value System

RTK-1 operations are governed by ITIL 4 principles for continual improvement:

| Principle | Implementation |
|-----------|----------------|
| Focus on Value | ASR tied to customer-stated success metrics |
| Start Where You Are | Recon node fingerprints target before committing |
| Progress Iteratively | ReAct supervisor adapts strategy each batch |
| Think Holistically | Multi-vector campaigns across all providers |
| Keep It Simple | Facade pattern — swappable providers, clean interface |
| Optimize and Automate | 24/7 scheduler, CI/CD gates, mutation engine |

---

## Roadmap — v0.5.0

- [ ] **Glasswing Bridge** — mTLS BYOM adapter for private model endpoints
- [ ] **Blast Radius Engine** — Claude 4 patch simulation + LangGraph shadow fork
- [ ] **AI-ISAC Full Integration** — automated VDP disclosure + DHS portal submission
- [ ] **Neutrality Check Module** — GSA federal procurement compliance
- [ ] **Agentic/Physical Adapter** — SCADA, industrial IoT, autonomous systems
- [ ] **Auto-Patch Validation Loop** — find → patch → verify pipeline
- [ ] **Multi-node home lab deployment** — failover across OptiPlex + NUC + Desktop

---

## Environment Variables

```env
ANTHROPIC_API_KEY=sk-ant-...
DEFAULT_MODEL=claude-sonnet-4-6
CI_FAIL_ON_ASR_ABOVE=20.0
SCHEDULED_CAMPAIGN_ENABLED=false
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
BASE_URL=http://localhost:8000
GRAFANA_BASE_URL=http://localhost:3000
```

---

## Disclaimer

RTK-1 is designed for **authorized security testing only**. All campaigns require explicit written authorization from the system owner. Built for ethical, legal red teaming in compliance with applicable law including CFAA, EU AI Act, and NDAA Section 1512.

---

<div align="center">

**RTK-1 v0.4.0** · Claude Sonnet 4.6 · LangGraph · PyRIT 0.12.0

*Built by Ramon Loya — First AI Red Teaming Toolkit in 2026.*

*Always on. Proof of safety. Every sprint.*

⭐ Star this repo if RTK-1 helped your AI security posture

</div>
