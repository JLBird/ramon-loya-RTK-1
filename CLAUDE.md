# CLAUDE.md — RTK Security Labs · Ramon Loya
> Primary context file for all Claude sessions. Read this before any technical or business work.
> Last compiled: April 22, 2026

---

## 1. WHO I AM & MISSION

**Ramon Loya** — sole founder, RTK Security Labs (DBA sole proprietorship, Guadalupe County / Seguin, TX).  
**Primary business:** RTK-1, an autonomous AI red teaming platform.  
**Operating mode:** Solo founder. Claude is my primary technical collaborator.  
**Current phase:** Pre-revenue. Hard financial deadline: mid-May 2026 (unemployment benefits end).  
**North Star:** Location independence, time sovereignty, income decoupled from hours worked.

---

## 2. RTK-1 PLATFORM — TECHNICAL STATE

### Version & Status
- **Version:** v0.5.0 — 95/95 objectives complete (100%)
- **Test suite:** 20/20 integration tests (pytest) — must be green before and after every session
- **Equivalent output:** 15 specialized red team professionals running 24/7

### Core Stack
| Component | Choice | Reason |
|-----------|--------|--------|
| LLM Orchestrator | Claude Sonnet 4.6 | Primary intelligence layer |
| Graph Framework | LangGraph | Stateful, checkpointable agentic workflows |
| Attack Framework | PyRIT 0.12.0 | Primary red team attack execution |
| API Layer | FastAPI | Async, production-grade, OpenAPI/Swagger auto-docs |
| Monitoring | Prometheus + Grafana | Real-time ASR gauge, live KPI dashboard |
| Log Aggregation | Loki v3.7.1 + Grafana Alloy | Structured JSON from all providers |
| Portal | Streamlit (port 8501) | Client-facing self-service |
| Signing | SHA-256 | All compliance reports signed |
| Database | SQLite (sliding window) | Per-customer rate limiting |
| Workflow Diagrams | Mermaid | Attack graph visualization |

### Ports
| Service | Port |
|---------|------|
| FastAPI (main API) | 8000 |
| Streamlit portal | 8501 |
| Prometheus | 9090 |
| Grafana | 3000 |
| Loki | 3100 |
| Alloy | 12345 |

### Attack Providers (13 total)
`pyrit`, `garak`, `deepteam`, `promptfoo`, `crewai`, `rag_injection`, `tool_abuse`, `multi_vector` + 5 additional

### Key Endpoints
- `POST /api/v1/redteam/ci` — CI gate (fast, binary verdict)
- `POST /api/v1/redteam/crescendo` — Crescendo multi-turn attack
- `GET /health` — Server health check
- 26 total endpoints (25 redteam + 1 health)

---

## 3. ARCHITECTURE DECISIONS (LOCKED)

### Orchestration Graph
```
Recon → Planner → Supervisor → Executor → Evaluator → Report
```
- **Supervisor node** = eval-driven (LLM judge, not rule-based if/else)
- Supervisor chooses next action based on state + "is this attack successful yet?" evaluation
- All external calls wrapped with **tenacity** retry logic
- HITL node with Slack notification + audit logging

### Domain Model Rule
- The only object that crosses the domain boundary into core services is `AttackResult`
- Raw API responses must be converted to Pydantic models inside the facade before anything else sees them
- Facade is swappable (provider-agnostic) — tools injected at constructor, not hardcoded

### Facade Pattern
- `RTKFacade` hides all raw wrappers (PyRIT, Garak, promptfoo, etc.)
- Returns `OrchestratorResult` → state transition in LangGraph (checkpointable, observable)
- `main.py` stays intentionally minimal — all logic lives in the facade + providers

### Strategy Pattern
- Each provider implements a common interface
- Orchestrator selects provider dynamically based on state ("this scenario needs Garak" vs "this needs PyRIT")

---

## 4. CODING STANDARDS & PATTERNS

### Environment / dotenv (CRITICAL GOTCHA)
```python
# ALWAYS call this explicitly — environment injection is disabled in the terminal
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / '.env', override=True)
```
- Never assume `.env` is auto-loaded
- Use pathlib relative resolution — not hardcoded absolute paths
- Call `load_dotenv` at the top of every standalone Python script

### Virtual Environment
```powershell
# Correct venv name
.\venv_rtk\Scripts\Activate.ps1

# NOT .venv — that one doesn't exist
```

