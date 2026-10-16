# SmartOps AI — README

## What Is This?

SmartOps AI is a college Major Project demonstrating three autonomous AI agent systems for enterprise automation.

| System | What it does | URL |
|:---|:---|:---|
| **Customer Support Agent** | Receives complaints, AI-triages sentiment + priority (P1–P4), routes to staff | :5173 · :5174 · :8000 |
| **Sales Outreach Agent** | Researches leads, scores them, generates 9 intelligence reports via 12-node LangGraph pipeline | :5175 |
| **Voice AI Platform** | Two AI personas (Support + Sales) you can talk/type to in your browser | :8765 |
| **Platform Hub** | Overview, status dots, how-it-works, architecture | :8080 |

---

## 5-Minute Quickstart (Windows)

### Prerequisites
- Python 3.11+
- Node.js 20+
- Git

### 1. Clone & Enter
```bash
git clone https://github.com/Sidd2721/Major-Project-Agents-
cd Major-Project-Agents-/smartops-ai
```

### 2. Setup (one command — creates all venvs + npm installs)
```bash
python scripts/setup.py
```

### 3. Add API Keys (or run fully offline)
Edit each `.env` file **OR** skip this and use mock mode (no AI keys needed):
```
# Customer-Support-Agent/.env
GROQ_API_KEY=your_groq_key_here
LLM_MODE=mock        # change to "live" when you have keys

# sales_agent_module/.env
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here
LLM_MODE=mock

# gemini-voice-agent/.env
GEMINI_API_KEY=your_gemini_key_here
GROQ_API_KEY=your_groq_key_here
LLM_MODE=mock
```

### 4. Start Everything
```bash
python scripts/run_all.py
```

### 5. Open Browser
| URL | Page |
|:---|:---|
| http://localhost:8080 | **Platform Hub** ← Start here |
| http://localhost:5173 | Customer complaint form |
| http://localhost:5174 | Employee ticket dashboard |
| http://localhost:8000/docs | API documentation |
| http://localhost:5175 | Sales intelligence dashboard |
| http://localhost:8765 | Voice AI console |

Press `Ctrl+C` to stop all services.

---

## Running Offline (No API Keys)

Set `LLM_MODE=mock` in each `.env`. The system uses deterministic canned responses so demos
work without any API keys. The UI shows a **MOCK** badge.

## Demo Mode

See [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) for the 7-minute guided demo script.

---

## Architecture

```
┌────────────────────────────────────────────────────┐
│              SmartOps AI Platform                   │
│                                                    │
│  Customer Support  │  Sales Outreach  │  Voice AI  │
│  FastAPI + React   │  LangGraph       │  WebSocket │
│  SQLite + Worker   │  ChromaDB RAG    │  2 Personas│
│                                                    │
│              Hub :8080 (this page)                 │
│       LLM: Groq → Gemini → Mock (fallback)         │
└────────────────────────────────────────────────────┘
```

For full architecture diagrams see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## Project Structure

```
smartops-ai/
├── scripts/
│   ├── setup.py      ← create venvs, npm install
│   └── run_all.py    ← start all 6 services
├── hub/
│   └── index.html    ← Platform Hub (:8080)
├── shared/
│   ├── tokens.css    ← design tokens
│   └── nav.js        ← shared navigation bar
├── Customer-Support-Agent/   ← System 1
├── sales_agent_module/       ← System 2
├── gemini-voice-agent/       ← System 3
├── data/                     ← KB, case studies, samples
└── docs/                     ← all documentation
```

---

## What's Planned (Next Semester)

- Email Management Agent — classify/draft replies
- Invoice Agent — OCR, extract, validate, approve
- Unified backend + PostgreSQL + RLS
- Full TypeScript + Tailwind frontend
- See [docs/ROADMAP.md](docs/ROADMAP.md)

---

## Attribution

See [NOTICE.md](NOTICE.md) for upstream project attribution and licenses.

## License

MIT — see [LICENSE](LICENSE)
