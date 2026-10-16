# SmartOps AI — 7-Minute Live Viva Demo Script

This script is structured for a college project evaluation or viva. Follow the timing, clicks, and fallback protocols.

---

## Pre-Demo Checklist (T-minus 2 minutes)
1. Open PowerShell and run: `python scripts/run_all.py`
2. Confirm the URL table prints in console:
   - Hub: `http://localhost:8080`
   - Customer Portal: `http://localhost:5173`
   - Employee Dashboard: `http://localhost:5174`
   - Sales Dashboard: `http://localhost:5175`
   - Voice Platform: `http://localhost:8765`
3. Open browser tabs for Hub (:8080) and Employee Dashboard (:5174).

---

## Minute 0:00 – 1:00: Overview & Central Hub
- **Action**: Display `http://localhost:8080`.
- **What to Say**:
  > "Respected Guide, SmartOps AI is an enterprise operational platform uniting three specialized AI agents under one roof: Support Triage, B2B Sales Research, and Interactive Voice Guidance. As seen on our Hub dashboard, all three services are actively communicating with green health indicators. We can verify our system mode in the top right: running in mock-verified mode to guarantee zero rate-limit disruptions."
- **Visual Evidence**:
  - Point to the 3 service cards and green live status dots.
  - Click "How It Works" modal on the Customer Support card to show the 3-step diagram (Input -> AI does -> Output).
- **Fallback**: If any status dot is gray, refresh page; health is polled every 5 seconds.

---

## Minute 1:00 – 3:00: Customer Support Triage Demo
- **Action**: Switch to Customer Portal (`http://localhost:5173`).
- **Input**:
  - Email: `demo.customer@enterprise.com`
  - Order ID: `ORD-9901`
  - Complaint: `The display monitor arrived completely cracked and won't turn on. Urgent replacement needed!`
- **Click**: "Submit Complaint".
- **Action**: Switch immediately to Employee Dashboard (`http://localhost:5174`).
- **What to Say**:
  > "The complaint was ingested and queued in SQLite. Our background worker polled the queue, invoked our classification graph, and instantly triaged this ticket as a P1 Critical incident. Notice that it does not just output a label—it explains the 'Why': physical damage in transit detected, and suggests 3 actionable next steps."
- **Visual Evidence**:
  - Point out the red P1 Critical badge.
  - Point out the AI Explanation field: *"Physical defect / severe product damage detected with immediate replacement urgency"*.
  - Show the auto-generated response email draft.
- **Fallback**: If worker polling is delayed, point to the pre-seeded P1 ticket (#TKT-1001-P1) already visible on the dashboard.

---

## Minute 3:00 – 5:00: Sales Outreach & RAG Pipeline Demo
- **Action**: Navigate to Sales Dashboard (`http://localhost:5175`).
- **Action**: Click "Trigger Pipeline Run".
- **What to Say**:
  > "Our second system is an autonomous 12-node LangGraph state machine. It profiles enterprise accounts, performs automated qualification scoring, and uses ChromaDB vector search to find relevant case studies. Here we see live step-by-step progress events: profiling the prospect, scoring them 8.5/10 (Qualified), and matching the Spark Retail case study."
- **Visual Evidence**:
  - Show the progress feed updating in real time.
  - Open the generated reports tab and review *"Personalized Email"* and *"Interview Script"*.
  - Point out the evidence citation: *"Spark Retail (85% query resolution, $150k quarterly revenue lift)"*.
- **Fallback**: If external API limits are exceeded, click "Load Replay Run"; it loads the verified 9-report replay dataset from `data/replay/` instantly with zero API dependencies.

---

## Minute 5:00 – 6:30: Voice Agent with Live Operational Grounding
- **Action**: Navigate to Voice Console (`http://localhost:8765`).
- **Action**: Click the microphone icon or type into the fallback prompt box:
  - Input: *"How many open P1 tickets are there?"*
- **What to Say**:
  > "Our third system demonstrates conversational voice interaction. Importantly, this is not an isolated chatbot. Before generating any response, the voice agent reads a real-time read-only context snapshot from our SQLite database. Watch as it accurately answers the exact number of open P1 tickets currently recorded in our live system."
- **Visual Evidence**:
  - Point to the spoken response: *"According to our live database, there are currently 3 open P1 critical tickets..."*
  - Point to the banner: *"Answered using: 12 open tickets recorded"*.
  - Point out the visible badge: *"Browser voice simulation, not telephony"*.
- **Fallback**: If microphone permissions are blocked in Chrome, use the integrated text-input box at the bottom of the console.

---

## Minute 6:30 – 7:00: Conclusion & Scope Alignment
- **What to Say**:
  > "To conclude: all three core systems operate with one-command start, share unified design tokens, feature graceful offline fallbacks, and run with zero external CDN dependencies. Per our approved project slides, Email and Invoice agents are formally scheduled for Semester 2. We welcome any questions from the guide."