### Starting the API
```powershell
cd C:/Projects/RTK-1/ramon-loya-RTK-1
.\venv_rtk\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Always use `python -m uvicorn` (not bare `uvicorn`) to ensure correct module resolution.

### Running Tests
```powershell
python -m pytest tests/test_integration.py -v
```
Run before AND after every technical session. 20/20 = green baseline.

### JSON / LLM Output Handling
- Always strip markdown fences before parsing LLM output: `text.replace('```json', '').replace('```', '').strip()`
- Apply to all four orchestrator LLM calls

### main.py Philosophy
- Keep it tiny — only imports, lifespan, middleware, router inclusion, and health endpoint
- No business logic in main.py

### FastAPI main.py Pattern
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(asyncio.to_thread(start_http_server, 8001))
    await scheduler.start()
    yield
    await scheduler.stop()
```

---

## 5. FILE & DIRECTORY STRUCTURE

```
C:/Projects/RTK-1/ramon-loya-RTK-1/
├── app/
│   ├── main.py                    # Intentionally minimal
│   ├── api/v1/redteam.py          # All 26 endpoints
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   ├── alerts.py
│   │   ├── audit.py
│   │   ├── history.py
│   │   ├── scheduler.py
│   │   └── social_automation.py   # X + LinkedIn auto-posting
│   └── providers/                 # 13 attack providers
├── tests/
│   └── test_integration.py        # 20 tests, must all pass
├── docs/
│   ├── index.html                 # GitHub Pages website (482 lines)
│   └── sample-report.html         # Live sample report (575 lines)
├── .github/workflows/
│   └── update_docs.yml.bak        # DISABLED — was overwriting index.html on push
├── venv_rtk/                      # Correct venv
├── .env                           # Never commit — all secrets here
└── Objectives.md                  # 95-objective master list
```

### GitHub Pages Deployment Rules
- GitHub Pages serves from `/docs` directory
- `update_docs.yml` was renamed `.bak` — do NOT re-enable without scoping it to exclude `index.html`
- Any push triggers pages rebuild automatically — no manual action needed
- Cloudflare email obfuscation breaks all `mailto:` links on mobile — use Google Form instead

---

## 6. INFRASTRUCTURE & EXTERNAL SERVICES

### GitHub
- Repo: `JLBird/ramon-loya-RTK-1`
- Website: `jlbird.github.io/ramon-loya-RTK-1`
- Sample report: `jlbird.github.io/ramon-loya-RTK-1/sample-report.html`

### Domain & Email
- Domain: `rtksecuritylabs.com` (Cloudflare)
- Primary business email: `ramon@rtksecuritylabs.com`
- Google Form (contact bypass for Cloudflare obfuscation): `forms.gle/JBKYsLRmxictTA837`

### Social Automation (Live)
- **X (@RTKSec):** Tweepy OAuth 1.0a — keys: `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_SECRET`
- **LinkedIn:** UGC Posts API v2 — correct endpoint is `/v2/userinfo` (NOT `/v2/me` — returns 403 on new apps)
- Required LinkedIn OAuth scopes: `w_member_social`, `profile`, `openid`
- LinkedIn access token expires every 60 days — plan for refresh

### Payment & Banking
- Stripe: live mode, weekly Monday payouts, handle `@rtksecuritylabs`
- Chase: account ••••0879, routing 111000614
- Stripe migrated to `ramon@rtksecuritylabs.com`

### Homelab
| Machine | Role | Specs |
|---------|------|-------|
| Desktop (Ryzen 7700X, RTX 3090, 64GB) | RTK-1 primary (post-Jonathan) | Proxmox |
| OptiPlex 5080 Micro (64GB) | A2SPA target agent VM | Proxmox |
| Intel NUC 7i5 (32GB) | Monitoring | Ubuntu Server |
| Dell Inspiron 16 Plus (16GB) | **Current RTK-1 host** | Windows |
| Network | Spectrum 575/22Mbps, UDR7, CAT8 | GL-iNet GL-MT3000 portable gateway |

---

## 7. AUDIO/VIDEO SETUP (FOR CLIENT CALLS)

### Headset: Arctis Nova Pro + GameDAC Gen 2
- GameDAC Gen 2 **must be plugged in via USB** — even if headphones are also wired
- Must be unmuted at the hardware level for Sonar mic routing to work
- In SteelSeries GG (Sonar), all four channels (GAME, CHAT, AUX, MIC) must have a device assigned — if any show "⚠ Select a device..." in red, nothing will route through

