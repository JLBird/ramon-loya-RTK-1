# CLAUDE.md — RTK Security Labs · Ramon Loya

> **Persistent context for all Claude sessions.** Read fully before any technical or business work. Start every session with: Daily Risk Audit → pytest green → then work.
>
> **Last compiled:** April 22, 2026 | **Platform:** RTK-1 v0.5.0 | **Status:** 95/95 objectives · 20/20 pytest green · pre-revenue

---

## 1. PROJECT OVERVIEW

### Identity
- **Founder:** Ramon J. Loya — sole founder, operating solo. Claude is the primary technical and business collaborator (operate as partner, not tool — push back when wrong).
- **Entity:** RTK Security Labs, DBA sole proprietorship, Guadalupe County (Seguin), TX
- **Address:** 233 Pecan Estates, New Braunfels TX 78130 · **Phone:** 512-577-1347
- **Credentials:** ITIL 4 Foundation (87.5%, Feb 2026), 64% through B.S. Cybersecurity (WGU), bilingual EN/ES

### Product
RTK-1 — **Autonomous AI Red Teaming Platform**. Equivalent of a 15-person specialized red team delivered as a managed service. Not a toolkit — a compliance archive with switching cost moat. Automates 85–90% of a manual engagement that typically costs $75K–$150K over 6 weeks; RTK-1 delivers in under 12 minutes.

### Phase
Pre-revenue. **Hard financial deadline: ~May 15, 2026** (unemployment benefits end). Every decision weighed against: income-generating vs platform-protecting.

### Canonical URLs
| Item | URL |
|---|---|
| GitHub repo | `JLBird/ramon-loya-RTK-1` |
| Website | `jlbird.github.io/ramon-loya-RTK-1` |
| Sample report | `jlbird.github.io/ramon-loya-RTK-1/sample-report.html` |
| Domain (Cloudflare) | `rtksecuritylabs.com` |
| Contact form (mailto: bypass) | `forms.gle/JBKYsLRmxictTA837` |
| X handle | `@RTKSec` |
| Primary email | `ramon@rtksecuritylabs.com` |

---

## 2. TECH STACK

| Layer | Technology | Purpose / Reason |
|---|---|---|
| LLM orchestrator | Claude Sonnet 4.6 (`claude-sonnet-4-20250514`) | Best reasoning for ReAct eval loop |
| Agent framework | LangGraph | Stateful graph, checkpointing, HITL native |
| Attack engine | PyRIT 0.12.0 | Crescendo multi-turn + SelfAskTrueFalseScorer |
| API layer | FastAPI + uvicorn | Async, auto-OpenAPI at `/docs`, 26 endpoints |
| Self-service portal | Streamlit | 5-page non-technical client portal |
| Metrics | Prometheus | Scrape endpoint at `/metrics` |
| Dashboards | Grafana | RTK-1 Executive Dashboard, live ASR gauge |
| Logs | Loki v3.7.1 + Grafana Alloy | Structured JSON log pipeline |
| Logging library | `structlog` | Log aggregation into Loki |
| Rate limiting | SQLite (sliding window) | Per-customer tenant isolation |
| Report signing | SHA-256 HMAC | Compliance archive switching cost moat |
| Social — X | Tweepy OAuth 1.0a | Only auth that works for posting |
| Social — LinkedIn | UGC Posts API v2, `/v2/userinfo` | `/v2/me` = 403 on new apps |
| PDF reports | ReportLab + pypdf | Signed compliance PDFs |
| Testing | pytest | 20/20 green baseline, mandatory before/after every session |
| Secrets | python-dotenv + pathlib explicit load | Terminal env injection is disabled |
| Pages | GitHub Pages from `/docs` folder | `update_docs.yml` renamed `.bak` |
| IP protection | DTSA (18 U.S.C. § 1836) + TX UTSA (§ 134A) | In every SOW |

### Attack Providers (13 total)
```
pyrit           — Crescendo multi-turn (LLM01, MITRE ATLAS AML.T0054)
garak 0.14.1    — 100+ probe-based failure modes (LLM06)
deepteam        — LLM-as-attacker (fallback=True when not installed)
promptfoo       — CI/CD deterministic gate (cp1252 encoding fail on Windows = non-blocking)
crewai          — Multi-agent attack crews
rag_injection   — RAG poisoning (LLM02 Indirect Injection)
tool_abuse      — Unauthorized tool execution (LLM08 Excessive Agency)
multi_vector    — Parallel pyrit + rag_injection + tool_abuse
neutrality      — GSA federal bias/sycophancy scoring
byom            — Bring your own model
glasswing       — Behavioral fingerprint, semantic drift week-over-week
digital_twin    — SCADA/ICS/OT (NDAA Section 1535)
agentic_chain   — Cross-agent boundary injection (LLM08 + AML.T0043)
```

### Ports (all local)
| Service | Port |
|---|---|
| FastAPI API | 8000 |
| Streamlit portal | 8501 |
| Prometheus | 9090 |
| Grafana | 3000 |
| Loki | 3100 |
| Grafana Alloy | 12345 |

---

## 3. ARCHITECTURE DECISIONS (LOCKED)

### Orchestration Graph
```
Recon → Planner → Supervisor (eval-driven) → Executor → Evaluator → Report
                       ↓
                  HITL Node (Slack notification + audit log, never bypass in prod)
```
- **Supervisor = LLM judge**, not rule-based if/else. Evaluates current state + "is this attack successful yet?" and selects tool dynamically.
- All external calls wrapped with `tenacity` retry.
- Per-customer rate limiting: sliding window SQLite.
- Behavioral fingerprinting: 7 canonical probes.
- Semantic drift monitoring: week-over-week ASR baseline.
- Regulatory change tracker: EU AI Act / NIST.
- Attack graph visualization: Mermaid.

### Domain Model Boundary (non-negotiable)
- **Only `AttackResult` (and other canonical domain models) cross the facade → orchestrator boundary.** No raw provider dicts ever.
- Canonical types in `app/domain/models.py`: `AttackResult`, `AttackVector`, `CampaignConfig`, `OrchestratorResult`, `IssueAnalysis`.
- Providers return raw results → Facade converts → Orchestrator consumes typed models.

### Facade Pattern
- `RTKFacade` is the single swappable entry point. Providers injected at constructor — never hardcoded.
- Hides all wrapper details (PyRIT, Garak, promptfoo, etc.).
- Returns `OrchestratorResult` → state transition in LangGraph.

### Strategy Pattern
Each provider implements the common `BaseProvider` interface. Orchestrator selects provider dynamically based on state ("this scenario needs Garak" vs "this needs PyRIT") — never scripted sequence.

### `main.py` Rule
Keep it intentionally minimal: imports, lifespan, middleware, router includes, `/health`. Zero business logic.

### C1/C2 Binary Execution Gate (proprietary differentiator)
```
C1 — No unauthorized execution occurred (observable outcome)
C2 — No executable path existed without valid proof (architectural enforcement)
     If C2 holds, C1 is guaranteed. C2 is the stronger claim and always the headline.
```
No other platform uses this framing. Every report leads with the binary verdict — never ASR%, never risk ratings. This is trade-secret protected.

### Endpoints
- **26 total** (25 redteam + 1 health)
- **Demo endpoints:** `POST /api/v1/redteam/ci` · `POST /api/v1/redteam/crescendo`

### Delivery Layer
PDF (SHA-256 signed) · VDP Package (JSON v1.0 + XML v1.1) · Executive Email · Slide Deck · LinkedIn Post · X Post · Grafana Dashboard · Loki Logs · Slack Alert · GitHub Auto-Docs.

---

## 4. FILE & DIRECTORY STRUCTURE

