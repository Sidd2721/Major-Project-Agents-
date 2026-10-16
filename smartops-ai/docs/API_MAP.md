# SmartOps AI — Discovered API & System Map

This document records the **verified, code-inspected** entry points, routes, ports, environment variables, and package versions across all SmartOps AI subsystems.

## 1. Runtime Environment
- **Operating System**: Windows (tested with PowerShell & cmd)
- **Python Runtime**: Python 3.11.9 (`C:\Users\avadu\AppData\Local\Programs\Python\Python311\python.exe`)
- **Package Managers**: pip, uv (0.11.8), npm (10.x)
- **Default Encoding**: UTF-8 configured explicitly via `sys.stdout.reconfigure(encoding="utf-8")`

---

## 2. Service Endpoints & Real Routes

| Service | Port | Process / Entry Point | Real Routes Discovered |
|---|---|---|---|
| **Central Hub** | `:8080` | `http.server` serving `hub/index.html` | `/`, `/hub.js`, `/hub.css` |
| **Customer Support API** | `:8000` | `uvicorn Backend.api:app` | `POST /complaints`<br>`GET /complaints`<br>`GET /complaints/{id}`<br>`PUT /complaints/{id}`<br>`DELETE /complaints/{id}`<br>`GET /analytics/status`<br>`GET /analytics/priority`<br>`GET /analytics/trends`<br>`GET /health`<br>`GET /api/mode` |
| **Support AI Worker** | N/A | `python main_worker.py` | Background loop polling `complaints` table in `complaints.db` |
| **Customer Portal UI** | `:5173` | `npm run dev` (`Frontend/customer`) | Static SPA (Vite + React) at `http://localhost:5173` |
| **Employee Dashboard UI**| `:5174` | `npm run dev` (`Frontend/employee-dashboard`) | Static SPA (Vite + React) at `http://localhost:5174` |
| **Sales Outreach Dashboard** | `:5175` | `python web_dashboard.py` | `GET /`<br>`GET /api/status`<br>`POST /api/run-pipeline`<br>`GET /api/reports`<br>`GET /api/reports/{id}`<br>`GET /health`<br>`GET /api/mode` |
| **Voice Agent Platform** | `:8765` | `python bot.py` (or `uv run python bot.py`)| `GET /`<br>`GET /api/health`<br>`GET /api/mode`<br>`POST /api/chat`<br>`WS /ws` |

---

## 3. Discovered Model & Version Discrepancies (Audit vs Code)

| Subsystem | Report Claimed Model | Code Found Model | Verified Working Resolution |
|---|---|---|---|
| **Customer Support Agent** | Groq LLaMA 3 | `openai/gpt-oss-120b` (invalid model name on Groq) | `llama-3.3-70b-versatile` / `llama-3.1-8b-instant` / Mock |
| **Sales Outreach Agent** | Groq / Gemini | `qwen/qwen3.8-27b` / `gemini-3.8-flash` (unreleased/invalid) | Dynamic resolution: `llama-3.3-70b-versatile` / `gemini-1.5-flash` / Replay |
| **Voice Agent** | Gemini Multimodal Live | `gemini-3.8-flash`, `gemini-3.5-flash-lite` | `gemini-1.5-flash` / `llama-3.3-70b-versatile` / Heuristic mock |

---

## 4. Environment Variables Mapping

| Environment Variable | Default / Fallback | Subsystem Usage |
|---|---|---|
| `LLM_MODE` | `mock` (`live` \| `mock` \| `replay`) | Shared across all 3 services via `shared/llm_helper.py` |
| `GROQ_API_KEY` | *(empty)* | Customer Support Agent, Sales Agent, Voice Agent |
| `GEMINI_API_KEY` / `GOOGLE_API_KEY` | *(empty)* | Sales Agent, Voice Agent |
| `ADMIN_KEY` / `ADMIN_PASSWORD` | `smartops-admin-2026` | Employee Dashboard API & Sales pipeline triggers |
| `ENABLE_EMAIL_SEND` | `false` | Support & Sales outreach (logs preview to outbox when false) |
| `ENABLE_LINKEDIN_SCRAPE`| `false` | Sales pipeline (avoids rate limits and headless browser crashes) |
| `ALLOWED_ORIGINS` | `http://localhost:5173,5174,5175,8080,8765,8000` | CORS allowlist for FastAPI and WebSockets |
