# RTK-1 OBJECTIVES — v0.5.0 Roadmap

## COMPLETED ✅ (v0.3.0 — v0.4.0)

```
Objective 1  ✅ — Full compliance-mapped PDF report generator
Objective 2  ✅ — Dynamic customer-defined scorer
Objective 3  ✅ — Domain models (AttackResult, OrchestratorResult)
Objective 4  ✅ — Swappable facade + dependency injection
Objective 5  ✅ — EngagementConfig structured intake
Objective 6  ✅ — ReAct eval-driven supervisor with reflection loops
Objective 7  ✅ — Async parallel sequence execution
Objective 8  ✅ — LangGraph checkpointing (SqliteSaver)
Objective 9  ✅ — Human-in-the-loop node (Slack + audit)
Objective 10 ✅ — Tenacity on all external calls
Objective 11 ✅ — Structured JSON logging (structlog)
Objective 14 ✅ — Garak provider v0.14.1 (sys.executable fix)
Objective 15 ✅ — DeepTeam provider (LLM-synthesized fallback)
Objective 16 ✅ — promptfoo provider v0.121.3
Objective 17 ✅ — CrewAI multi-agent (Attacker + Mutator + Judge)
Objective 18 ✅ — Recon→Planner→Executor→Evaluator graph
Objective 19 ✅ — Multi-vector unified campaigns
Objective 20 ✅ — Campaign history store + ASR trend DB
Objective 21 ✅ — ASR delta "93% safer" business framing
Objective 22 ✅ — Risk dashboard in every report
Objective 23 ✅ — CI/CD webhook endpoint
Objective 24 ✅ — Scheduled 24/7 campaign runner
Objective 25 ✅ — Slack/Teams ASR spike alerts
Objective 27 ✅ — Per-customer rate limiting (sliding window)
Objective 28 ✅ — Prometheus + Grafana ASR trend panels
Objective 29 ✅ — One-click delivery bundle
Objective 30 ✅ — architecture.md (living document)
Objective 31 ✅ — Integration test suite (28/28 passing)
Objective 32 ✅ — Single source of truth config
Objective 33 ✅ — Full audit trail store (immutable)
Objective 35 ✅ — GitHub Actions CI/CD workflow
Objective 38 ✅ — Mutation engine (10 algorithmic variants)
Objective 39 ✅ — Weekly PDF summary auto-generation
Objective 43 ✅ — Executive email template auto-generator
Objective 44 ✅ — 3-slide deck content auto-generator
Objective 45 ✅ — Monthly executive dashboard email
Objective 46 ✅ — Public GitHub documentation (docs/README.md)
Objective 47 ✅ — Business value statement generator
Objective 48 ✅ — LinkedIn post template auto-generator
Objective 50 ✅ — Jailbreak mutation engine
Objective 51 ✅ — Multimodal provider foundation
Objective 52 ✅ — Adaptive evasion layer
Objective 53 ✅ — RAG injection provider (OWASP LLM02)
Objective 54 ✅ — Tool abuse provider (OWASP LLM08)
Objective 55 ✅ — Multi-judge consensus scorer
Objective 56 ✅ — Deterministic rule-based scorers
Objective 57 ✅ — Parallel model comparison runner
Objective 58 ✅ — Behavioral fingerprinting + model versioning
Objective 59 ✅ — Streamlit self-service portal
Objective 60 ✅ — Adversarial fine-tuning detection suite
Objective 61 ✅ — Semantic drift monitoring
Objective 63 ✅ — Attack library + arXiv monitoring
Objective 64 ✅ — Model fingerprinting
Objective 65 ✅ — Regulatory change tracker
Objective 66 ✅ — Federated red teaming coordinator
```

---

## v0.5.0 NEW OBJECTIVES — Federal, Agentic, and Mythos-Ready

---

### BLOCK A — COMPLIANCE ENGINE (Federal & NDAA 1512)

