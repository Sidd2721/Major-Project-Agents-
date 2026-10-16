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

## Minute 3:00 – 5:00: Sales Outreach Assistant Demo (Business-Owner Experience)
- **Action**: Navigate to `http://localhost:5175`.
- **Expected Screen**: Clean, responsive assistant layout. Top nav shows SmartOps AI brand and MOCK mode badge. Collapsible *"How it works"* strip is visible at the top. Left panel displays 3 demo prospects (`Alex Mercer`, `Elena Rostova`, `Timmy Small`).
- **What to Say**:
  > "Our second system is designed specifically for small business owners who sell to other businesses and have zero hours to research prospects manually. The owner's job is simple: 'Tell me if this prospect is worth contacting, and give me what I need to contact them.'"
- **Step 1: Strong-Fit Prospect (Alex Mercer, Apex Dynamics)**:
  - **Action**: Select `Alex Mercer` (labelled 'Demo prospect') and click **"Prepare outreach"**.
  - **What to Say**:
    > "Watch the live plain-English progress list: reading their website, checking recent news, scoring fit, finding a past success story, and writing the email. In seconds, we receive three clear outcome cards."
  - **Visual Evidence**:
    1. **VERDICT Card**: Standout card with green *"Good fit"* badge, **8.5 out of 10** fit score, 3 plain-language reasons, matching success story citation (*"Similar to Spark Retail: Automated 85% of complex customer queries..."*), and data quality line (*"Based on 4 of 5 sources • High confidence"*).
    2. **EMAIL Draft Card**: Personalized subject and body draft. Notice the prominent label: *"Draft only. Nothing has been sent."*
    3. **Action**: Click **"Copy email"**; a toast confirmation appears (*"Email draft copied to clipboard"*).
    4. **Action**: Click **"Mark as contacted"**; button smoothly updates to *"✓ Contacted"*.
    5. **CALL SCRIPT Card**: Displays consultative opening hook, 3 discovery questions, and 2 anticipated objections with scripted replies.
- **Step 2: Unqualified Prospect Filtering (Timmy Small, Solo Blogger)**:
  - **Action**: Select `Timmy Small` in the left list.
  - **What to Say**:
    > "Now let's see what happens with a solo blogger or unqualified lead. We click 'Prepare outreach'—and notice our pipeline protects the business owner's time and reputation."
  - **Visual Evidence**:
    - Verdict card updates to gray *"Not a fit right now"* badge, **2.8 out of 10** score, and *"Low confidence"* data quality tag (*"Based on 2 of 5 sources"*).
    - Clear explanation displayed: *"No email draft generated. Outreach is intentionally withheld for low-fit prospects to protect your brand."*
    - Suggestion what to do: *"Check again after they hire a dedicated support team or expand commercial B2B operations."*
- **Step 3: Source Verification & Architecture Transparency**:
  - **Action**: Expand *"Research behind this (5 sources verified)"* accordion: show status for Website, Blog, News, Public Profile, and YouTube (shows friendly message *"This site blocks automated reading, so we skipped it"* with technical detail toggle).
  - **Action**: Click *"How this works"* in the footer to open the modal. Show the 5-step plain-language overview, then switch to the *"Technical view"* tab to present the 12-node LangGraph state machine diagram.
- **Fallback**: Works 100% offline in mock/replay mode with zero external API dependencies.

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
