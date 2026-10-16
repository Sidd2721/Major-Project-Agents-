# SmartOps AI — System Architecture

SmartOps AI unifies three autonomous AI agent subsystems under a single, offline-first orchestration layer.

## 1. System Ecosystem (Context Diagram)

```mermaid
graph TB
    subgraph Browser & Client Tier
        HUB[Central Demo Hub<br/>Port 8080]
        CP[Customer Portal<br/>Port 5173]
        ED[Employee Dashboard<br/>Port 5174]
        SD[Sales Dashboard<br/>Port 5175]
        VC[Voice Simulator Console<br/>Port 8765]
    end

    subgraph Core Services Tier
        API[Customer Support API<br/>FastAPI :8000]
        WORKER[AI Triage Worker<br/>main_worker.py]
        SALES[Sales LangGraph Engine<br/>web_dashboard.py]
        VOICE[Pipecat Voice Server<br/>bot.py :8765]
    end

    subgraph Data & Storage Tier
        SDB[(SQLite Database<br/>complaints.db)]
        VDB[(ChromaDB Vector Store<br/>Case Studies)]
        REP[Generated Reports<br/>reports/]
        RPLY[Replay Cache<br/>data/replay/]
    end

    CP -->|Submit Ticket| API
    ED -->|Review Tickets| API
    API <-->|Read / Write| SDB
    WORKER -->|Poll & Update| SDB
    SD -->|Trigger Pipeline| SALES
    SALES -->|Retrieve Evidence| VDB
    SALES -->|Write Outputs| REP
    SALES <-->|Replay| RPLY
    VC <-->|WebSocket Audio/Text| VOICE
    VOICE -->|Read Context Snapshot| SDB
    HUB -->|Poll Health & Mode| API & SALES & VOICE
```

---

## 2. Agent 1: Customer Support Triage Flow

```mermaid
sequenceDiagram
    autonumber
    actor Customer
    participant API as FastAPI (:8000)
    participant DB as SQLite (complaints.db)
    participant Worker as Background Worker
    participant LLM as LLM Triage Engine
    actor Employee

    Customer->>API: POST /complaints (email, order_id, text)
    API->>DB: Insert new complaint (status: 'new')
    API-->>Customer: 200 OK (ticket_id)
    loop Every 3 seconds
        Worker->>DB: Query complaints where status='new'
        Worker->>LLM: Triage(sentiment, category, priority P1-P4)
        LLM-->>Worker: {priority, reason, actions, email}
        Worker->>DB: Update complaint (status: 'escalated' | 'resolved', priority, reason)
    end
    Employee->>API: GET /complaints (filter by P1 / status)
    API-->>Employee: Tickets with AI "why" explanations
```

---

## 3. Agent 2: Sales Outreach State Machine Flow

```mermaid
stateDiagram-v2
    [*] --> FetchLeads: Load leads (CRM / TestLoader)
    FetchLeads --> CheckLeads: Remaining leads?
    CheckLeads --> ResearchLinkedIn: Yes (Extract company signals)
    CheckLeads --> [*]: No (Completed)
    ResearchLinkedIn --> ReviewWebsite: Audit website & positioning
    ReviewWebsite --> ParallelIntel: Gather blog, social & news signals
    ParallelIntel --> ScoreLead: Synthesize lead analysis
    ScoreLead --> BranchDecision: Is Lead Qualified (Score >= 7.0)?
    BranchDecision --> OutreachMaterials: QUALIFIED (ChromaDB RAG case study match)
    BranchDecision --> SaveReports: UNQUALIFIED (Graceful exit, zero KeyError)
    OutreachMaterials --> GenerateEmail: SPIN sales questions & email draft
    GenerateEmail --> SaveReports: Save 9 intelligence reports locally
    SaveReports --> UpdateCRM: Update status to ATTEMPTED_TO_CONTACT
    UpdateCRM --> CheckLeads
```

---

## 4. Agent 3: Voice Simulation & Cross-Agent Grounding Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as Demo Presenter
    participant Client as Browser (web_client.html)
    participant WS as WebSocket Server (:8765)
    participant DB as Support DB (complaints.db)
    participant LLM as Multi-Model Engine (Gemini / Groq / Mock)

    User->>Client: Speak into Mic or Type Question
    Client->>WS: Send utterance ("How many open P1 tickets?")
    WS->>DB: Read real-time ticket counts & open P1 items
    DB-->>WS: Snapshot: 12 tickets recorded, 3 P1 items
    WS->>LLM: Generate response citing live DB context
    LLM-->>WS: Crisp 1-2 sentence spoken answer
    WS-->>Client: WebSocket audio/text + used_data badge
    Client-->>User: Synthesize speech & render verified response
```