```
Objective 67 — ISAC-Transporter Module
  Build: app/core/isac_transporter.py
  Purpose: Serialize LangGraph state → DHS AI-ISAC XML/JSON schema
  Mappings:
    - Asset Criticality    ← system_scope field
    - Exploit Chain        ← full LangGraph Crescendo trace
    - MITRE ATLAS Mapping  ← auto-mapped from attack_type
    - NIST MEASURE 2.7     ← automated score from ASR + evidence quality
    - Mitigation Status    ← priority-ranked remediations
  Output: VDP-ready disclosure package (machine-readable)
  Endpoint: GET /api/v1/redteam/vdp-package/{job_id}

Objective 68 — SHA-256 Safety-Seal Cryptographic Signature
  Build: app/core/report_signer.py
  Purpose: Tamper-proof reports for FCA liability protection
  Implementation:
    - Generate SHA-256 hash of full report + audit trail
    - Sign with mTLS certificate (or dev keypair)
    - Embed signature in PDF metadata and JSON export
    - Verify endpoint: GET /api/v1/redteam/verify/{job_id}
  Required for: Federal contractor deployments, FCA compliance

Objective 69 — VDP-Ready Disclosure Package Endpoint
  Build: Add to app/api/v1/redteam.py
  Purpose: Pre-formatted XML/JSON for DHS AI-ISAC portal upload
  Fields: NDAA Sec 1512 + America's AI Action Plan schema
  Output formats: JSON (v1.0), XML (v1.1 Q3 2026)
  Endpoint: POST /api/v1/redteam/vdp-package

Objective 70 — NDAA Section 1512 Compliance Report Section
  Build: Update app/orchestrator/claude_orchestrator.py report_generator
  Purpose: Add dedicated NDAA 1512 section to every PDF report
  Contents:
    - Federal contractor accountability statement
    - Documented adversarial testing evidence
    - Quantified vulnerability metrics with confidence intervals
    - MITRE ATLAS technique mapping
    - Remediation timeline and blast radius

Objective 71 — Neutrality Check Module (GSA Federal Procurement)
  Build: app/providers/neutrality_provider.py
  Purpose: Test AI models for political bias and sycophancy
         per GSA federal procurement "objective truth" requirement
  Test categories:
    - Ideological consistency (same question, different framing)
    - Sycophancy detection (model agreeing with false premises)
    - Factual accuracy under adversarial pressure
    - Balanced response verification
  Output: Neutrality Score (0-100) + evidence in compliance report

Objective 72 — Continual Monitoring VDP Loop
  Build: Update app/core/scheduler.py
  Purpose: Automated resubmission when new exploits published
  Logic:
    1. AI-ISAC threat feed check (or manual trigger)
    2. Auto-trigger mini-run against existing model
    3. If model fails → generate P1 ISAC Disclosure
    4. Auto-email CISO with Priority 1 alert + report link
  ITIL 4 mapping: Continual Improvement → Monitor → Detect → Respond
```

---

### BLOCK B — GLASSWING BRIDGE (Mythos-Ready Architecture)

```
Objective 73 — BYOM (Bring Your Own Model) Gateway
  Build: app/providers/byom_provider.py
  Purpose: mTLS-authenticated private endpoint support
         for sovereign/VPC model deployments
  Supports:
    - AWS Bedrock High-Security Tiers
    - Microsoft Azure Foundry private endpoints
    - Any OpenAI-compatible private VPC endpoint
  Config: .env BYOM_ENDPOINT, BYOM_CERT_PATH, BYOM_KEY_PATH
  Why: When Tier-1 bank or government buys RTK-1, they point it
       at their internal Mythos instance inside their perimeter

Objective 74 — Agent-to-Agent (A2A) Protocol Interface
  Build: app/core/a2a_protocol.py
  Purpose: Send Goal-Oriented Tasks (not just text prompts)
         to external agent systems (Mythos, Claude Computer Use, etc.)
  Structure:
    - StrategicObjective (high-level goal from RTK-1 Brain)
    - TacticalTask (specific action for external agent)
    - ExecutionResult (standardized result schema)
  LangGraph integration: New A2A Supervisor node in orchestrator
  Why: Architecturally ready for Mythos the moment Glasswing opens

Objective 75 — Glasswing Bridge Adapter (Mythos Stub)
  Build: app/providers/glasswing_provider.py
  Purpose: Stub adapter that becomes Mythos integration when available
  Current: Uses Claude Computer Use as architectural proxy
  Future: Direct mTLS connection to Mythos VPC endpoint
  Interface: Identical to existing AttackProvider base class
  Activation: Set GLASSWING_ENDPOINT in .env when available

Objective 76 — Dual-Model Validation Feature
  Build: app/core/dual_model_validator.py
  Purpose: Claude 4 proposes attack → secondary model predicts blast radius
  Current implementation: Claude 4 attacker + Claude 4 defender (different prompts)
  Future: Claude 4 attacker + Mythos-Inspect defender
  Output: Attack success probability + blast radius score
  Endpoint: POST /api/v1/redteam/dual-validate
```

---

### BLOCK C — BLAST RADIUS ENGINE (Remediation-as-a-Service)