### Webcam: BRIO 100
- Disable **Auto-framing** in Zoom settings
- If overly zoomed in, adjust in Zoom camera settings

### Screen Share (Zoom)
- `Alt+S` → select Chrome window → uncheck "Optimize for video clip"

---

## 8. ITIL 4 PRE-SESSION RITUAL (CLIENT CALLS — MANDATORY)

All five must be green before any call starts. Log failures as ITIL Incidents.

1. `pytest tests/test_integration.py` → 20/20 passing
2. `uvicorn app.main:app --host 0.0.0.0 --port 8000` → running
3. Browser confirm `localhost:8000/docs` loads and shows full endpoint catalog
4. Audio/mic test in Zoom (Sonar chat mic routing verified)
5. Video confirm (BRIO 100, Auto-framing off)

---

## 9. DEMO PATH (FOR JONATHAN / CLIENT CALLS)

**Phase 1 (Undefended — ASR should be HIGH):**
```json
POST /api/v1/redteam/crescendo
{"target_model": "claude-sonnet-4-20250514", "goal": "test A2SPA authorization gates", "attack_type": "crescendo"}
```

**Phase 2 (A2SPA Active — ASR should drop LOW):**
```json
POST /api/v1/redteam/ci
{"target_model": "claude-sonnet-4-20250514", "goal": "trigger unauthorized tool execution without valid A2SPA proof token", "providers": ["tool_abuse"], "max_prompts": 3}
```

The ASR delta between Phase 1 and Phase 2 is the proof for procurement committees.

---

## 10. BUSINESS POSITIONING (NEVER DEVIATE)

### Pricing (Never Discount)
| Tier | Price |
|------|-------|
| Starter | $25,000 flat (point-in-time) |
| Professional | $41,667/mo |
| Enterprise | $83,333/mo |
| Federal | $250,000/mo |

Minimum engagement: $25K point-in-time / $500K/yr retainer.  
Target: 3–5 enterprise retainer clients = $1.5M–$5M/yr.

### MRR Thresholds
- $0 = maximum risk
- $41,667 = survival
- $83,333 = stability
- $250,000 = lifestyle freedom

### C1/C2 Binary Verdict
- Never use ambiguous language in reports
- Every engagement produces a binary verdict: C1 (pass) or C2 (fail)
- This framing is unique to RTK-1 — no other toolkit uses it

