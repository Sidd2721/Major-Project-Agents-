# SmartOps AI — Engineering Roadmap

This roadmap outlines planned enhancements, architectural refactoring, and next-semester feature additions aligned with project milestone commitments.

## Semester 2 Milestone Plan (Planned Deliverables)

### 1. Additional Autonomous Agents
- **Email Agent**:
  - Direct IMAP/Gmail API integration.
  - Multi-threaded inbox monitoring and categorization.
  - Contextual draft synthesis with human-in-the-loop approval.
- **Invoice & Financial Agent**:
  - OCR extraction for vendor invoices and receipts (Tesseract / Cloud Vision).
  - Cross-referencing against ERP purchase orders.
  - Discrepancy flagging and automated ledger reconciliation.

### 2. Platform Architecture & Data Layer
- **Unified FastAPI Gateway**:
  - Consolidate individual sub-agent micro-backends into a single asynchronous service gateway with modular routers.
  - Shared connection pools, standard pagination, and OpenAPI 3.1 documentation.
- **Supabase / PostgreSQL + pgvector Migration**:
  - Transition from local SQLite and ChromaDB files to hosted PostgreSQL.
  - Enable Row Level Security (RLS) policies for multi-tenant customer and employee isolation.
  - Store vector embeddings natively with `pgvector` indexation (HNSW).

### 3. Workflow & Human-in-the-Loop
- **Central Approval Queue**:
  - Unified escalation inbox for high-value actions (e.g., P1 ticket escalations, executive cold email dispatches, high-value invoices).
  - Audit log tracking every approval, rejection, and manual override.
- **Telephony Integration**:
  - Bridge browser-based voice simulation into Twilio / SIP telephony endpoints for inbound phone support and outbound sales dialing.

### 4. Frontend & Testing Evolution
- **Tailwind CSS & TypeScript**:
  - Migrate all UI modules to a shared TypeScript React component library.
  - Standardize on Tailwind CSS v4 with design-system tokens.
- **Automated End-to-End Suite**:
  - Complete Playwright test coverage with `@axe-core/playwright` accessibility audits across all responsive viewport widths (1280px, 768px, 375px).