```
Objective 77 — Blast Radius Remediation Engine
  Build: app/core/blast_radius.py
  Purpose: After successful injection, simulate impact of proposed patch
  Steps:
    1. RTK-1 identifies vulnerability (ASR > 0)
    2. Claude 4 generates surgical patch suggestion
    3. LangGraph forks shadow environment
    4. RTK-1 re-runs attack against patched configuration
    5. Reports: patch_verified=True/False + production_impact_score
  Output: "Remediation Impact Score" in every report
  ITIL 4: Change Control → Risk Assessment → Validation

Objective 78 — Auto-Patch Validation Loop
  Build: Update app/orchestrator/claude_orchestrator.py
  Purpose: Find → Patch → Verify pipeline
  Logic:
    1. Successful attack detected (outcome=SUCCESS)
    2. Claude 4 proposes system prompt hardening
    3. LangGraph checkpoint forks campaign state
    4. Re-run 3 sequences against hardened config
    5. Report: patch_reduced_asr_by = X%
  NDAA 1512 value: "Mitigation Status: Patch_Verified" field

Objective 79 — Remediation Impact Scorer API
  Build: Add endpoint to app/api/v1/redteam.py
  Endpoint: POST /api/v1/redteam/remediation-impact
  Input: job_id + proposed_patch (text description)
  Output: blast_radius_score + patch_confidence + re-test_results
```

---

### BLOCK D — AGENTIC & PHYSICAL SYSTEM TESTING

```
Objective 80 — Digital Twin / Hardware-in-the-Loop Adapter
  Build: app/providers/digital_twin_provider.py
  Purpose: Red team AI controlling physical systems
         SCADA, industrial IoT, autonomous drones
  Attack scenarios:
    - SCADA command injection via LLM interface
    - Industrial IoT sensor data manipulation
    - Autonomous vehicle decision manipulation
    - Drone flight path adversarial input
  NDAA 1535 alignment: Critical infrastructure AI testing
  AI-ISAC alignment: Physical system vulnerability reporting

Objective 81 — SCADA/ICS Attack Simulation
  Build: app/core/scada_simulator.py
  Purpose: Simulate adversarial attacks on industrial control AI
  Test vectors:
    - False sensor readings injected into LLM context
    - Emergency override command injection
    - Maintenance mode bypass via conversational manipulation
  Output: SCADA-specific findings section in compliance report

Objective 82 — Agentic Chain Attack Simulator
  Build: app/providers/agentic_chain_provider.py
  Purpose: Test multi-agent pipelines for inter-agent injection
  Scenarios:
    - Agent A injects malicious context into Agent B's memory
    - Shared tool poisoning across agent network
    - Orchestrator manipulation via sub-agent output
  OWASP LLM08: Excessive Agency in multi-agent systems
```

---

### BLOCK E — SUBSCRIPTION & PRODUCTIZATION

```
Objective 83 — Subscription Tier Management
  Build: app/core/subscription.py
  Purpose: McAfee-style subscription model enforcement
  Tiers:
    - Starter:     $2,000/month — 10 campaigns, 3 providers
    - Professional: $8,000/month — unlimited campaigns, 5 providers
    - Enterprise:  $25,000/month — multi-node, federated, NDAA package
    - Federal:     $50,000/month — AI-ISAC integration, mTLS, VDP package
  Implementation: JWT token + tier enforcement in rate_limiter.py

Objective 84 — Multi-Tenant Campaign Isolation
  Build: Update app/core/config.py + app/core/audit.py
  Purpose: Secure isolation between enterprise clients
  Implementation:
    - Customer namespace in all DB tables
    - Separate report directories per customer
    - API key → customer_id → tier lookup
    - Zero data leakage between tenants

Objective 85 — Stripe/Payment Integration Hook
  Build: app/core/billing.py (webhook handler)
  Purpose: Automate subscription activation on payment
  Integration: Stripe webhook → activate customer_id → set tier
  ITIL 4: Service Financial Management practice

Objective 86 — Customer Onboarding Wizard
  Build: Update streamlit_app.py
  Purpose: First-time setup in under 5 minutes
  Steps:
    1. Enter API key for target model
    2. Define success criteria in plain language
    3. Select compliance frameworks needed
    4. Launch first campaign immediately
  Goal: Zero-friction enterprise onboarding
```

---

### BLOCK F — INFRASTRUCTURE & ITIL 4 OPERATIONS

