# Notice & Attribution

SmartOps AI integrates and adapts open-source libraries, patterns, and reference architectures.
This document details third-party components, licenses, and specific adaptations.

## 1. Upstream Components & Frameworks

### Gemini Voice Agent (Browser / WebSocket Voice Simulation)
- **Upstream Project**: [Pipecat AI](https://github.com/pipecat-ai/pipecat) (Pipecat Technologies, Inc.)
- **License**: BSD 2-Clause License
- **Adaptation**:
  - Implemented standalone WebSocket server (`bot.py`) providing bidirectional audio/text pipeline.
  - Adapted for Google Gemini / Groq LLM integration.
  - Custom browser client (`web_client.html`) with Web Speech API synthesis/recognition, live waveform canvas, and text fallback.
  - Added read-only snapshot context injection from Support DB and Sales reports.

### Sales Outreach Agent (Autonomous B2B Pipeline)
- **Upstream Libraries**:
  - [LangGraph / LangChain](https://github.com/langchain-ai/langgraph) (MIT License)
  - [ChromaDB](https://github.com/chroma-core/chroma) (Apache 2.0 License)
- **Written by Project Team**:
  - 12-node state graph defining research, qualification, RAG case-study matching, and email synthesis.
  - Built-in multi-mode orchestration (`live`, `mock`, `replay`).
  - Standalone FastAPI/HTTP web dashboard with live execution logs and report viewers.

### Customer Support Agent (Triage & Ticketing)
- **Upstream Libraries**:
  - [FastAPI](https://github.com/tiangolo/fastapi) (MIT License)
  - [React](https://github.com/facebook/react) (MIT License)
  - [Vite](https://github.com/vitejs/vite) (MIT License)
  - [SQLAlchemy / SQLite](https://www.sqlalchemy.org/) (MIT License)
- **Written by Project Team**:
  - REST API (`api.py`) with complaint submission, status tracking, and protected employee endpoints.
  - Asynchronous polling worker (`main_worker.py`) for automated LLM priority & sentiment triage.
  - React Customer Portal (`:5173`) and Employee Dashboard (`:5174`).
  - Unified design tokens and navigation bar integration.

### Central Demo Hub & Design System
- **Written by Project Team**:
  - Lightweight single-page control hub (`hub/index.html` on `:8080`) with live agent health monitors, architectural flow modals, and glossary tooltips.
  - System font tokens (`shared/tokens.css`) and universal navigation bar (`shared/nav.js`) operating without external CDN dependencies.

## 2. Model Attributions
- **Groq Cloud API**: `llama-3.3-70b-versatile` / `llama-3.1-8b-instant` (Meta Llama 3 Community License)
- **Google Generative AI**: `gemini-1.5-flash` / `gemini-2.0-flash` (Google AI Terms of Service)
- **Mock LLM Fallback**: In-process deterministic heuristic generator (No external API calls or network dependency).
