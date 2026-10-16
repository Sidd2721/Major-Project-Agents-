# SmartOps AI — Autonomous Multi-Agent Operations Platform

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![LangGraph](https://img.shields.io/badge/LangGraph-StateGraph-FF6F00?logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_RAG-7952FF)](https://www.trychroma.com/)
[![WebSockets](https://img.shields.io/badge/WebSockets-Pipecat_Voice-00d2ff)](https://github.com/pipecat-ai/pipecat)
[![Status](https://img.shields.io/badge/Evaluation-Offline_Certified-16a34a)](#)

> **College Major Project**  
> An enterprise operational intelligence platform uniting three specialized AI agent workflows: **Automated Customer Support Triage**, **B2B Sales Outreach & Prospect Intelligence**, and **Live Data-Grounded Conversational Voice Interaction**.

---

## 🌐 Unified Service & Port Map

| Service | Port / URL | Primary Technology | Core Function |
|---|---|---|---|
| **Central Operations Hub** | [http://localhost:8080](http://localhost:8080) | Vanilla HTML5 / Shared CSS | Platform launchpad, service health monitoring, and system architecture guides |
| **Customer Support Portal** | [http://localhost:5173](http://localhost:5173) | React 18, Vite | Customer self-service ticket submission interface |
| **Employee Support Dashboard** | [http://localhost:5174](http://localhost:5174) | React 18, Vite | Operational dashboard displaying live P1–P4 triaged tickets, sentiment, and response drafts |
| **Customer Support Backend API** | [http://localhost:8000](http://localhost:8000) /docs | FastAPI, SQLite, Pydantic | Ticket ingestion API, asynchronous worker queue, prompt-injection defense |
| **Sales Outreach Assistant** | [http://localhost:5175](http://localhost:5175) | FastAPI, LangGraph, ChromaDB | Prospect research engine, fit scoring, email drafting, call scripts, source verification |
| **Conversational Voice Console** | [http://localhost:8765](http://localhost:8765) | FastAPI, WebSockets, Pipecat | Spoken AI assistance grounded in live database queries (dual personas: Support / Sales) |

---

## 🚀 Quick Start Running Guide

### Option 1: Start All Services (Unified Launcher)
From the repository root or `smartops-ai/`:
```powershell
# 1. Install all dependencies and seed database (first time only)
python scripts/setup.py

# 2. Run all services simultaneously
python scripts/run_all.py

# 3. Run automated verification suite
python scripts/verify.py
```

### Option 2: Run Individual Agents Independently
```powershell
python scripts/run_agent.py support   # Support API :8000 + Worker + Portals :5173/:5174
python scripts/run_agent.py sales     # Sales Outreach Assistant :5175 only
python scripts/run_agent.py voice     # Conversational Voice Agent :8765 only
python scripts/run_agent.py hub       # Central Operations Hub :8080 only
python scripts/run_agent.py all       # All services simultaneously
```

### Option 3: Live Localhost Verification
While services are running, verify live data flows across all 3 agents in 5 seconds:
```powershell
python scripts/test_live_agents.py
```

For full setup documentation, architecture diagrams, and academic viva resources, see the root [README.md](../README.md).