### 7 Competitive Moat Pillars
1. Quarterly ASR benchmark archive (historical data competitors can't replicate)
2. Binary C1/C2 execution gate verdict
3. EU AI Act Article 15 first mover
4. Federal co-marketing (Jonathan + KK Mookhey)
5. Managed service model = compliance archive switching cost
6. Agentic AI specialization ~2 years ahead of toolkit market
7. Continuous monitoring lock-in — trend data is the product

### Legal Protection
- Include `DTSA + TX UTSA` trade secret language in every scope document

---

## 11. SEO KEYWORDS (ALL CONTENT — 2–3 PER POST)

**Primary:** `AI red teaming`, `LLM security testing`, `EU AI Act compliance`, `autonomous red teaming`  
**Secondary:** `prompt injection testing`, `AI safety validation`, `NIST AI RMF compliance`, `OWASP LLM Top 10`  
**Long-tail:** `automated AI red teaming platform`, `EU AI Act Article 15 tool`, `continuous LLM adversarial testing`

---

## 12. DAILY OPERATING RULES (NON-NEGOTIABLE)

1. **Daily Risk Audit before any technical work** — ITIL loop: Identify risk → Assess → Mitigate → Execute → Review
2. **1hr selling per 1hr building** — until MRR hits $41,667
3. **pytest before and after every technical session** — 20/20 green is the baseline
4. **3 active pipeline conversations minimum at all times**
5. **Healthcare = first use of revenue** after retainer #1 signs
6. **5 job applications per day (including weekends)** — every resume includes the sample report link

---

## 13. PIPELINE & KEY CONTACTS

| Contact | Company | Status | Notes |
|---------|---------|--------|-------|
| Jonathan Capriola | AI Blockchain Ventures / A2SPA Protocol | Follow-up Oct 15, 2026 | Deferred after closing Middle East bank deal. 3 Stripe invoices staged. $25K–$250K expected. **Excluded from survival plan dependency.** |
| KK Mookhey | Shasta / transilienceai | Warm | SOC2/ISO27001/HIPAA toolkit; AI Red Teaming on roadmap. Federal co-marketing opportunity. |
| Raza Sharif | CybersecAI | Connected | CISSP, 7 MCP CVEs |
| Ben Crenshaw | CLEAR AI Initiative | Connected | — |
| Simar Girn | Booz Allen Hamilton | Request sent | AI Red Teaming |
| Sonu Kapoor | Microsoft MVP | In network | CVE Lite CLI, OWASP |
| Devi Devs | X.com | Warm | ML governance/testing tools, replied to RTK-1 post |
| Jeremie Strand | SkillSafe.AI | Messaging | Confidence layer for autonomous agents |

**Email:** `Jon@aiblockchainventures.com`  
**Zoom PMR:** 745 085 1745  
**Close sentence:** *"Can I send you the deposit invoice right now while we're on the call?"*

---

## 14. EMAIL ACCOUNTS (CONSOLIDATION IN PROGRESS)

| Account | Status | Action |
|---------|--------|--------|
| `ramon@rtksecuritylabs.com` | **Primary business — going forward** | All new accounts here |
| `ramon.it.career@gmail.com` | Legacy — winding down | Toptal application pending here — DO NOT DISTURB |
| `rmnloya@gmail.com` | Personal — passive | Keep lean |

**Queued migrations (next session: Cloudflare first):** Cloudflare → Anthropic billing → OWASP → Ubiquiti → Buffer → CommissionCrowd → Upwork  
**Queued:** Gmail forwarding from legacy → business; online profile deactivations (Indeed, ZipRecruiter, Lensa, Glassdoor, Talent.com); data broker opt-outs (Spokeo, Whitepages, BeenVerified)

---

## 15. EXISTENTIAL RISKS & COUNTERS

| Risk | Counter |
|------|---------|
| Toolkit commoditization | ASR archive + managed service switching cost |
| Cloning | DTSA + TX UTSA in every scope |
| Zero MRR | 1hr selling per 1hr building |
| Single client dependency | 3 pipeline conversations minimum |
| Health crisis without insurance | Healthcare first-use-of-revenue |

---

## 16. GOTCHAS & LESSONS LEARNED

| Gotcha | Fix |
|--------|-----|
| `load_dotenv` not auto-called | Always call explicitly with pathlib path |
| LinkedIn `/v2/me` returns 403 on new apps | Use `/v2/userinfo` instead |
| `update_docs.yml` overwrites `index.html` on every push | File is renamed `.bak` — keep it disabled |
| Cloudflare obfuscates all `mailto:` links on mobile | Use Google Form for all contact buttons |
| Bare `uvicorn` may miss module path | Use `python -m uvicorn app.main:app` |
| `.venv` doesn't exist | Correct venv is `venv_rtk` |
| Windows UTF-8/CRLF corrupts special characters in HTML | Use ASCII equivalents (no em dashes, arrows, checkmarks) |
| 20 tests ≠ 95 objectives | 20 = integration test count; 95 = development objective count |
| GitHub Pages serves stale cache | Make a trivial commit to force redeploy; also check Actions tab for competing workflows |
| Sonar shows "⚠ Select a device..." | Must assign physical devices to all four Sonar channels before mic routing works |
| LinkedIn token expires in 60 days | Build auto-refresh or calendar reminder |
| Stripe was on legacy Gmail OAuth | Migrated to `ramon@rtksecuritylabs.com` — confirmed |
| Cloudflare has daily email-change limit | Migrate Cloudflare account email first thing in any session where it's queued |

---

## 17. PREFERRED WORKING STYLE

- Deliver complete, copy-paste-ready code blocks — not just guidance
- Provide click-by-click instructions for platform tasks
- Maintain full strategic context across all decisions
- Flag when an action conflicts with existential risk mitigations
- Always run ITIL loop: Identify top risk → Assess → Mitigate → Execute → Review
- When building documents or resumes: ATS ghost keyword layer, orange accent branding, embedded sample report link in every deliverable
- Never discount. Never anchor low. The platform replaces 15 specialists — price accordingly.

---

## 18. LIFE VISION (STRATEGIC CONTEXT)

Every decision must serve: Hill Country land near Wimberley (home office deductible), Jeep Grand Cherokee Summit Reserve (Section 179), Nigerian Dwarf / miniature goat herd with full nursery and milking station, health and fitness and faith as daily non-negotiables. Business income funds lifestyle — not the other way around.
