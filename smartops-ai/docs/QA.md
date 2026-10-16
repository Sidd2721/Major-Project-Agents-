# SmartOps AI — 20 Critical Viva Questions & Honest Answers

### Q1: What is the core problem SmartOps AI solves?
**Answer**: Enterprise operations face human latency bottlenecks in routing critical support complaints, conducting time-consuming account research for B2B sales outreach, and providing unified conversational access to operational data. SmartOps AI automates these workflows using specialized, coordinated AI agents.

### Q2: Why did you choose a multi-agent architecture instead of a single prompt?
**Answer**: A monolithic prompt combining customer service policies, lead research protocols, and sales qualification suffers from context window pollution and hallucination. Decomposing into discrete agents (Triage, Research, Scoring, RAG, Voice) provides deterministic state transitions, clear audit trails, and modular error recovery.

### Q3: Why did you use Groq Cloud as the primary LLM provider instead of OpenAI?
**Answer**: Groq's custom LPU (Language Processing Unit) architecture achieves inference speeds of 300–500 tokens/second, which is essential for real-time customer triage and voice conversation where latency over 800ms causes unacceptable conversational pauses.

### Q4: Why use SQLite and local ChromaDB instead of Supabase or PostgreSQL with pgvector?
**Answer**: For this phase of the major project, local embedded databases (SQLite and ChromaDB) enable 100% offline self-contained portability, zero network latency, zero hosting cost, and reproducible evaluation on any examiner's laptop. Migration to Supabase and PostgreSQL with pgvector and Row Level Security is scheduled for Semester 2.

### Q5: What is adapted from open-source vs written by your team?
**Answer**: As documented in `NOTICE.md`:
- We adapted the core WebSocket voice pipeline structure from Pipecat AI under the BSD-2-Clause license, extending it with dual personas, browser synthesis, and live SQLite context grounding.
- For Sales Outreach, we built the 12-node LangGraph state machine, scoring rubrics, and reporting templates on top of LangGraph/LangChain.
- For Customer Support, we developed the FastAPI backend, asynchronous worker, and dual React interfaces.

### Q6: What components are simulated vs real?
**Answer**:
- **Real & Working**: SQLite ticket storage, FastAPI REST APIs, background worker triage loop, P1-P4 classification, LangGraph 12-node state machine, ChromaDB RAG retrieval, and WebSocket bidirectional data streaming.
- **Simulated & Labelled**: Outbound email sending (logged to an outbox to prevent spamming real inboxes), outbound LinkedIn scraping (disabled by default to prevent headless browser blocks and IP bans), and telephony (browser Web Speech simulation instead of Twilio SIP trunks).

### Q7: What are the P1 to P4 priority definitions?
**Answer**:
- **P1 Critical**: Severe hardware defects, safety hazards (smoke/fire), or catastrophic service outages requiring immediate executive escalation.
- **P2 High**: Fulfillment delays >7 days, missing shipments, or billing discrepancies impacting ongoing client operations.
- **P3 Medium**: Standard inquiries, product setup questions, or cosmetic package scuffs.
- **P4 Low**: Positive customer feedback, address updates, or general operational compliments.

### Q8: How does the Customer Support worker communicate with the API?
**Answer**: Via an event-driven decoupled pattern backed by SQLite. The public FastAPI endpoint writes tickets with `status='new'`. An independent worker process (`main_worker.py`) polls unprocessed tickets every 3 seconds, runs the triage graph, and updates the database with priority, sentiment, AI explanation, and suggested actions.

### Q9: How does the Sales Outreach agent prevent hallucination in its emails?
**Answer**: It uses RAG (Retrieval-Augmented Generation) powered by ChromaDB. Before drafting email copy, the agent queries a vector index of verified client case studies (e.g. Spark Retail, EcoTrend) and forces the LLM to cite verifiable benchmarks (e.g., 85% query resolution, $150k quarterly revenue lift).

### Q10: What is the SPIN framework used in the sales pipeline?
**Answer**: SPIN is a consultative sales methodology focusing on:
1. **Situation**: Current operational setup.
2. **Problem**: Bottlenecks in manual ticket handling.
3. **Implication**: Financial cost of slow response times.
4. **Need-Payoff**: Quantifiable value of autonomous AI triage.

### Q11: How do you handle LLM rate limits during an evaluation demo?
**Answer**: SmartOps AI provides a 3-tier fallback hierarchy (`live` -> `mock` -> `replay`):
1. `live`: Calls Groq or Gemini if keys are provided.
2. `mock`: Produces deterministic, verified heuristic results with zero external network dependency.
3. `replay`: In the sales module, serves verified full pipeline runs saved on disk in `data/replay/`.

