# RTK-1 ITIL 4 Service Catalog — Objective 90

**Platform:** RTK-1 Autonomous AI Red Teaming  
**Version:** v0.5.0  
**ITIL 4 Practice:** Service Catalog Management  
**Last Updated:** 2026-04-10

---

## Service Utility Statement

RTK-1 delivers autonomous AI red teaming that identifies vulnerabilities in large language models before adversaries exploit them. It removes the constraint of manual security testing by running 24/7 campaigns across 8 attack providers, generating compliance-mapped reports aligned to EU AI Act, NIST AI RMF, OWASP LLM Top 10, and MITRE ATLAS.

## Service Warranty Statement

RTK-1 guarantees:

- **Availability:** 99.5% uptime for scheduled campaign execution
- **Capacity:** Up to 50 concurrent attack sequences per campaign
- **Continuity:** LangGraph checkpointing ensures zero lost campaigns on failure
- **Security:** Immutable audit trail, SHA-256 signed reports, per-tenant isolation

---

## Service Tiers

### Tier 1 — Starter ($2,000/month)

| Attribute | Value |
|-----------|-------|
| Campaigns/month | 10 |
| Providers | PyRIT, Garak, promptfoo |
| Report formats | PDF + Markdown |
| Compliance | OWASP LLM Top 10 |
| Support | Email, 48hr SLT |
| Grafana dashboard | ✅ |
| Scheduled campaigns | ❌ |
| NDAA package | ❌ |

### Tier 2 — Professional ($8,000/month)

| Attribute | Value |
|-----------|-------|
| Campaigns/month | Unlimited |
| Providers | All 5 core providers |
| Report formats | PDF + Markdown + Delivery bundle |
| Compliance | OWASP + NIST AI RMF + EU AI Act |
| Support | Slack, 24hr SLT |
| Grafana dashboard | ✅ |
| Scheduled campaigns | ✅ |
| NDAA package | ❌ |

### Tier 3 — Enterprise ($25,000/month)

| Attribute | Value |
|-----------|-------|
| Campaigns/month | Unlimited |
| Providers | All 8 providers + Digital Twin |
| Report formats | All formats + ISAC XML |
| Compliance | Full stack + MITRE ATLAS |
| Support | Dedicated Slack, 4hr SLT |
| Grafana dashboard | ✅ |
| Scheduled campaigns | ✅ |
| NDAA package | ✅ |
| Federated deployment | ✅ |
| Multi-tenant isolation | ✅ |
| Blast radius engine | ✅ |

### Tier 4 — Federal ($50,000/month)

| Attribute | Value |
|-----------|-------|
| Campaigns/month | Unlimited |
| Providers | All providers + SCADA + Agentic Chain |
| Report formats | All formats + VDP package + mTLS signed |
| Compliance | NDAA 1512 + NDAA 1535 + DHS AI-ISAC |
| Support | Dedicated engineer, 1hr SLT, on-call |
| Grafana dashboard | ✅ |
| Scheduled campaigns | ✅ |
| NDAA package | ✅ |
| Federated deployment | ✅ |
| AI-ISAC integration | ✅ |
| mTLS report signing | ✅ |
| BYOM / Glasswing | ✅ |
| Continual monitoring VDP loop | ✅ |

---

## Service Level Targets (SLT)

| Metric | Starter | Professional | Enterprise | Federal |
|--------|---------|--------------|------------|---------|
| Campaign completion | 4hr | 2hr | 1hr | 30min |
| Report delivery | 1hr post-campaign | 30min | 15min | 5min |
| Alert response | 48hr | 24hr | 4hr | 1hr |
| Scheduled run SLT | N/A | ±15min | ±5min | ±1min |
| Uptime SLA | 99% | 99.5% | 99.9% | 99.99% |

---

## Escalation Paths

```
P1 — Critical (ASR > 80%, SCADA finding, federal breach)
  → Immediate Slack P1 alert → CISO email → VDP disclosure within 1hr

P2 — High (ASR > 50%, new jailbreak technique detected)
  → Slack alert within 15min → Campaign auto-triggered → Report within 2hr

P3 — Medium (ASR > 20%, scheduled campaign result)
  → Grafana dashboard update → Weekly summary PDF → Next business day review

P4 — Low (Informational, trend data, compliance status)
  → Monthly executive email → LinkedIn post auto-generated
```

---

## RACI Matrix

| Activity | Customer | RTK-1 Auto | Engineer | CISO |
|----------|----------|------------|----------|------|
| Define attack goal | R | I | C | I |
| Execute campaign | I | R | I | I |
| Score results | I | R | C | I |
| Generate report | I | R | I | A |
| ISAC disclosure | C | R | C | A |
| Patch validation | C | R | R | A |
| Escalation P1 | I | R | C | A |

**R** = Responsible, **A** = Accountable, **C** = Consulted, **I** = Informed

---

## Continual Improvement Register (Summary)

See `app/core/cir.py` for live register. Current initiatives:

| Priority | Initiative | Status |
|----------|------------|--------|
| Critical | ASR below 20% for all clients | In Progress |
| Critical | Federal NDAA 1512 compliance package | In Progress |
| High | Subscription tier enforcement | In Progress |
| High | 100% objective completion v0.5.0 | In Progress |
| Completed | Loki/ELK log integration (Obj 40) | ✅ 2026-04-10 |

---

*RTK-1 v0.5.0 — ITIL 4 Service Value System*  
*Governing principle: Do not buy unless RTK-1 has already provided the money.*