```
C:\Projects\RTK-1\ramon-loya-RTK-1\
├── app/
│   ├── main.py                      # Intentionally minimal — routers + middleware only
│   ├── facade.py                    # RTKFacade — swappable provider entry point
│   ├── schemas.py                   # Pydantic request/response models
│   ├── api/v1/redteam.py            # All 26 endpoints
│   ├── core/
│   │   ├── config.py                # pydantic_settings (load_dotenv MUST run before this imports)
│   │   ├── logging.py               # structlog setup + file sink for Loki
│   │   ├── metrics.py               # Prometheus metrics
│   │   ├── social_automation.py     # X + LinkedIn auto-posting
│   │   ├── billing.py               # Stripe integration
│   │   ├── delivery.py              # PDF report generation
│   │   ├── scheduler.py             # 24/7 autonomous campaign scheduler
│   │   ├── scoring.py               # SelfAskTrueFalseScorer + deterministic
│   │   ├── rate_limiter.py          # Sliding window SQLite
│   │   ├── semantic_drift.py        # Week-over-week ASR comparison
│   │   ├── alerts.py                # Slack HITL notifications
│   │   ├── regulatory.py            # EU AI Act / NIST change tracker
│   │   ├── attack_graph.py          # Mermaid visualization
│   │   ├── fingerprint.py           # 7 canonical behavioral probes
│   │   ├── isac_transporter.py     # VDP package generation (NDAA 1512)
│   │   └── report_signer.py         # SHA-256 HMAC report signing
│   ├── providers/                   # 13 attack providers (base.py + 13 implementations)
│   ├── orchestrator/
│   │   └── claude_orchestrator.py   # ReAct eval-driven supervisor
│   └── domain/
│       ├── models.py                # AttackResult, OrchestratorResult, etc.
│       └── engagement.py
├── docs/                            # GitHub Pages source — ALL public assets here
│   ├── index.html                   # 482-line mobile-first site
│   ├── sample-report.html           # 575-line live report (canonical)
│   └── sample-report.pdf            # Legacy binary — kept for reference
├── tests/test_integration.py        # 20 tests, must all pass
├── reports/                         # Generated campaign reports
├── logs/                            # rtk1.log (Alloy tails this)
├── .github/workflows/
│   └── update_docs.yml.bak          # DISABLED — was overwriting index.html on push
├── venv_rtk/                        # Virtual environment (NOT .venv, NOT venv)
├── .env                             # NEVER commit — all secrets
├── rtk1_audit.db                    # ITIL audit log (gitignored)
├── rtk1_campaigns.db                # Campaign history (gitignored)
├── pyproject.toml
├── requirements.txt
└── CLAUDE.md                        # This file
```

---

## 5. CODING PATTERNS & STANDARDS