### Q12: How is the Voice Agent grounded in real data?
**Answer**: Before each conversational turn, `bot.py` queries `complaints.db` using read-only SQL aggregation (`COUNT(*)`, `SUM(P1)`). It injects this dynamic snapshot into the LLM system prompt and UI metadata, allowing the agent to accurately answer operational questions like "How many open P1 tickets are there?".

### Q13: What security guardrails are implemented against prompt injection?
**Answer**:
1. User complaint text is treated strictly as untrusted DATA, not system instructions.
2. The triage worker executes in an isolated environment without arbitrary tool-execution permissions.
3. Outputs are strictly schema-validated via Pydantic. Malicious attempts to reveal prompts or override priority are neutralized.

### Q14: How are administrative routes protected?
**Answer**: Sensitive administrative operations—such as ticket deletion, sales pipeline execution, and the `/demo/reset` endpoint—require an `ADMIN_KEY` passed via HTTP Bearer auth or `X-Admin-Key` headers. Unauthenticated requests receive HTTP 401/403.

### Q15: Why are Email and Invoice agents not in this repository?
**Answer**: Per our formal project milestone slides approved at the start of the semester, Email Automation (direct Gmail/Outlook IMAP syncing) and Financial Invoice Reconciliation (OCR & ERP integration) are scheduled for Semester 2. No stub or dummy code has been created for them.

### Q16: How do all user interfaces maintain visual consistency?
**Answer**: All web interfaces import and share `shared/tokens.css` (defining an 8-shade neutral scale, primary indigo brand color, P1-P4 semantic tokens, 4px spacing, and 3 shadow levels) and `shared/nav.js` (rendering a unified top navigation bar with live mode badges).

### Q17: Can this platform run completely offline?
**Answer**: Yes. All frontends rely on system font stacks (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto`) rather than external Google Fonts or CDN links. In `LLM_MODE=mock`, all three systems complete their workflows with zero internet connectivity.

### Q18: What is the regression fix for the old KeyError in the sales module?
**Answer**: Previously, when an unqualified lead (score < 7.0) took the `"not qualified"` branch, `custom_outreach_report_link` was not generated, causing a dictionary lookup `KeyError` at CRM update. We resolved this by using safe dictionary accessor methods (`state.get(...)`) and providing fallback metadata.

### Q19: How do you verify the system state from a clean clone?
**Answer**: Using `python scripts/verify.py`. It runs an end-to-end automated verification harness testing 17 specific criteria across health checks, triage accuracy, prompt injection defense, replay loading, voice context grounding, and auth protection, recording real command outputs to `docs/VERIFICATION.md`.

### Q20: What is the roadmap for Semester 2?
**Answer**:
1. Implementation of autonomous Email and Invoice agents.
2. Migration from local SQLite/ChromaDB to hosted PostgreSQL/Supabase with pgvector and Row Level Security.
3. Central human-in-the-loop escalation approval queue.
4. Twilio / SIP telephony integration replacing browser voice simulation.

### Q21: How does the Sales Outreach Assistant score with no data or when sources fail?
**Answer**:
The scoring engine evaluates the ratio of successfully retrieved data sources to total expected sources (Website, Blog, News, Public Profile, Social). If most sources are unreachable or blocked by anti-bot measures, the assistant never pretends the score is well-evidenced:
- It caps the confidence level to **Low confidence** and visibly flags: *"Based on X of 5 sources • Low confidence: Most sources could not be verified."*
- Unqualified or empty profiles are given a low score (e.g. 2.8/10), classified as *"Not a fit right now"*, and an explanatory note is displayed advising the user to check back when the company expands.
- This prevents false-positive outreach recommendations based on thin or hallucinated data.

### Q22: Is anything sent automatically by the Sales Outreach Assistant?
**Answer**:
**No, absolutely nothing is ever sent automatically.**
The product is intentionally designed as an executive assistant for a busy business owner, not an autonomous spam bot:
- Every email draft is prominently labelled: *"Draft only. Nothing has been sent."*
- The business owner must review the draft, can edit it inline, and must explicitly click *"Copy email"* to paste and send it from their own verified email client.
- The *"Mark as contacted"* button is a manual status toggle that records the outreach timestamp in local CRM state only after the user has taken action.

### Q23: Where do the matching success stories come from?
**Answer**:
Matching success stories are retrieved via RAG (Retrieval-Augmented Generation) powered by a local ChromaDB vector database:
- Past successful client deployments (such as *Spark Retail*, which achieved 85% automated customer query resolution and $150k quarterly revenue lift) are indexed as semantic embeddings.
- When researching a prospect's industry and operational pain points, the agent queries the vector collection for the closest semantic match.
- This grounds every generated pitch and call script in verifiable historical outcomes rather than ungrounded marketing claims.