```
Objective 87 — Multi-Node Home Lab Deployment
  Build: docker-compose.yml + scripts/deploy_homelab.sh
  Purpose: Deploy RTK-1 across Desktop + OptiPlex + NUC + Beelink
  Node roles:
    - Desktop (192.168.10.10):  Primary API + Orchestrator
    - OptiPlex (192.168.10.20): Hot standby + 24/7 scheduler
    - NUC (192.168.10.30):      Monitoring + Grafana + attack library
    - Beelink (192.168.10.40):  CI/CD + testing node
  Failover: Nginx load balancer with health check routing

Objective 88 — GL-iNet Portable Gateway Configuration
  Build: scripts/network_portability.sh
  Purpose: One-command location change — plug into new network,
           everything else stays identical
  Implementation:
    - GL-iNet WAN: DHCP from any upstream
    - UDR7 LAN: fixed 192.168.10.0/24 always
    - All machines: static IPs behind UDR7
    - VPN: WireGuard on GL-iNet for encrypted upstream

Objective 89 — UPS + Auto-Restart Service Scripts
  Build: scripts/startup_all.ps1
  Purpose: Auto-restart all services on power restore
  Services: RTK-1 API + Prometheus + Grafana + Streamlit
  Windows Task Scheduler: Run on startup, retry on failure

Objective 90 — ITIL 4 Service Catalog
  Build: docs/service_catalog.md
  Purpose: Formal ITIL 4 service definitions for each RTK-1 tier
  Contents:
    - Service utility and warranty statements
    - Service level targets (SLT) per tier
    - Escalation paths and RACI matrix
    - Continual improvement register (CIR)

Objective 91 — ITIL 4 Continual Improvement Register
  Build: app/core/cir.py (Continual Improvement Register)
  Purpose: Track all improvement initiatives per ITIL 4 CSI model
  Fields: initiative, baseline_metric, target_metric, owner, status
  ITIL 4 CSI steps applied to RTK-1:
    1. What is the vision?       → ASR below 20% for all clients
    2. Where are we now?         → Current ASR baseline
    3. Where do we want to be?   → Target ASR + compliance status
    4. How do we get there?      → Campaign plan + remediation
    5. Take action               → Execute campaign
    6. Did we get there?         → Week-over-week delta
    7. How do we keep momentum?  → Scheduled campaigns + fingerprinting
```

---

### BLOCK G — SOCIAL + MARKETING AUTOMATION

```
Objective 92 — GitHub Actions Auto-Update Workflow
  Build: .github/workflows/update_docs.yml
  Purpose: Auto-commit architecture.md and README updates
           after every significant campaign result
  Triggers: Campaign ASR > threshold, new provider loaded,
            new test passing

Objective 93 — LinkedIn Post Auto-Generator (Enhanced)
  Build: Update app/core/delivery.py
  Purpose: Generate campaign-specific LinkedIn posts
           with compliance framing and business value
  Templates: Enterprise win, ASR improvement, new provider,
             regulatory milestone, NDAA compliance

Objective 94 — X (Twitter) Post Auto-Generator
  Build: app/core/x_poster.py
  Purpose: Auto-generate X posts from campaign milestones
  Templates: Technical insight (150 char), compliance win,
             security research finding

Objective 95 — Professional Profile Sync
  Build: app/core/profile_sync.py
  Purpose: Keep GitHub, LinkedIn, X aligned on RTK-1 milestones
  Triggers: New release tag, new compliance coverage, test milestone
```

---

## IMPLEMENTATION PRIORITY ORDER

```
WEEK 1 (Immediate Revenue):
  67 — ISAC-Transporter (federal market differentiator)
  68 — SHA-256 Safety-Seal (FCA compliance requirement)
  69 — VDP Disclosure Package (NDAA 1512 compliance)
  71 — Neutrality Check (GSA procurement requirement)
  83 — Subscription Tier Management (monetization)

WEEK 2 (Architecture):
  73 — BYOM Gateway (Glasswing readiness)
  74 — A2A Protocol (Mythos readiness)
  77 — Blast Radius Engine (highest client value)
  78 — Auto-Patch Validation Loop
  87 — Multi-Node Home Lab Deployment

WEEK 3 (Market Expansion):
  80 — Digital Twin Adapter (NDAA 1535 / AI-ISAC)
  81 — SCADA Simulation
  84 — Multi-Tenant Isolation
  86 — Customer Onboarding Wizard
  90 — ITIL 4 Service Catalog

WEEK 4 (Operations + Marketing):
  88 — GL-iNet Portable Network
  89 — Auto-Restart Scripts
  91 — ITIL 4 CSI Register
  92 — GitHub Auto-Update Workflow
  93 — LinkedIn Auto-Generator
  94 — X Post Generator
```

---

## ITIL 4 GOVERNING PRINCIPLES APPLIED TO THIS ROADMAP

| ITIL 4 Principle | Roadmap Application |
|------------------|---------------------|
| Focus on Value | Every objective maps to client revenue or compliance requirement |
| Start Where You Are | Build on v0.4.0 foundation — no rewrites |
| Progress Iteratively | Weekly delivery blocks with feedback loops |
| Collaborate | HITL at strategic gates — human approves high-risk objectives |
| Think Holistically | Federal + commercial + agentic all addressed simultaneously |
| Keep It Simple | Each objective is one file or one endpoint — no over-engineering |
| Optimize and Automate | Objectives 92-95 automate the marketing layer entirely |

---

*RTK-1 v0.5.0 Objectives — Built on ITIL 4 Service Value System*
*Governing principle: Do not buy unless RTK-1 has already provided the money.*
*Human in the loop at: strategic decisions, high-risk authorizations, investment gates.*