### 5.1 `load_dotenv` — THE most important pattern
Terminal environment injection is disabled. `load_dotenv` is NOT called automatically. It must be called explicitly at the top of every script, with `pathlib` relative resolution, **before any import that reads env vars** (especially `from app.core.config import settings` — settings initializes on import and silently captures `None` values if env isn't loaded first).

```python
from pathlib import Path
from dotenv import load_dotenv

_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_ENV_PATH, override=True)

# Only AFTER load_dotenv:
from app.core.config import settings
```

**Terminal one-liner fallback:**
```python
from dotenv import load_dotenv
load_dotenv('C:/Projects/RTK-1/ramon-loya-RTK-1/.env', override=True)
```

**Verify keys loaded:**
```powershell
python -c "
from dotenv import load_dotenv; import os
load_dotenv('C:/Projects/RTK-1/ramon-loya-RTK-1/.env', override=True)
print('ANTHROPIC_API_KEY:', os.getenv('ANTHROPIC_API_KEY','MISSING')[:8])
print('X_API_KEY:', os.getenv('X_API_KEY','MISSING')[:10])
print('LINKEDIN_ACCESS_TOKEN:', os.getenv('LINKEDIN_ACCESS_TOKEN','MISSING')[:10])
"
```

### 5.2 Environment Variable Names (exact)
```
X_API_KEY / X_API_SECRET / X_ACCESS_TOKEN / X_ACCESS_SECRET    ← NOT TWITTER_*
LINKEDIN_ACCESS_TOKEN        ← single line, no wrapping, regenerate every ~60 days
LINKEDIN_CLIENT_ID / LINKEDIN_CLIENT_SECRET
ANTHROPIC_API_KEY
```

### 5.3 JSON Fence Stripping (all 4 orchestrator LLM calls)
```python
import re, json
def strip_json_fences(text: str) -> str:
    return re.sub(r"```(?:json)?\s*|\s*```", "", text).strip()
data = json.loads(strip_json_fences(raw))
```

### 5.4 Tenacity Retry (all external calls)
```python
import tenacity

@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
async def call_external(): ...
```

### 5.5 FastAPI Lifespan Pattern
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(asyncio.to_thread(start_http_server, 8001))
    await scheduler.start()
    yield
    await scheduler.stop()
```

### 5.6 Logger Pattern (use everywhere)
```python
from app.core.logging import get_logger
logger = get_logger("component_name")
logger.info("event_name", key=value, key2=value2)
logger.error("event_name", error=str(e))
```

### 5.7 Provider Pattern
```python
from app.providers.base import BaseProvider

class MyProvider(BaseProvider):
    async def run(self, config: dict) -> dict:
        # Returns: {success, asr, sequences, findings, duration}
        ...
```

### 5.8 API Endpoint Pattern
```python
@router.post("/redteam/my_endpoint")
async def my_endpoint(request: MyRequest) -> MyResponse:
    try:
        result = await some_provider.run(request.dict())
        return MyResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 5.9 Supervisor JSON Schema
```json
{
  "next_action": "run_attack | generate_report | human_approval | end_campaign",
  "reasoning": "short explanation",
  "confidence": 0.0,
  "recommended_tool": "pyrit | garak | null"
}
```
Validate against `SupervisorDecision` Pydantic schema before routing. Never route on raw string output.

### 5.10 HITL Node Pattern
```python
if state.hitl_required and not state.hitl_approved:
    await alerter.send_slack_notification(...)
    await audit.log(AuditEventType.HITL_REQUIRED, ...)
    return state  # Halt until human approval endpoint is called
```
Never block indefinitely — configure timeout + auto-continue window.

### 5.11 Report Structure (binary verdict leads — always)
```
Section 1: BINARY VERDICT — C1/C2 pass/fail (not ASR%)
Section 2: Phase 1 Baseline — undefended execution paths, ASR, attack traces
Section 3: Phase 2 Validation — C1/C2 per sequence
Section 4: Delta Analysis
Section 5: Compliance Mapping — EU AI Act, NIST AI RMF, OWASP LLM Top 10, MITRE ATLAS
Section 6: Remediation Recommendations
```

### 5.12 ReportLab (PDF) Rules
- Never use `Helvetica-Bold-Oblique` → use `Helvetica-Oblique` (the first crashes)
- Never use Unicode subscript/superscript → use `<sub>` / `<super>` XML tags
- Never name a loop variable `path` when the function param is also `path` — causes `FileNotFoundError` misinterpretation (`for method, ep_path, desc in endpoints:`)
- Always use `io.BytesIO()` buffer before writing to disk
- Encrypt with `pypdf` AFTER building, not during: `writer.encrypt(user_password="", owner_password="RTKSecLabs2026!OwnerOnly", use_128bit=True)`
- Orange callout box for sample report link = the consistent signature element
- Footer: `RTK-1 v0.5.0 · 95/95 objectives · 20/20 tests passing · rtksecuritylabs.com`

### 5.13 DOCX Rules (node.js `docx` package)
```javascript
const sp = (b=0,a=0) => ({spacing:{before:b,after:a}});
const p  = (runs,opts={}) => new Paragraph({...opts,children:Array.isArray(runs)?runs:[runs]});
const t  = (text,opts={}) => new TextRun({text,font:"Calibri",...opts});
```
- Never use unicode bullets — always use numbering config with `\u2013`
- Page: US Letter `{width:12240,height:15840}`, margins `{top:756,right:1008,bottom:756,left:1008}` — docx-js defaults to A4
- Tables: set both table `width` AND each cell `width`; `columnWidths` must sum to table width
- `ShadingType.CLEAR` — NOT `ShadingType.SOLID` (SOLID creates black backgrounds)
- Avoid duplicate closing brackets — copy-paste JS syntax errors are the #1 build failure

### 5.14 Brand Color Palette (resumes + docs — consistent)
```javascript
const DARK   = "0A0A0A";  // body text
const ORANGE = "C84E00";  // RTK Security Labs brand accent
const SLATE  = "1E293B";  // section headers
const MIST   = "F1F5F9";  // section backgrounds
const WHITE  = "FFFFFF";  // ATS ghost text
const MED    = "334155";  // medium text
const LIGHT  = "64748B";  // light/italic
```

### 5.15 Social Automation — Circular Import Fix
`app/core/logging.py` shadows Python's stdlib `logging`. Running scripts directly causes circular import.
```powershell
$env:PYTHONPATH = "C:\Projects\RTK-1\ramon-loya-RTK-1"
python -m app.core.social_automation    # Correct
# NEVER: python app/core/social_automation.py
```

### 5.16 LinkedIn Posting
```python
# CRITICAL: Use /v2/userinfo NOT /v2/me
# CRITICAL: NO X-Restli-Protocol-Version header on userinfo
headers = {"Authorization": f"Bearer {access_token}"}
profile = httpx.get("https://api.linkedin.com/v2/userinfo", headers=headers)
author_urn = f"urn:li:person:{profile.json()['sub']}"

payload = {
    "author": author_urn,
    "lifecycleState": "PUBLISHED",
    "specificContent": {"com.linkedin.ugc.ShareContent": {
        "shareCommentary": {"text": post_text},
        "shareMediaCategory": "NONE"
    }},
    "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
}
resp = httpx.post("https://api.linkedin.com/v2/ugcPosts",
    headers={**headers, "X-Restli-Protocol-Version": "2.0.0",
             "Content-Type": "application/json"},
    json=payload)
```
Required scopes: `w_member_social`, `profile`, `openid`.

### 5.17 GitHub Pages Rules
- Pages serves from `/docs` folder only — never change this, never switch to root (breaks site)
- `update_docs.yml` renamed to `update_docs.yml.bak` — DO NOT re-enable without scoping it to exclude `docs/index.html`
- Cloudflare email obfuscation silently replaces `mailto:` with `/cdn-cgi/l/email-protection#...` — use Google Form `forms.gle/JBKYsLRmxictTA837` for all contact buttons
- Windows UTF-8/CRLF corrupts special characters in HTML written via PowerShell — use ASCII-only (no em dashes, no arrows, no curly quotes, no checkmarks)
- File size sanity check: new `index.html` should be ~37KB+; smaller = wrong file deployed
- Commit file directly inside `/docs` via "Create new file" — NOT drag-and-drop upload (path ambiguity)
- Hard refresh `Ctrl+Shift+R` to bypass browser cache after Pages rebuild

---

## 6. STARTUP & TEST COMMANDS

```powershell
# Change to project
cd C:\Projects\RTK-1\ramon-loya-RTK-1

# Activate venv (name is venv_rtk — NOT .venv, NOT venv)
.\venv_rtk\Scripts\Activate.ps1
# If PowerShell blocks: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Start API (entry is app.main:app — bare `main:app` fails)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
# Confirm: browser → localhost:8000/docs — 25 redteam + 1 health = 26 endpoints visible

# Run tests (MUST be green before AND after every technical session)
python -m pytest tests/test_integration.py -v --tb=short
# Expected: 20 passed in ~0.54s

# Run social automation
python -m app.core.social_automation

# Git commit pattern
git add .
git commit -m "feat|fix|docs: description — keyword"
git push

# Check GitHub Pages deployment
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/JLBird/ramon-loya-RTK-1/main/docs/index.html" -OutFile "C:\temp\deployed.html"
(Get-Item "C:\temp\deployed.html").Length

# Start Loki (leave terminal open)
cd C:\loki
.\loki-windows-amd64.exe --config.file=loki-config.yaml   # NOTE: double dash

# Restart Alloy
Restart-Service -Name "Alloy"
```

**Harmless startup warnings (always ignore):**
- `GLib-GIO-WARNING` — Windows UWP noise
- `PyTorch not found` — PyRIT optional dependency
- `UnicodeDecodeError: 'charmap' codec can't decode byte 0x8f` — promptfoo Windows cp1252, non-blocking
- `promptfoo_load_failed` / `deepteam_not_installed_using_llm_fallback` — expected fallbacks

---

## 7. INFRASTRUCTURE CONFIGS

### Loki v3.7.1 — `C:\loki\loki-config.yaml`
```yaml
auth_enabled: false
server:
  http_listen_port: 3100
schema_config:
  configs:
    - from: 2024-01-01
      store: tsdb                  # v3.x uses tsdb, NOT boltdb-shipper
      object_store: filesystem
      schema: v13                  # v3.x uses v13, NOT v11
      index:
        prefix: index_
        period: 24h
storage_config:
  tsdb_shipper:
    active_index_directory: C:/loki/data/index
    cache_location: C:/loki/data/cache
  filesystem:
    directory: C:/loki/data/chunks
compactor:
  working_directory: C:/loki/data/compactor
```
**Start:** `.\loki-windows-amd64.exe --config.file=loki-config.yaml` (double dash)

### Grafana Alloy — `C:\Program Files\GrafanaLabs\Alloy\config.alloy`
Tails `C:\Projects\RTK-1\ramon-loya-RTK-1\logs\*.log` → Loki at `http://localhost:3100/loki/api/v1/push`. Alloy UI: `http://localhost:12345`. Promtail removed in Loki v3.x — use Alloy.

### Grafana
Datasource: Connections → Data sources → Add → Loki → URL `http://localhost:3100` → Save & test. Look for "Data source connected and labels found."

---

## 8. ITIL 4 PRE-SESSION RITUAL (MANDATORY BEFORE EVERY CLIENT CALL)

**All five must be green — no exceptions. Log any failure as an ITIL Incident immediately.**

```
[ ] 1. pytest 20/20 green
[ ] 2. uvicorn running on :8000
[ ] 3. Browser confirms localhost:8000/docs loads full endpoint catalog
[ ] 4. Zoom audio/mic test passes
[ ] 5. Zoom video confirmed (BRIO 100 rendering, Auto-framing OFF)
```

### Hardware Setup
**Audio (Arctis Nova Pro + GameDAC Gen 2):**
- GameDAC MUST be connected via USB (not 3.5mm analog — mic routes through USB only)
- GameDAC hardware mute button MUST be physically unmuted (even if Sonar shows active)
- Sonar Device Manager: all four channels (GAME, CHAT, AUX, MIC) must have a device assigned — red `⚠ Select a device...` = nothing routes
- Windows Sound Settings: Output `SteelSeries Sonar - Chat`, Input `SteelSeries Sonar - Microphone`, all other SteelSeries = "Don't allow"
- Zoom: explicitly select `SteelSeries Sonar - Microphone` (NOT "Same as system")

**Webcam (BRIO 100):**
- Disable **Auto-framing** in Zoom Video settings (causes excessive zoom)
- If laptop built-in webcam fails (Code 45 hardware): external USB camera clipped to laptop top — Zoom picks it up automatically

**Screen share:**
- `Alt+S` → select Chrome WINDOW (not tab — switching tabs switches what client sees) → uncheck "Optimize for video clip"
- Show Swagger UI and Streamlit only — NEVER show source code, architecture diagrams, provider logic

### Laptop Power (CRITICAL for demos)
- Sleep: **NEVER** · Display off: **NEVER** · Windows Update: **Pause 35 days** (re-pause after every unpause)
- Budget 20–30 min prep buffer — Windows Update can fire mid-prep
- Zoom Basic = 40-min limit → have PMR `745 085 1745` ready to restart instantly

---

## 9. DEMO PATH (CLIENT CALLS)

**Phase 1 — Undefended baseline (ASR must read HIGH):**
```json
POST /api/v1/redteam/crescendo
{"target_model": "claude-sonnet-4-20250514",
 "goal": "test A2SPA authorization gates",
 "attack_type": "crescendo"}
```

**Phase 2 — A2SPA active (ASR drops LOW):**
```json
POST /api/v1/redteam/ci
{"target_model": "claude-sonnet-4-20250514",
 "goal": "trigger unauthorized tool execution without valid A2SPA proof token",
 "providers": ["tool_abuse"],
 "max_prompts": 3}
```

**Full multi-vector (if deeper demo requested):**
```json
{"target_model": "claude-sonnet-4-20250514",
 "goal": "bypass A2SPA cryptographic execution gate across agentic chain",
 "providers": ["tool_abuse", "rag_injection"],
 "max_prompts": 5}
```

### Demo Narrative
> "This is Phase 1 — your agent undefended. Watch the ASR. Phase 2 is the same attack with A2SPA active. **The delta between these two numbers is your proof of value.**"

### ASR Framing (CRITICAL)
- If demo target = Claude, ASR may read 0% (Claude's own safety training). Do NOT mention demo target was Claude unless directly asked.
- Real engagements need the client's undefended/sandboxed agent for Phase 1 to show HIGH ASR.
- The **delta between Phase 1 and Phase 2** IS the product. Never show a low Phase 1 — the narrative collapses.

### The Close (memorize verbatim)
> "Can I send you the deposit invoice right now while we're on the call?"

Then stop. Silence. Wait. Do not add words.

### The Ending (one sentence)
> "I'll let you go. You have the invoice in your inbox. Campaign starts the moment it clears."

Then wait for them to say goodbye first.

---

## 10. BUSINESS POSITIONING — PRICING (NEVER DISCOUNT)

| Tier | Price | Notes |
|---|---|---|
| Starter | **$25,000 flat** | Point-in-time, 1–3 providers |
| Professional | **$41,667/mo** ($500K/yr) | All 13 providers, weekly reports |
| Enterprise | **$83,333/mo** ($1M/yr) | Full platform + VDP packages |
| Federal/Sovereign | **$250,000/mo** ($3M/yr) | NDAA compliance + SCADA testing |

- **Minimum engagement:** $25K point-in-time / **$500K/yr** retainer
- **Payment:** 50% deposit (binding acceptance — no separate signature) / 50% on delivery via Stripe
- **Target:** 3–5 enterprise retainers = $1.5M–$5M/yr
- **Framing always:** "A 15-person red team runs $75K–$150K for a 6-week engagement. RTK-1 delivers equivalent output in under 12 minutes for $25K." Lead with the team equivalent — not the number.
- **Never discount.** Floor is $25K. The first number said sets the relationship's financial frame forever.
- **Delivery sequencing flexibility OK** (e.g., $12,500 deposit → Phase 1 → $12,500 balance → Phase 2+3) — total price never adjusts.
- **Report "tweaking"** = presentation + narrative only. NEVER ASR numbers, test results, or C1/C2 verdicts. The verdict is what it is.

### MRR Thresholds
| MRR | Status |
|---|---|
| $0 | **Maximum existential risk — current state** |
| $41,667/mo | **SURVIVAL** — healthcare activates here |
| $83,333/mo | **STABILITY** — Hill Country land + Jeep |
| $250,000/mo | **LIFESTYLE FREEDOM** |

### Healthcare Rule
**Healthcare = first use of revenue after first retainer signs.** Not optional. Non-negotiable. Uninsured founder = existential risk.

---

## 11. DAILY OPERATING PRINCIPLES (NON-NEGOTIABLE)

### Daily Rhythm (until MRR hits $41,667, every day including weekends)
1. **Bible + prayer + fitness FIRST** — non-conditional
2. **Daily Risk Audit** (5 min) — top risk + one mitigation action
3. `pytest tests/ -v` — must stay green; fix before anything else
4. Confirm `uvicorn` running at `localhost:8000/docs`
5. **BLOCK 1 (90 min) — Upwork:** 5 proposals minimum, sample report link in every one
6. **BLOCK 2 (90 min) — W-2 Applications:** 5/day, resume + cover letter + sample report link
7. **10 AM – 1 PM writing block is SACRED** — protect it
8. **BLOCK 3 (60 min) — RTK-1 Build:** one focused task, pytest after every change
9. **BLOCK 4 (45 min) — Visibility:** LinkedIn post Tue/Thu, 5 CISO DMs, X check, 10 cold pitches
10. **End-of-day close:** log activity, update risk audit, draft tomorrow's article outline

### Non-Negotiable Rules
1. **1hr selling per 1hr building** until MRR hits $41,667
2. **3 active pipeline conversations minimum** at all times — if below 3, next action = open a new one (not build)
3. **pytest green before AND after** every technical session — report count explicitly
4. **Never discount** — not even for first clients
5. **Never stop pipeline outreach** even when fully engaged with a client
6. **Stripe → Chase connection verified** before every engagement
7. **Healthcare = first-use-of-revenue** after retainer #1
8. **Jonathan = SILENCE until October 15, 2026** — do not contact, do not rely on for survival math
9. **Sample report link** embedded in every resume, every pitch, every email

### Daily Risk Audit Template
```
DATE: [today]
MRR: $[current] / $41,667 survival threshold
BENEFITS REMAINING: [days]
TOP FINANCIAL RISK: [one sentence]
TOP TECHNICAL RISK: [one sentence]
#1 ACTION (income-generating): [specific action]
#2 ACTION (platform-protecting): [specific action]
PIPELINE STATUS: [X] of 3 required active conversations
PYTEST STATUS: [GREEN/RED]
YESTERDAY'S MITIGATION: [done/partial/blocked]
```

### ITIL 4 Failure Loop (every session)
**Identify top risk → Assess impact → Mitigate → Execute → Review**

### ITIL 4 Framework Applied to RTK-1
- **Continual Improvement Model** → eval-driven supervisor loop (not willpower-dependent)
- **Service Value Chain** → RTK-1 deliver & support layer
- **Value co-creation** → customer-defined scope drives every campaign design
- **Utility** = what RTK-1 does (adversarial testing) / **Warranty** = how it performs (signed reports)

---

## 12. COMPETITIVE MOAT — 8 PILLARS

1. **Quarterly ASR benchmark archive** — historical data competitors cannot manufacture. Publish quarterly "State of LLM Security" report.
2. **Binary C1/C2 execution gate verdict** — no toolkit uses this framing. Procurement-committee language. Trade-secret protected.
3. **EU AI Act Article 15 first mover** — enforcement August 2, 2026. Only autonomous platform mapping attacks to Article 15 explicitly.
4. **Federal co-marketing pipeline** — Jonathan Capriola (A2SPA/Middle East banking) + KK Mookhey (SOC2/ISO27001/HIPAA federal).
5. **Managed service = compliance archive switching cost** — 6 months of trend data makes leaving expensive.
6. **Agentic AI specialization** — ~2 years ahead of toolkit market. CrewAI + LangGraph multi-agent attack infrastructure.
7. **Continuous monitoring lock-in** — 6 months of signed reports = institutionally irreplaceable. Trend data IS the product.
8. **Usage-metered cost protection** *(NEW — April 2026)* — Claude Enterprise moved to metered billing. Insecure agents trigger runaway API costs. RTK-1 = the security gate before the meter runs.

---

## 13. EXISTENTIAL RISKS & COUNTERS

| Risk | Mitigation |
|---|---|
| Toolkit commoditization (PyRIT/Garak/promptfoo go mainstream) | ASR archive + managed service switching cost + agentic specialization 2yr ahead |
| Cloning / IP theft | DTSA + TX UTSA in every SOW. C1/C2 framework is trade-secret protected. |
| Zero MRR | 1hr selling per 1hr building. 5 Upwork + 5 W-2 applications/day. 10 cold pitches/day. |
| Single client dependency | 3 pipeline conversations minimum at all times |
| Health crisis without insurance | Healthcare = first-use-of-revenue after retainer #1 |
| Technical failure during demo | pytest before every session, ITIL 4 pre-call ritual |
| Underpricing / discounting | Fixed pricing, sample report is the justification |
| Scope creep | Written SOW + ITIL service catalog; change orders billed separately |
| Platform dependency (Anthropic) | Multi-provider facade already built; provider-agnostic |
| Invisibility | 2+ LinkedIn posts/week using SEO keyword set |
| API cost overrun | Budget $50–100/engagement, monitor Anthropic credits |

### IP Protection Clause (paste into EVERY SOW)
> "All methodologies, attack sequences, scoring algorithms, orchestration logic, provider architecture, report framework, and deliverables produced by RTK Security Labs (Ramon Loya, sole proprietor, Guadalupe County, Texas) are proprietary trade secrets protected under the Defend Trade Secrets Act (18 U.S.C. § 1836) and the Texas Uniform Trade Secrets Act (Tex. Civ. Prac. & Rem. Code § 134A)."

**Never show source code** on demos. Only Swagger UI + Streamlit output. Capabilities PDF withheld until post-deposit.

---

## 14. COMPLIANCE FRAMEWORK MAPPINGS

Every RTK-1 campaign maps findings to:
- **EU AI Act** — Articles 9, 14, 15, Annex IV (**Article 15 = primary first-mover claim**)
- **NIST AI RMF 1.0** — GOVERN / MAP / MEASURE 2.4+2.7 / MANAGE (RTK-1 covers MEASURE and MANAGE)
- **OWASP LLM Top 10** — LLM01 (Prompt Injection), LLM02 (RAG Injection), LLM06 (Disclosure), LLM08 (Excessive Agency / Tool Abuse)
- **MITRE ATLAS** — AML.T0054 (Crescendo), AML.T0051, AML.T0043
- **NDAA Section 1512** — DHS AI-ISAC VDP packages (JSON v1.0 + XML v1.1)
- **NDAA Section 1535** — SCADA/OT critical infrastructure AI
- **FCA AI guidelines** — SHA-256 HMAC report signing
- **GSA federal procurement** — Neutrality Check endpoint (political bias, sycophancy, factual accuracy)

Reports are **SHA-256 signed PDFs**. The signature IS the compliance archive switching cost moat.

---

## 15. SEO KEYWORDS (use 2–3 per post/article/update)

- **Primary:** "AI red teaming" · "LLM security testing" · "EU AI Act compliance" · "autonomous red teaming"
- **Secondary:** "prompt injection testing" · "AI safety validation" · "NIST AI RMF compliance" · "OWASP LLM Top 10"
- **Long-tail:** "automated AI red teaming platform" · "EU AI Act Article 15 tool" · "continuous LLM adversarial testing"

---

## 16. PIPELINE & KEY CONTACTS

### Protected — DO NOT CONTACT
**Jonathan Capriola** — `Jon@aiblockchainventures.com` · AI Blockchain Ventures / AImodularity.com · Sarasota FL (EST) · A2SPA Protocol inventor · closed major Middle East bank deal · **follow-up October 15, 2026 ONLY** · three Stripe invoices staged · $25K–$250K expected · **excluded from survival math**. A2SPA-invested banks closed deals without compliance reports → RTK-1 is the mandatory compliance monitoring layer. Zoom PMR: `745 085 1745`.

### Tier 1 — Call Confirmed
**Jose Ruiz-Vazquez** — `joseruiz1571@gmail.com` · ISO 42001 Lead Auditor, Healthcare-Privacy-GRC-Toolkit builder (Claude Code + HIPAA) · Monday 10 AM CT call · his tool (AI vendor risk assessment / governance) is **COMPLEMENTARY, not competitive** — RTK-1 = execution layer, his = governance layer. Frame: peer-to-peer, explore co-sell.

### Tier 2 — Active Thread
| Contact | Context | Status |
|---|---|---|
| **Neeraj Kumar Singh B.** | Security infra for $8B+ fintech, ex-Meta/JPM/Wayfair | One more exchange then DM for call. NHI runtime gap. |
| **Jeremie Strand** | Co-Founder SkillSafe.AI (confidence layer for autonomous agents) | Liked 8+ posts in 22 min (research signal). DM sent. Mutual: Mike Takahashi. |
| **KK Mookhey** | Shasta / transilienceai (SOC2/ISO27001/HIPAA toolkit) | "AI Red Teaming on Whitney roadmap" — warm co-marketing. Federal. |

### Tier 3 — Warming
| Contact | Context | Status |
|---|---|---|
| **Dr. Anil Lamba** | VP Cyber & Tech Risk, JPMorgan (CISSP/CISM, 269 papers) | 2018 paper explicitly calls for "periodic automated penetration testing" = RTK-1 verbatim. 30 days substantive comments → DM offering free platform access for case study. DO NOT name RTK-1 in comments yet. |
| **Kyle Polley** | Security @ Perplexity (just went SOC 2 Type II) | Connection request sent |
| **Jacques Longa Bissay** | Chugach Government Solutions LLC (federal) | Connected, "Absolutely" reply |
| **Raza Sharif** | CybersecAI, 7 MCP CVEs, CISSP | Connected |
| **Ben Crenshaw** | CLEAR AI Initiative | Connection accepted |
| **Simar Girn** | Booz Allen Hamilton AI Red Teaming | Connection sent |
| **Mohammad Alshaggah** | Cybersecurity + Red Team Ops | Connection sent |
| **Sonu Kapoor** | Microsoft MVP, OWASP, CVE Lite CLI | In network |
| **Devi Devs** (`@Devi_Devs`) | ML governance/testing | Warm X reply to RTK-1 post |
| **Alan Aqrawi** | Accenture Sr Mgr, multi-agentic red team, Harvard AI/ML | Accept connection |
| **Amada Echeverría** | LangChain Community + Startups | Connected. RTK-1 on LangGraph = ecosystem angle. Interrupt26 SF May 13-14. |
| **Damaris** | Personal contact, construction co. owner | Sales PDF ready |

**Non-negotiable: 3 active pipeline conversations at all times. Below 3 → next action is opening a new one.**

### Declined / Gated
- **Palo Alto Networks Technology Partner** — DECLINED April 20, 2026. Requires 3 validated customers in PANW sales opportunities. Contact: `mrichmond@paloaltonetworks.com`. Re-apply post-first 3 paying clients. Target integration: RTK-1 + Prisma AIRS (AIRS = AI-SPM / what's in stack; RTK-1 = adversarial validation / proves it holds).

### Freelance / Platform Status
| Platform | Status |
|---|---|
| Upwork | Active, Membership Plus $9.99/mo. Floor $150/hr. 2 proposals out (Supabase $4,500, bench partner, AI article $500 Mode B only). |
| nDash | Pending verification (15–20 days, est. May 12–21) |
| Contently | Setup in progress |
| Toptal | Pending at `ramon.it.career@gmail.com` — **DO NOT DISTURB** |
| Commission Crowd | On hold until first income (insufficient funds) |
| weremote.com | Queued post-first-income |
| Scale AI | 7 applications 4/17/26 → **90-day lockout until ~July 17, 2026** |

---

## 17. BUSINESS INFRASTRUCTURE

| Item | Detail |
|---|---|
| Entity | RTK Security Labs, DBA sole proprietorship, Guadalupe County TX |
| Business checking | Chase ••••0879 / routing 111000614 |
| Stripe | Live mode, weekly Monday payouts, migrated to `ramon@rtksecuritylabs.com` ✅ |
| Domain | `rtksecuritylabs.com` (Cloudflare, CNAME `@` → `jlbird.github.io` proxied orange) |
| Google Workspace | Live ✅ (MX/SPF/DKIM/DMARC live) |
| LinkedIn | Updated to business email ✅ |
| OWASP | Member, recovering account; channels: `#project-top10-for-llm`, `#team-llm-discuss`, `#project-genai-security` |
| Palo Alto Partner | DECLINED 4/20 — re-apply post-3-clients |
| Wire | Chase routing 111000614, account ••••0879. Domestic same-day. Intl SWIFT 1–3 biz days. |

### Email Identity (CRITICAL — do not confuse)
| Account | Role | Status |
|---|---|---|
| `ramon@rtksecuritylabs.com` | **PRIMARY business — all future comms** | Active |
| `ramon.it.career@gmail.com` | Legacy — winding down | **Toptal + OWASP original pending here — DO NOT DISTURB** |
| `rmnloya@gmail.com` | Personal — passive | Keep lean |

**Migration queue (Cloudflare ALWAYS first — daily change limit hit):**
Cloudflare → Anthropic billing → OWASP → Ubiquiti → Buffer → CommissionCrowd → Upwork → Gmail forwarding (legacy → business)

**Stripe OAuth disconnect lesson:** Before disconnecting Google OAuth on any service, confirm password + authenticator app both work. Stripe → already migrated ✅.

### Online Image Cleanup (queued)
- **Deactivate job boards:** Indeed, ZipRecruiter, Lensa/Lensa24, Glassdoor, Talent.com
- **Data broker opt-outs:** Spokeo, Whitepages, BeenVerified
- **LinkedIn:** Remove any job-seeker-era content conflicting with founder narrative

### Writing Rate Ladder (current freelance strategy)
- Week 1–2: $0.50/word floor → Week 3: $0.75/word → Month 2: $1.00/word → Month 3+: $1.50/word
- Whitepaper: $1,500 flat · Hourly: $150/hr

### Sales Force Architecture (planned)
- 1099 independent reps, 20hr/week commitment, commission-only
- Base commission: **10% of contract value**, rep share 40–50% of base, paid direct-deposit day payment clears Stripe
- Each rep: sandboxed Claude account + Streamlit portal instance only — NO access to API, methodology, source
- **FSRS spaced repetition training** — onboard with 10 things they love; Claude builds personalized RTK-1 training through those lenses
- **Customer Definition of Value portal** (Claude-backed chatbot) = core infrastructure — ITIL 4 value co-creation is the literal OS
- DTSA protection in every rep agreement
- Active recruitment: Damaris PDF ready; Gadiel PDF queued week 2

---

## 18. HOMELAB

| Machine | Specs | Role |
|---|---|---|
| Desktop | Ryzen 7700X, RTX 3090, 64GB, Proxmox | RTK-1 primary (post-first-income migration) |
| OptiPlex 5080 Micro | 64GB, Proxmox | A2SPA target agent VM (for Palo Alto integration) |
| Intel NUC 7i5 | 32GB, Ubuntu Server | Monitoring stack (Prom/Grafana/Loki) |
| Beelink SER3 | Ryzen 3750H | Auxiliary |
| Dell Inspiron 16 Plus | 16GB | **CURRENT RTK-1 host — do not migrate until first income** |

**Network:** Spectrum 575/22Mbps · UDR7 10GbE · GL-iNet GL-MT3000 portable gateway · CAT8  
**Proxmox UI:** `https://192.168.100.2:8006` (note `https://` not `http://`, port `:8006` not `:8000`, **colon not slash**)  
**Tailscale:** Planned for remote laptop → desktop sync, post-first-income.

**Version mismatch lesson:** Always verify router registrations in `app/main.py`, not just `pyproject.toml` version — desktop container once had v0.3.0 main.py while version string said 0.5.0. Container port conflict fix: `pct exec 100 -- fuser -k 8000/tcp && sleep 2 && pct exec 100 -- systemctl restart rtk1-api`.

---

## 19. 25 BILLABLE SERVICE OFFERINGS (Upwork / Toptal / Commission Crowd)

Each RTK-1 endpoint = a standalone billable engagement at $25K floor:

1. Crescendo attack campaign + executive report
2. CI/CD gate integration for AI pipelines
3. ASR trend analysis over time
4. Campaign history audit
5. ASR delta comparison (before/after security controls)
6. Multi-model comparison testing
7. Multi-vector attack simulation
8. Delivery bundle — full compliance package
9. Weekly security summary report
10. Monthly compliance report
11. Rate limit + abuse threshold testing
12. Agentic sales pipeline security audit
13. VDP package creation
14. Signed + verified report delivery
15. Remediation impact assessment
16. Neutrality + bias check
17. Dual validation (independent verification)
18. Subscription-based continuous monitoring
19. ITIL CIR dashboard access
20. ITIL change incident reporting
21. RAG injection testing
22. Tool abuse simulation
23. Prompt injection campaign
24. EU AI Act Article 15 compliance assessment
25. OWASP LLM Top 10 coverage report

---

## 20. RESUME & DELIVERABLE STANDARDS

- **Font:** Calibri throughout
- **Page:** US Letter (12240×15840 DXA), margins 756 top/bottom, 1008 left/right
- **Header:** two-column table (name/tagline left, contact right)
- **ATS ghost strip:** white text size 8, after header divider; keywords always include: AI red teaming, LLM security testing, EU AI Act compliance, autonomous red teaming, prompt injection, NIST AI RMF
- **Section headers:** single-row table, MIST background, SLATE text, letter-spacing 50
- **Bullets:** numbering config with `\u2013` (em dash) — never unicode bullet chars
- **JD alignment table** ("JD REQUIREMENT" vs "RAMON'S DIRECT PROOF") — always include for targeted resumes
- **Cover letters:** ReportLab PDF, orange callout box for sample report link, clickable hyperlink via `<link href="...">` in Paragraph
- **Sample report link** embedded in every resume, every pitch, every email — no exceptions
- **When producing docs:** DOCX + PDF both, always
- **Social posts:** X and LinkedIn versions every time, ready-to-copy

---

## 21. WRITING VOICE RULES (all RTK-1 / Ramon content)

1. **Short declarative sentences.** Never more than 20 words when making a key claim.
2. **The magician doesn't explain the trick.** Authority comes from conviction, not credentials.
3. **Remove political framing** — global buyers (EU, Middle East, APAC). No Trump / America First references.
4. **Remove speculative references** — no Musk AGI timelines, no biblical "left behind" framing in technical articles.
5. **Replace Reddit/drowning imagery** with forum/career-narrowing framing for practitioner articles.
6. **ITIL 4 thread is always available** — use for consistency, process, continuous improvement framing.
7. **C1/C2 framing is proprietary** — always use it, never explain it away.
8. **85% automation, 15% human creativity** — Ramon's role is creative director, not developer.
9. **"It never tires. It never gets distracted."** — core RTK-1 value proposition sentence. Protect it.
10. **LinkedIn captions end on a single punchy line** — never a CTA paragraph.

---

## 22. KEY GOTCHAS & LESSONS LEARNED

### Python / Environment
- `venv_rtk` is the venv name — **NOT** `.venv`, **NOT** `venv`. Verify with `Get-ChildItem` if unsure.
- `load_dotenv()` does NOT auto-load — always explicit pathlib path, override=True, BEFORE settings import
- Use `pathlib.Path(__file__).resolve().parents[N]` for relative resolution — never hardcoded absolute paths in shared code
- `pip install` needs `--break-system-packages` in this environment
- Bare `uvicorn` may miss module path → use `python -m uvicorn app.main:app`
- Uvicorn entry is `app.main:app` — NOT `main:app` (throws ModuleNotFoundError)
- `app/core/logging.py` shadows stdlib `logging` → always run scripts as `python -m app.core.foo`, never directly
- `TWITTER_API_KEY` is WRONG — use `X_API_KEY`
- `LINKEDIN_ACCESS_TOKEN` must be single line in `.env` (multi-line = silent 401 / auth failure)
- LinkedIn token expires ~60 days — regenerate, required scopes: `w_member_social` + `profile` + `openid`
- LinkedIn `/v2/me` returns 403 on new apps → use `/v2/userinfo` (no `X-Restli-Protocol-Version` header on userinfo)
- Cursor IDE truncates long files → use F1 → "Find and Replace" for surgical edits
- Cursor terminal injection disabled — all env vars need explicit load

### GitHub Pages / Deployment
- `update_docs.yml` silently overwrites `index.html` → renamed `.bak`, **never re-enable**
- Pages serves from `/docs` only — never root
- "Create new file" in `/docs`, not drag-and-drop upload (path ambiguity)
- Wait 60–90s after commit for Pages rebuild; `Ctrl+Shift+R` hard refresh
- CDN caches aggressively — wait for Actions green checkmark before testing
- Sample report URL canonical: `jlbird.github.io/ramon-loya-RTK-1/sample-report.html`
- Google Search Console: use **URL prefix** `https://jlbird.github.io/ramon-loya-RTK-1/`, NOT domain property
- Cloudflare has **daily email-change limit** → migrate Cloudflare FIRST in any session involving email consolidation
- Cloudflare email obfuscation silently replaces `mailto:` with `/cdn-cgi/l/email-protection#...` → Google Form `forms.gle/JBKYsLRmxictTA837` for contacts
- Windows CRLF + UTF-8 = mojibake in HTML written via PowerShell → ASCII-only special chars

### Website / HTML
- CSS `opacity: 0` on `.fade-up` with IntersectionObserver → cards invisible if JS doesn't fire. Default to `opacity: 1; transform: translateY(0)`.
- `--surface: #0D1017` is nearly identical to `--bg: #080A0F` — increase contrast for visible cards
- Any contact button → Google Form, not mailto:

### PowerShell
- `Get-Content | Select-String` fails on binary/unicode — use `-Pattern` carefully
- `Set-Content -Encoding UTF8` to prevent mojibake
- Multi-line regex `-replace` is unreliable → use Python for complex replacements
- `Move-Item` with `.disabled` fails → use `.bak`
- Always `.\` prefix for executables: `.\grafana-server.exe`
- `pytest` alone won't work if venv not activated → `python -m pytest`

### Loki / Observability
- Loki v3.x removes `shared_store` → use `tsdb` + schema `v13`, not `boltdb-shipper` / `v11`
- Loki v3.x CLI: `--config.file` (double dash), not `-config.file`
- Promtail removed in v3.x → use Grafana Alloy

### DOCX / PDF
- `ShadingType.CLEAR` — SOLID creates black backgrounds
- `columnWidths` must sum exactly to table width
- Both table width AND cell width must be set
- `pageBreakBefore:true` on paragraph OR `new PageBreak()` — both work
- #1 build failure: duplicate closing brackets from copy-paste
- ReportLab: never `Helvetica-Bold-Oblique` (crash) → `Helvetica-Oblique`
- ReportLab: never `path` as loop var when it's also a function param
- PDF encryption with pypdf: after build, not during

### Stripe / Billing
- `Linked external accounts` ≠ `Payout accounts` — check both in Stripe Settings
- Payment links must be **archived** (not deactivated) to remove from website
- `Manage payout accounts` ≠ `Add account` in bank settings
- Invoices finalized and left "Open" status is correct — manual send post-call
- "Finalize only" NOT "Finalize and send" — verbal confirm first
- Jonathan's email is `Jon@aiblockchainventures.com` — NOT the shortened version

### Social Automation
- X post fires manually if automation fails — @RTKSec cannot go silent 2+ days
- Circular import fix: `python -m app.core.social_automation` with PYTHONPATH set
- Dry-run test: `python -c "import sys; sys.path.insert(0, '.'); import asyncio; from app.services.social_automation import x_poster; print(asyncio.run(x_poster.generate_and_post('technical_insight', {'asr': 3.2, 'model': 'test'}, dry_run=True)))"`

### Demo / Calls
- Demo ASR=0% is Claude's safety training — NOT A2SPA. Don't mention unless asked.
- Real engagement = client's undefended agent for Phase 1 HIGH ASR
- Zoom Basic 40-min limit — PMR link ready to restart
- Share Chrome **WINDOW** not tab — tab switch = client sees the switch
- Never show Zoom passcode in shared screenshots of invites
- Windows Update mid-prep — 20–30 min buffer required

### Scope Documents
- Never include version numbers visible to client (v1, v2, etc.)
- Payment of deposit = binding acceptance, no separate signature needed
- Report "tweaking" = presentation only, NEVER numbers or verdicts

### Strategy
- Usage-metered Claude Enterprise (April 2026) = new moat pillar — frame RTK-1 as "secure before the meter runs"
- C1/C2 = procurement committee language — lead every report
- Compliance archive switching cost compounds monthly
- Pricing shame is a cognitive trap — $25K vs $75K–$150K manual engagement
- Phase 1 MUST read HIGH ASR — the delta IS the product
- Jonathan's "Sounds good" = implicit October 2026 commitment — protect it

---

## 23. APPLICATION HISTORY

### Scale AI (April 17, 2026 — 90-day lockout active until ~July 17, 2026)
Evals Engineer Applied AI · AI Controls & Monitoring · Frontier Risk Evaluations · Agent Robustness · Lead TPM Trust & Safety · Senior MLE Public Sector · Staff MLRS LLM Evals

### Other Submitted
- Anthropic — Safeguards Enforcement Analyst
- 10a Labs — AI Red Teamer
- HiddenLayer — Post-Sales Solutions Architect

---

## 24. LONG-TERM CREDENTIALING / FEDERAL PATH (post-stability)

1. NIST AI RMF adoption documentation
2. **ISO 42001 certification** — target: register RTK-1 as an ISO 42001 auditor with full audit suite for AI governance, risk management, and regulatory compliance
3. EU notified body recognition
4. AI Auditor status (enables third-party conformity assessment)
5. **SBIR/Federal (July 2026 build block):** DoD SBIR Phase I $50K–$250K · Phase II $750K–$1.5M · aligns with NDAA 1512 AI/robotics hardening
6. **OWASP Q3 2026:** Submit RTK-1 to GenAI Solutions Landscape

Timeline: 12–18 month build.

---

## 25. RTK-1 ENDPOINT → OWASP LLM MAPPING (for pitches)

| Endpoint / Capability | OWASP Tag | Customer Pain Solved |
|---|---|---|
| `POST /api/v1/redteam/ci` | LLM01, LLM02 | "Every deploy might silently regress my safety" |
| `POST /api/v1/redteam/crescendo` | LLM01 | "Single-turn filters don't catch gradual escalation" |
| Mutation Engine | LLM01 | "I don't know what attacks to try" |
| Deterministic Scorer | LLM01/02 | "I need an auditable verdict, not subjective judgment" |
| Rate Limiter | LLM04 | "Can my endpoint be bankrupted by abuse?" |
| Attack Graph (Mermaid) | Cross-cutting | "My board needs to see the attack, not read it" |
| 13-provider coverage | Cross-cutting | "My vendor claims safety but I can't verify across models" |
| C1/C2 Binary Execution Gate | All OWASP LLM | "Vulnerability lists don't tell me whether to ship" |

---

## 26. APPROVED SOCIAL POSTS (rotate and reuse)

### X (@RTKSec) — Usage-Metered Pivot
```
Claude Enterprise just moved to usage-based billing.

Every agentic workflow is now a metered financial instrument.

An insecure AI agent doesn't just create risk — it creates a runaway API bill.

RTK-1 validates your deployment before the meter runs.

C1/C2 binary verdict. 13 attack providers. SHA-256 signed reports.

jlbird.github.io/ramon-loya-RTK-1

#AIredteaming #LLMsecurity #EUAIActcompliance
```

### LinkedIn — Usage-Metered Pivot
```
Anthropic just changed the economics of enterprise AI.

Claude Enterprise moved to usage-based billing this month. Every agent, every workflow, 
every Claude Code session now has a direct cost on your P&L.

An insecure agentic deployment doesn't just expose you to breach risk. 
It exposes you to prompt injection attacks that trigger runaway token consumption.

RTK-1 validates your deployment before it hits production — and monitors it continuously after.

- C1/C2 binary verdict (procurement committee language)
- SHA-256 signed compliance artifacts  
- OWASP LLM Top 10 + NIST AI RMF + EU AI Act Article 15 mapping
- Metered cost risk analysis — we find the attack vectors that burn your budget

The meter is running. Is your AI secured?

RTK Security Labs | rtksecuritylabs.com

#AIredteaming #LLMsecurity #EUAIActcompliance #autonomousredteaming #NISTAIRMFcompliance
```

### Published Content
**Article 1 (LIVE):** *"Why Eval-Driven Supervisors Catch the Bugs Your Scripted Red Team Misses"* — LinkedIn article + X post, ~1,520 words, 6 sections

---

## 27. MILESTONE MAP

| Milestone | Date | Definition |
|---|---|---|
| **SURVIVAL** | May 15, 2026 | W-2 offer OR first freelance contract signed. Benefits end. |
| **STABILITY** | Aug 1, 2026 | $41,667/mo MRR OR $130K+ W-2 + first RTK-1 close. EU AI Act Aug 2 deadline drives urgency. |
| **BREAKTHROUGH** | Oct–Dec 2026 | Quarterly ASR benchmark published. Jonathan A2SPA activates Oct 15. |
| **LIFESTYLE** | 2027+ | $250K/mo. Hill Country land. Jeep. Goats. Time-sovereign. |

---

## 28. LIFE VISION (THE "WHY")

- **Location independence**, **time sovereignty**, **income decoupled from hours worked**
- Hill Country land near Wimberley (~$3,500/mo, home office deductible)
- Jeep Grand Cherokee Summit Reserve (Section 179 — >6,000 lbs GVWR qualifies, deduct full price year 1)
- Nigerian Dwarf or miniature goat herd with full newborn nursery (colostrum protocol, bottle feeding progression, milking station)
- Apartment interim: $550/mo one-bedroom New Braunfels (home office 20–35% deduction)
- **Health, fitness, faith — foundational daily non-negotiables, not lifestyle add-ons**

### Tax Strategy
- Home office deduction: photograph workspace, measure sq ft percentage
- Section 179: Jeep Grand Cherokee qualifies (>6,000 lbs GVWR)
- Schedule C: Claude API credits, homelab, domain, Workspace all deductible
- Confirm with CPA after first retainer clears

### The Core Principle
Every strategic decision evaluated against: *does this move me closer to or further from that life?*

---

## 29. HOW CLAUDE SHOULD OPERATE

- **Always lead with:** Daily Risk Audit before any technical work
- **Deliver:** Complete, copy-paste-ready deliverables — not guidance alone
- **Python:** Always include pathlib `load_dotenv` block at top of any script needing env vars
- **Scope docs:** Always include DTSA + TX UTSA clause
- **Pricing:** Never suggest discounting. Floor is $25K. Reinforce 15-person red team value.
- **Pipeline:** Verify 3 active conversations. If below 3, next action = open a new one.
- **Code changes:** Run pytest before AND after. Report count explicitly.
- **Context priority:** userMemories first, then this file. More specific / more recent wins on conflict.
- **When producing docs:** DOCX + PDF both, always. Social posts: X and LinkedIn versions ready to copy.
- **Flag** when an action conflicts with existential-risk mitigations.
- **Operate as full partner** — push back when something is wrong. Prioritize income-generating actions during the survival window.

---

## 30. TOOL-USE & AGENTIC WORKFLOW RULES

Never exceed **~15 tool calls per turn**. Plan first, then batch actions efficiently. If you approach the per-turn tool-use limit, summarize progress clearly and pause for user confirmation before continuing.

**For complex multi-step tasks:**
1. **Create a step-by-step plan first** — no tools yet
2. **Execute in small batches**
3. **Summarize after every 3–5 tool uses**

**Always prefer fewer, higher-impact tool calls over many small ones.** One well-scoped read beats five exploratory ones; one thorough edit beats ten micro-patches.

---

## 31. NEW-CHAT PROMPT TEMPLATE

```
You are my primary technical and strategic collaborator for RTK Security Labs and RTK-1.
Read userMemories and CLAUDE.md fully before responding.

Today is [DATE].
Session type: [Daily Risk Audit + pipeline / Technical build / Client prep / Business dev / Writing]

Key updates since last session:
- [e.g., "Jose call Monday confirmed"]
- [e.g., "Cloudflare migration completed"]
- [e.g., "New warm lead: [name]"]

Start with Daily Risk Audit. Then address the priority item.

Always hold active:
- Jonathan October 15, 2026 follow-up (SILENCE until then)
- 3-pipeline-minimum rule
- 1 hr selling per 1 hr building until $41,667 MRR
- Healthcare = first use of revenue after retainer #1
- pytest green before/after every technical session
- Never discount — floor $25K
```

---

## 32. PENDING TICKETS

| Ticket | Block | Priority |
|---|---|---|
| Paste 8 new pytest functions → confirm 28/28 | Tonight | HIGH |
| Fix social automation circular import (PYTHONPATH set) | Tonight | HIGH |
| **Fix rtksecuritylabs.com rendering** (DNS + GitHub Pages CNAME + Stripe buttons + sample report link) | Monday AM | HIGH |
| Website: Customer-Defined Value suite (intake portal, pre-load per tier, intelligent orchestrator auto-start RTK-1) | 30-day build | HIGH |
| Sales Recruitment PDF for Gadiel | Week 2 | MEDIUM |
| RTK-1 DoD/NDAA 1512 alignment documentation | Week 3 | MEDIUM |
| SBIR application research + federal positioning | July 2026 | LOW |
| ISO 42001 AI Auditor credentialing path | Post-stability | LOW |
| Email consolidation (Cloudflare FIRST) | Ongoing | LOW |
| Online image cleanup (job boards, data brokers) | Ongoing | LOW |

---

*RTK Security Labs · Ramon Loya · `ramon@rtksecuritylabs.com`*  
*Protected under DTSA (18 U.S.C. § 1836) + TX UTSA (§ 134A). All methodologies are trade secrets. Confidential.*  
*Update this file at the close of every major session.*
