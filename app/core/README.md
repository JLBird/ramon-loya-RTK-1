# RTK-1 — Claude Orchestrated AI Red Teaming Toolkit

**Production-grade defensive red-teaming API (Claude 4 + LangGraph)**

Built as a hybrid of:
- Claude as the intelligent central orchestrator (high-level endpoints)
- LangGraph for stateful, reflective, multi-turn attack workflows

**Live Demo** → [http://localhost:8000/docs](http://localhost:8000/docs) (after `python -m uvicorn app.main:app --port 8000`)

![Swagger UI Screenshot](https://github.com/JLBird/ramon-loya-RTK-1/raw/main/docs/screenshots/swagger-health.png)
*(Screenshot of /health and /redteam/crescendo endpoints)*

## Features
- Claude dynamically plans attack chains (crescendo, TAP, single-turn, agent-tool-calling)
- Stateful multi-turn workflows with reflection and checkpoints
- High-level API (`POST /api/v1/redteam/crescendo`, `/tap`, etc.)
- Zero-trust ready (CORS, rate-limiting, prompt guards, mTLS path prepared)
- Clean, modular structure (FastAPI + Pydantic v2)

## Quick Start
```powershell
# 1. Clone & install
git clone https://github.com/JLBird/ramon-loya-RTK-1.git
cd ramon-loya-RTK-1
pip install -e .

# 2. Add your Anthropic key to .env
# 3. Run the API
python -m uvicorn app.main:app --port 8000