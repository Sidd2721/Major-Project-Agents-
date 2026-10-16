# Project Assumptions & Constraints

This document records architectural, operational, and scope assumptions adopted during the "Stabilize & Explain" phase of SmartOps AI.

## 1. Scope & System Boundaries
- **Email & Invoice Agents**: Explicitly OUT OF SCOPE for this semester per approved project presentation slides. They are categorized as "Planned (Semester 2)" across all documentation. No stub code or fake endpoints are created for them.
- **Three Active Systems**:
  1. Customer Support Agent (`:8000` API, `:5173` Customer Portal, `:5174` Employee Dashboard, background worker)
  2. Sales Outreach Agent (`:5175` Web Dashboard & CLI)
  3. Voice Agent (`:8765` WebSocket / HTTP server & Browser Simulation)
- **Central Hub**: Unified management portal served on port `:8080`.

## 2. Environment & Network Resilience
- **Offline First**: All frontend assets, fonts, and styles rely on local files or system font stacks (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`). No external CDN links (e.g. Tailwind CDN, Google Fonts) are required at runtime.
- **LLM Mode Hierarchy**:
  - `LLM_MODE=live`: Attempts configured provider (Groq primary, Gemini secondary).
  - `LLM_MODE=mock`: Returns fast, realistic, deterministic triage results, qualification scores, and answers without touching external networks or consuming quotas.
  - `LLM_MODE=replay`: Serves disk-cached runs (e.g. pre-generated qualified/unqualified sales pipeline outputs).
- **Authentication**:
  - Customer complaint form is public.
  - Employee dashboard, sales pipeline trigger, and reset endpoints are protected by simple admin credentials (`ADMIN_KEY` or HTTP Basic).

## 3. Data & Storage
- **Customer Support**: SQLite database (`complaints.db`).
- **Sales Outreach**: Local JSON/Markdown reports in `reports/` and local ChromaDB vector store.
- **Voice Agent**: In-memory and read-only cross-agent context snapshots pulled from SQLite DB and Sales report directories.
