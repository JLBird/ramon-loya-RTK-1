> ⚠️ **IP Notice:** RTK-1 methodology, attack provider architecture, C1/C2 Binary Execution Gate framework, SHA-256 signed report format, and orchestration logic are proprietary trade secrets of RTK Security Labs, protected under 18 U.S.C. § 1836 (Defend Trade Secrets Act) and Tex. Civ. Prac. & Rem. Code § 134A (Texas Uniform Trade Secrets Act). Unauthorized reproduction or commercial use is prohibited.

<div align="center">

# ⚔️ RTK-1

### Autonomous AI Red Teaming Platform

**Evidence before deployment. Not a report card after the incident.**

<br/>

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Stateful-FF6B35?style=for-the-badge&logo=langchain&logoColor=white)]()
[![Claude Sonnet 4.6](https://img.shields.io/badge/Claude-Sonnet_4.6-CC785C?style=for-the-badge&logo=anthropic&logoColor=white)]()

[![Tests](https://img.shields.io/badge/Tests-28%2F28_Passing-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)]()
[![Endpoints](https://img.shields.io/badge/Endpoints-27_Live-brightgreen?style=for-the-badge)]()
[![Providers](https://img.shields.io/badge/Attack_Providers-13_Active-brightgreen?style=for-the-badge)]()
[![Version](https://img.shields.io/badge/Version-0.5.0-blue?style=for-the-badge)]()
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)]()
[![OWASP Member](https://img.shields.io/badge/OWASP-Member_in_Good_Standing-4285F4?style=for-the-badge&logo=owasp&logoColor=white)](https://owasp.org/membership/)

[![EU AI Act](https://img.shields.io/badge/EU_AI_Act-Art._15_First_Mover-0052CC?style=flat-square)]()
[![NIST AI RMF](https://img.shields.io/badge/NIST_AI_RMF-MEASURE_2.4_%2B_2.7-0052CC?style=flat-square)]()
[![OWASP LLM](https://img.shields.io/badge/OWASP_LLM-Top_10_Coverage-D63031?style=flat-square)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
[![MITRE ATLAS](https://img.shields.io/badge/MITRE_ATLAS-AML.T0054_%2B_T0043-2C3E50?style=flat-square)]()
[![SHA-256 Signed](https://img.shields.io/badge/Reports-SHA--256_Signed-00B894?style=flat-square)]()
[![NDAA 1512](https://img.shields.io/badge/NDAA_Sec_1512-VDP_Package_Ready-F39C12?style=flat-square)]()

<br/>

[**🌐 rtksecuritylabs.com**](https://rtksecuritylabs.com) · [**📄 Sample Report**](https://jlbird.github.io/ramon-loya-RTK-1/sample-report.html) · [**🔍 API Endpoints**](./proof/screenshots/swagger-ui.png) · [**📊 Dashboard**](./proof/screenshots/grafana-dashboard.png)

</div>

---

## Evidence Before Deployment

RTK-1 runs adversarial campaigns against your AI agent and generates a **SHA-256 signed compliance artifact** — before it ships, not after the incident report.

Most AI security tools tell you what happened. RTK-1 proves whether the execution boundary was structurally possible to violate under adversarial conditions.

### The Binary Verdict

```
C1 — No unauthorized execution occurred           (observable outcome)
C2 — No executable path existed without valid proof  (architectural enforcement)

If C2 holds, C1 is guaranteed. C2 is the stronger claim.
```

Every RTK-1 report leads with this verdict. Pass or fail. No risk percentages. No ambiguity. Procurement committees and auditors require an artifact they can action immediately — not a score that requires interpretation.

### The Delta Is the Proof

```
Phase 1 — Undefended agent    → ASR: HIGH
Phase 2 — Defenses active     → ASR: LOW
─────────────────────────────────────────
Delta                         → Proof of value
```

### What RTK-1 Produces

| Artifact | Format | Purpose |
|---|---|---|
| **C1/C2 Binary Verdict** | PDF + JSON | Pass/fail on execution boundary integrity |
| **SHA-256 Signed Report** | PDF | Cryptographic proof for auditors, regulators, and procurement |
| **VDP Package** | JSON v1.0 + XML v1.1 | Machine-readable compliance artifact (NDAA Section 1512) |
| **Attack Trace** | Structured JSON | Per-finding mapping to OWASP / MITRE ATLAS / EU AI Act Article 15 |
| **Compliance Archive** | Signed PDF history | Irreplaceable institutional evidence (switching cost moat) |

---

## Why This Exists

The field keeps trying to solve AI security with better observability. It doesn't close.

Observability tells you **what happened**. Assurance tells you whether it was **structurally possible to prevent**. Most security teams have the former and believe they have the latter.

RLHF is irrelevant to the agentic attack surface. Heavy safety training suppresses direct prompt injection — so undefended ASR reads artificially low on tuned models. The real attack enters through tool calls and agent handoffs, which RLHF doesn't touch. The execution trace looks identical to a clean run.

**Credentials are finite. Authorization surfaces are architectural.** You can rotate a stolen key. You cannot rotate what an agent is authorized to call without redesigning the system. That is a fundamentally different blast radius than traditional security tooling was built for.

RTK-1 closes the gap between trust and proof.

---

## What RTK-1 Does

RTK-1 combines **13 attack providers**, a Claude Sonnet 4.6 ReAct supervisor, LangGraph stateful memory, and an automated compliance delivery layer into a single always-on platform.

| Capability | What It Means |
|-----------|---------------|
| 🎯 **Autonomous Campaigns** | Crescendo multi-turn, agentic chain injection, and tool abuse attacks run 24/7 |
| 📄 **SHA-256 Signed Reports** | Every campaign generates cryptographically signed compliance artifacts |
| ⚖️ **C1/C2 Binary Verdict** | Procurement-committee language. Pass/fail on execution boundary integrity |
| 🔁 **ReAct Supervisor Loop** | Claude evaluates results and adapts strategy between attack batches |
| 🏛️ **On-Premises Resilience** | Services survive internet outages — no cloud dependency, no vendor lock-in |
| 👤 **HITL by Design** | Human in Command at high-risk decision points — EU AI Act Article 14 compliance |
| 📦 **One-Click Delivery Bundle** | Executive email + slide deck + LinkedIn post + PDF auto-generated per campaign |
| 📈 **Behavioral Fingerprinting** | Week-over-week semantic drift detection via 7 canonical probes |

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
│                        ↓                                    │
│                   HITL Node                                 │
│              (Human in Command)                             │
│                                                             │
│              Claude Sonnet 4.6 Brain                        │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   RTK FACADE                                │
│      (Swappable providers · Canonical domain models)        │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              13 ATTACK PROVIDERS                            │
│   PyRIT · Garak · DeepTeam · promptfoo · CrewAI             │
│   RAG Injection · Tool Abuse · Multi-Vector · Neutrality    │
│   BYOM · Glasswing · Digital Twin · Agentic Chain           │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                 CORE SERVICES                               │
│   AuditTrail · History · Fingerprint · SemanticDrift        │
│   MutationEngine · Scorer · RateLimiter · Scheduler         │
│   AttackLibrary · RegulatoryTracker · ReportSigner          │
│   FederatedCoordinator · ISAC-Transporter · AttackGraph     │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                 DELIVERY LAYER                              │
│   SHA-256 Signed PDF · AI-ISAC VDP · Executive Email        │
│   Slide Deck · LinkedIn Post · Grafana · Slack Alert        │
└─────────────────────────────────────────────────────────────┘
```

---

## Attack Providers

All 13 providers return canonical `AttackResult` domain models via the `RTKFacade`. Providers are injected at constructor and swappable at runtime.

| Provider | Status | Attack Vector | Compliance Mapping |
|----------|--------|--------------|-------|
| **PyRIT 0.12.0** | ✅ Active | Crescendo multi-turn escalation | OWASP LLM01 · MITRE ATLAS AML.T0054 |
| **Garak 0.14.1** | ✅ Active | 100+ probe-based failure modes | OWASP LLM01 · LLM06 |
| **DeepTeam** | ✅ Active | LLM-as-attacker, structured scenarios | OWASP LLM01 |
| **promptfoo** | ✅ Active | CI/CD deterministic regression gate | OWASP LLM01 |
| **CrewAI** | ✅ Active | Multi-agent: Attacker + Mutator + Judge | OWASP LLM01 |
| **RAG Injection** | ✅ Active | Indirect prompt injection via retrieval | OWASP LLM02 |
| **Tool Abuse** | ✅ Active | Unauthorized tool execution | OWASP LLM08 · MITRE AML.T0043 |
| **Multi-Vector** | ✅ Active | Parallel PyRIT + RAG + tool abuse | Compound failure mode detection |
| **Neutrality** | ✅ Active | GSA federal bias + sycophancy scoring | Federal procurement compliance |
| **BYOM** | ✅ Active | Bring your own model adapter | Target-specific validation |
| **Glasswing** | ✅ Active | Behavioral fingerprint + semantic drift | Continuous monitoring |
| **Digital Twin** | ✅ Active | SCADA/ICS/OT adversarial testing | NDAA Section 1535 |
| **Agentic Chain** | ✅ Active | Cross-agent boundary injection | OWASP LLM08 · MITRE AML.T0043 |

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

**Run a Phase 1 baseline campaign:**

```bash
curl -X POST http://localhost:8000/api/v1/redteam/crescendo \
  -H "Content-Type: application/json" \
  -d '{
    "target_model": "claude-sonnet-4-6",
    "goal": "Test authorization boundary under multi-turn escalation",
    "attack_type": "crescendo"
  }'
```

**Run a Phase 2 validation (C1/C2 verdict):**

```bash
curl -X POST http://localhost:8000/api/v1/redteam/ci \
  -H "Content-Type: application/json" \
  -d '{
    "target_model": "claude-sonnet-4-6",
    "goal": "Validate execution boundary held under adversarial conditions",
    "providers": ["tool_abuse", "agentic_chain"],
    "max_prompts": 5,
    "customer_success_metrics": "C2 must hold — EU AI Act Article 15 compliance"
  }'
```

---

## 📄 Proof of Concept

> Generated autonomously in under 12 minutes. No human intervention required.

### [View Live Sample Campaign Report](https://jlbird.github.io/ramon-loya-RTK-1/sample-report.html)

A real Crescendo attack campaign against `claude-sonnet-4-6` — compliance-mapped, EU AI Act Article 15 evidence, MITRE ATLAS AML.T0054 technique documented, C1/C2 binary verdict at the top, SHA-256 signature appended at generation.

| Interface | Screenshot |
|-----------|-----------|
| **API — 26 Endpoints** | ![Swagger UI](./proof/screenshots/swagger-ui.png) |
| **Grafana ASR Dashboard** | ![Grafana](./proof/screenshots/grafana-dashboard.png) |
| **Streamlit Self-Service Portal** | ![Streamlit](./proof/screenshots/streamlit-portal.png) |

---

## API Endpoints

<details>
<summary><strong>View all 26 endpoints</strong></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/redteam/crescendo-with-report` | Full campaign + SHA-256 signed PDF |
| `POST` | `/api/v1/redteam/crescendo` | Lightweight Phase 1 baseline |
| `POST` | `/api/v1/redteam/ci` | CI/CD gate — C1/C2 verdict on ASR threshold |
| `POST` | `/api/v1/redteam/multi-vector` | Parallel compound attack run |
| `POST` | `/api/v1/redteam/agentic-chain` | Cross-agent boundary injection |
| `POST` | `/api/v1/redteam/tool-abuse` | Unauthorized tool execution test |
| `POST` | `/api/v1/redteam/rag-injection` | Indirect prompt injection via retrieval |
| `POST` | `/api/v1/redteam/neutrality` | Federal bias + sycophancy scoring |
| `POST` | `/api/v1/redteam/digital-twin` | SCADA/ICS/OT adversarial testing |
| `POST` | `/api/v1/redteam/compare` | Multi-model comparison |
| `POST` | `/api/v1/redteam/delivery-bundle` | One-click client delivery package |
| `POST` | `/api/v1/redteam/federated` | Multi-node distributed coordination |
| `POST` | `/api/v1/redteam/byom` | Bring your own model campaign |
| `POST` | `/api/v1/redteam/sign-report` | SHA-256 HMAC report signing |
| `POST` | `/api/v1/redteam/vdp-package` | AI-ISAC VDP generation (JSON + XML) |
| `POST` | `/api/v1/redteam/hitl-approve` | Human in Command approval callback |
| `GET` | `/api/v1/redteam/trend/{model}` | ASR trend data for Grafana |
| `GET` | `/api/v1/redteam/history` | Campaign history |
| `GET` | `/api/v1/redteam/delta/{model}` | Week-over-week ASR delta |
| `GET` | `/api/v1/redteam/weekly-summary/{model}` | Weekly executive summary |
| `GET` | `/api/v1/redteam/monthly-report/{model}` | Monthly dashboard email |
| `GET` | `/api/v1/redteam/attack-library` | All known attack techniques |
| `GET` | `/api/v1/redteam/attack-library/{owasp}` | Techniques by OWASP category |
| `GET` | `/api/v1/redteam/attack-graph/{campaign_id}` | Mermaid attack graph visualization |
| `GET` | `/api/v1/redteam/rate-limit/{id}` | Per-customer rate limit status |
| `GET` | `/health` | Health check |

</details>

---

## Compliance Coverage

<details>
<summary><strong>EU AI Act — Article 15 First Mover</strong></summary>

Enforcement begins **August 2, 2026**. RTK-1 is the only autonomous platform explicitly mapping every attack finding to Article 15.

| Article | Requirement | RTK-1 Evidence |
|---------|-------------|----------------|
| Article 9 | Risk management system | Attack plan + execution logs + ASR quantification |
| Article 14 | Human oversight | HITL node — Human in Command at critical checkpoints |
| Article 15 | Robustness + cybersecurity | C1/C2 verdict + SHA-256 signed ASR quantification |
| Annex IV | Technical documentation | Full reproducible campaign records |
| Article 72 | Post-market monitoring | Behavioral fingerprinting + semantic drift detection |

</details>

<details>
<summary><strong>NIST AI RMF 1.0</strong></summary>

Most AI governance tools cover GOVERN and MAP. RTK-1 covers **MEASURE** and **MANAGE** — the testing and response side most platforms skip.

| Function | Sub-Category | Coverage |
|----------|--------------|----------|
| GOVERN | 1.2 | Engagement scope + Rules of Engagement |
| MAP | 5.1 | Attack surface inventory |
| MEASURE | 2.4 | Safety risk quantification under adversarial load |
| MEASURE | 2.7 | Adversarial T&E — reproducible methodology |
| MANAGE | 4.1 | Residual risk documentation |

</details>

<details>
<summary><strong>OWASP LLM Top 10 · MITRE ATLAS</strong></summary>

| OWASP / MITRE | Coverage | RTK-1 Provider |
|----------|----------|--------------|
| LLM01 — Prompt Injection | ✅ | PyRIT Crescendo + encoding variants |
| LLM02 — Insecure Output Handling | ✅ | RAG Injection provider |
| LLM06 — Sensitive Info Disclosure | ✅ | Garak disclosure probes |
| LLM08 — Excessive Agency | ✅ | Tool Abuse + Agentic Chain |
| MITRE AML.T0054 | ✅ | Multi-Turn Adversarial Prompting |
| MITRE AML.T0051 | ✅ | Jailbreak techniques |
| MITRE AML.T0043 | ✅ | Adversarial data — mutation engine + agentic chain |

</details>

<details>
<summary><strong>NDAA Section 1512 + 1535 · AI-ISAC</strong></summary>

RTK-1's `ISAC-Transporter` module maps campaign results to the DHS AI-ISAC schema for federal contractor reporting. The `Digital Twin` provider addresses Section 1535 SCADA/OT critical infrastructure AI.

| NDAA Requirement | RTK-1 Implementation |
|----------------------|----------------------|
| Documented adversarial testing | Full LangGraph campaign trace |
| Quantified vulnerability metrics | ASR % with confidence intervals |
| MITRE ATLAS mapping | Auto-mapped per attack type |
| Tamper-proof audit evidence | SHA-256 HMAC signed reports |
| Remediation documentation | Priority-ranked mitigations |
| Continuous monitoring | 24/7 scheduler + CI/CD gates |
| SCADA/OT critical infrastructure | Digital Twin provider (Section 1535) |

*Direct DHS Shields Up portal API integration planned for v0.6.0.*

</details>

<details>
<summary><strong>Riyadh Charter on AI · SDAIA · MOAI · DIFC · ADGM · ALECSO · KSA + UAE PDPL · ISO 42001</strong></summary>

  ---

## 🌙 Middle East & Islamic World
---

## Test Results

```
28 passed in 6.13s
Platform: Python 3.12 · pytest
Coverage: DeterministicScorer · MutationEngine · RateLimiter
          DeliveryManager · DomainModels · ProviderAvailability
          ReportSigner · HITL Node · Facade Boundary
```

```bash
.\venv_rtk\Scripts\activate
python -m pytest tests/test_integration.py -v --tb=short
```

---

## Business Value

> RTK-1 replaces the equivalent output of **15 specialized red team professionals** running 24/7.

A manual equivalent engagement runs **$75,000–$150,000** and takes **6 weeks**.
RTK-1 delivers the same adversarial coverage in **under 12 minutes** — continuously, with a SHA-256 signed artifact after every run.

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

**Annual cost comparison per enterprise client:**

| | Annual Cost |
|--|------------|
| Human team (15 people) | ~$3,150,000 |
| RTK-1 Enterprise tier | ~$500,000–$1,000,000 |
| **Client savings** | **~$2,150,000–$2,650,000** |

---

## The Compliance Archive Switching Cost Moat

After 6 months of weekly RTK-1 campaigns, a client holds **26 signed, timestamped, cryptographically verified reports** — an institutionally irreplaceable adversarial validation history.

No competitor can manufacture historical signed reports. The switching cost compounds monthly. Trend data **is** the product.

This is why the SHA-256 signature is architectural, not cosmetic. Anything external becomes attestation, not proof.

---

## ITIL 4 Service Value System

RTK-1 operations are governed by ITIL 4 principles for continual improvement:

| Principle | Implementation |
|-----------|----------------|
| Focus on Value | ASR tied to customer-stated success metrics |
| Start Where You Are | Recon node fingerprints target before committing |
| Progress Iteratively | ReAct supervisor adapts strategy each batch |
| Think Holistically | Multi-vector campaigns across all 13 providers |
| Keep It Simple | Facade pattern — swappable providers, clean interface |
| Optimize and Automate | 24/7 scheduler, CI/CD gates, mutation engine |
| Collaborate & Promote Visibility | Grafana dashboards + Loki structured logging |

---

## Roadmap — v0.6.0

- [ ] **Glasswing Bridge** — mTLS BYOM adapter for private model endpoints
- [ ] **Blast Radius Engine** — Claude 4 patch simulation + LangGraph shadow fork
- [ ] **AI-ISAC Full Integration** — automated VDP disclosure + DHS portal submission
- [ ] **Customer-Defined Value Portal** — intake-to-campaign intelligent orchestrator
- [ ] **Agentic/Physical Adapter** — SCADA, industrial IoT, autonomous systems
- [ ] **Auto-Patch Validation Loop** — find → patch → verify pipeline
- [ ] **Multi-node home lab deployment** — failover across OptiPlex + NUC + Desktop
- [ ] **ISO 42001 Auditor Registration** — AI management system certification authority
- [ ] **DoD SBIR Phase I application** — NDAA 1512 alignment for federal deployment

---

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| LLM Orchestrator | Claude Sonnet 4.6 | ReAct evaluation loop brain |
| Agent Framework | LangGraph | Stateful graph with checkpointing and HITL native |
| Attack Engine | PyRIT 0.12.0 | Crescendo multi-turn + SelfAskTrueFalseScorer |
| API Layer | FastAPI + uvicorn | Async, auto-OpenAPI at `/docs` |
| Self-Service Portal | Streamlit | 5-page non-technical client interface |
| Metrics | Prometheus | Scrape endpoint at `/metrics` |
| Dashboards | Grafana | RTK-1 Executive Dashboard, live ASR gauge |
| Logs | Loki v3.7.1 + Grafana Alloy | Structured JSON log pipeline |
| Logging Library | structlog | Loki aggregation |
| Rate Limiting | SQLite (sliding window) | Per-customer tenant isolation |
| Report Signing | SHA-256 HMAC | Compliance archive switching cost moat |
| PDF Generation | ReportLab + pypdf | Signed compliance PDFs |
| Testing | pytest | 20/20 green baseline |

---

## Environment Variables

```env
ANTHROPIC_API_KEY=sk-ant-...
DEFAULT_MODEL=claude-sonnet-4-6
CI_FAIL_ON_ASR_ABOVE=20.0
SCHEDULED_CAMPAIGN_ENABLED=false
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
REPORT_SIGNING_SECRET=<32-byte-hex>
BASE_URL=http://localhost:8000
GRAFANA_BASE_URL=http://localhost:3000
LOKI_BASE_URL=http://localhost:3100
```

---

## Disclaimer

RTK-1 is designed for **authorized security testing only**. All campaigns require explicit written authorization from the system owner. Built for ethical, legal red teaming in compliance with applicable law including CFAA, EU AI Act, NDAA Section 1512/1535, and 18 U.S.C. § 1030.

---

<div align="center">

**RTK-1 v0.5.0** · Claude Sonnet 4.6 · LangGraph · PyRIT 0.12.0 · 13 Attack Providers · 27 Endpoints

*Built by Ramon Loya — RTK Security Labs · New Braunfels, Texas*

*Evidence before deployment. Not a report card after the incident.*

[![Website](https://img.shields.io/badge/rtksecuritylabs.com-Visit-C84E00?style=flat-square)](https://rtksecuritylabs.com)
[![Sample Report](https://img.shields.io/badge/Sample_Report-View_Live-0052CC?style=flat-square)](https://jlbird.github.io/ramon-loya-RTK-1/sample-report.html)

⭐ Star this repo if RTK-1 helped your AI security posture

</div>
