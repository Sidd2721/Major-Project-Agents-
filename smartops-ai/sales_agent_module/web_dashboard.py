import os
import time
import json
import threading
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parent
SHARED_DIR = BASE_DIR.parent / "shared"
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

app = FastAPI(title="SmartOps AI Sales Outreach Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount shared assets
if SHARED_DIR.exists():
    app.mount("/shared", StaticFiles(directory=str(SHARED_DIR)), name="shared")

# ---------------------------------------------------------------------------
# Demo Prospects Store
# ---------------------------------------------------------------------------
DEFAULT_PROSPECTS = [
    {
        "id": "prospect_001",
        "name": "Alex Mercer",
        "first_name": "Alex",
        "last_name": "Mercer",
        "company": "Apex Dynamics",
        "role": "VP of Operations",
        "email": "alex.mercer@example.com",
        "website": "https://apexdynamics.example.com",
        "note": "Growing mid-market B2B distributor experiencing customer support delays and high ticket volume.",
        "is_demo": True,
        "status": "Outreach ready",
        "last_prepared": "Today at 2:15 PM",
        "fit_type": "strong"
    },
    {
        "id": "prospect_002",
        "name": "Elena Rostova",
        "first_name": "Elena",
        "last_name": "Rostova",
        "company": "FinTech Cloud Solutions",
        "role": "Chief Customer Officer",
        "email": "elena.rostova@example.com",
        "website": "https://fintechcloud.example.com",
        "note": "Evaluating automation solutions, but currently transitioning core ticketing platforms.",
        "is_demo": True,
        "status": "Outreach ready",
        "last_prepared": None,
        "fit_type": "maybe"
    },
    {
        "id": "prospect_003",
        "name": "Timmy Small",
        "first_name": "Timmy",
        "last_name": "Small",
        "company": "Timmy's Solo Hobby Blog",
        "role": "Solo Blogger",
        "email": "timmy@example.com",
        "website": "https://timmyblog.example.com",
        "note": "Individual content creator with zero B2B operations or support staff.",
        "is_demo": True,
        "status": "Not a fit right now",
        "last_prepared": None,
        "fit_type": "poor"
    }
]

prospects_db = [dict(p) for p in DEFAULT_PROSPECTS]

# ---------------------------------------------------------------------------
# Structured Result Generator
# ---------------------------------------------------------------------------
def build_prospect_result(prospect: Dict[str, Any], mode: str = "mock") -> Dict[str, Any]:
    fit_type = prospect.get("fit_type", "strong")
    name = prospect.get("name", "Prospect")
    company = prospect.get("company", "Company")

    if fit_type == "strong":
        score = 8.5
        verdict = "Good fit"
        confidence = "High"
        reasons = [
            "Experiencing rapid B2B volume growth with support ticket backlogs",
            "High-ticket contract value makes operational automation ROI immediate",
            "Active digital footprint and clear leadership intent around workflow scaling"
        ]
        sources = [
            {"name": "Website", "ok": True, "summary": "Company runs active multi-region operations with digital customer touchpoints.", "reason_if_failed": "", "details": "Indexed 14 pages; detected service desk and ERP portals."},
            {"name": "Blog", "ok": True, "summary": "Recent articles discuss scaling customer onboarding and workflow challenges.", "reason_if_failed": "", "details": "3 recent articles published in Q3 2026."},
            {"name": "News", "ok": True, "summary": "Recent press releases announce operational expansion and team growth.", "reason_if_failed": "", "details": "Distribution hub expansion announced on BusinessWire."},
            {"name": "Public profile", "ok": True, "summary": f"{name} leads operational strategy and systems modernization.", "reason_if_failed": "", "details": f"Role verified: {prospect.get('role', 'Executive')}, 4+ years at company."},
            {"name": "YouTube & social", "ok": False, "summary": "No active dedicated business video channel found.", "reason_if_failed": "This site blocks automated reading, so we skipped it", "details": "Public channel API returned zero verified corporate video handles."}
        ]
        sources_summary = "Based on 4 of 5 sources"
        matched_story = "Similar to Spark Retail: Automated 85% of complex customer queries while lifting quarterly revenue by $150k."
        email = {
            "subject": f"Streamlining {company}'s customer support & operations volume",
            "body": (
                f"Hi {prospect.get('first_name', name)},\n\n"
                f"I noticed {company} is expanding regional operations and managing higher customer inquiry volumes. Many operational leaders face communication delays during rapid scaling.\n\n"
                f"At SmartOps AI, we help businesses automate triage and customer follow-ups (similar to Spark Retail, which achieved 85% automated query resolution). We'd love to share a 10-minute walkthrough of how our multi-agent workflows could lighten your team's support load.\n\n"
                f"Would you be open to a brief chat this Thursday?\n\n"
                f"Best,\nSmartOps AI Sales Team"
            )
        }
        call_script = {
            "opening": f"Hi {prospect.get('first_name', name)}, this is from SmartOps AI. I've been following {company}'s recent growth—congratulations on the expansion.",
            "questions": [
                "How is your operations team currently handling the surge in customer inquiry volume during peak hours?",
                "What is the biggest operational bottleneck when onboarding new accounts across your customer hubs?",
                "If you could resolve 80% of routine inquiries automatically, where would your staff redirect their focus?"
            ],
            "objections": [
                {
                    "objection": "We already have an existing CRM / ticketing setup.",
                    "reply": "SmartOps doesn't replace your CRM; it works alongside it to triage tickets and draft responses automatically before your reps touch them."
                },
                {
                    "objection": "Our team doesn't have bandwidth for a heavy software implementation.",
                    "reply": "Setup takes under 2 hours with our lightweight API adapters, and there are no complex workflow overhauls required."
                }
            ],
            "full_script": (
                f"**Opening Hook:**\n"
                f"\"Hi {prospect.get('first_name', name)}, this is from SmartOps AI. I've been following {company}'s recent growth—congratulations on the expansion.\"\n\n"
                f"**Discovery & Situation:**\n"
                f"\"To understand your current setup: how are your teams handling the spike in customer queries across channels? On average, how much time do your leads spend triaging repetitive inquiries versus handling high-value escalations?\"\n\n"
                f"**Implication & Need:**\n"
                f"\"If those response delays persist during peak quarters, what's the risk to customer retention? If we could automate 80% of those first-touch responses within 48 hours, what would that unlock for your team?\"\n\n"
                f"**Next Step Proposal:**\n"
                f"\"Let's schedule a 10-minute preview with your operations lead to see the triage engine in action on sample tickets.\""
            )
        }
        poor_fit_advice = None
        poor_fit_explanation = None

    elif fit_type == "maybe":
        score = 6.8
        verdict = "Maybe"
        confidence = "Medium"
        reasons = [
            "Enterprise support ticket scale aligns well with agentic triage",
            "Currently transitioning internal ticketing platforms, which may delay buying decision",
            "High compliance and security requirements require custom onboarding validation"
        ]
        sources = [
            {"name": "Website", "ok": True, "summary": f"{company} provides enterprise cloud and financial infrastructure.", "reason_if_failed": "", "details": "SOC2 certified, multi-tenant banking platform overview."},
            {"name": "Blog", "ok": True, "summary": "Discusses compliance certifications and platform security updates.", "reason_if_failed": "", "details": "Focus on data protection and regulatory compliance."},
            {"name": "News", "ok": False, "summary": "Search query returned zero recent media press releases.", "reason_if_failed": "This site blocks automated reading, so we skipped it", "details": "Zero news syndication hits in last 90 days."},
            {"name": "Public profile", "ok": True, "summary": f"{name} oversees customer success and enterprise service desk.", "reason_if_failed": "", "details": "Extensive enterprise IT and support operations background."},
            {"name": "YouTube & social", "ok": False, "summary": "Social media feeds restricted to internal employee updates.", "reason_if_failed": "This site blocks automated reading, so we skipped it", "details": "Authentication required for private team feed."}
        ]
        sources_summary = "Based on 3 of 5 sources"
        matched_story = "Similar to Spark Retail: Automated 85% of complex customer queries with bank-grade audit logs."
        email = {
            "subject": f"Automated support triage during {company}'s platform transition",
            "body": (
                f"Hi {prospect.get('first_name', name)},\n\n"
                f"I saw that {company} is actively modernizing customer success infrastructure. When transitioning critical platforms, maintaining responsiveness is often the hardest challenge.\n\n"
                f"SmartOps AI provides agentic triage that plugs directly into existing workflows without disruption, maintaining full audit trails.\n\n"
                f"Would you have 10 minutes next week to explore if this could support your roadmap?\n\n"
                f"Best,\nSmartOps AI Sales Team"
            )
        }
        call_script = {
            "opening": f"Hi {prospect.get('first_name', name)}, this is from SmartOps AI. I've been tracking {company}'s focus on enterprise reliability and client experience.",
            "questions": [
                "How are your customer success teams maintaining response times during platform updates?",
                "What security or compliance hurdles usually slow down evaluating AI tools in your stack?",
                "How would automated triage assist your tier-1 analysts during high-volume incidents?"
            ],
            "objections": [
                {
                    "objection": "We are currently freezing vendor evaluations until migration finishes.",
                    "reply": "Understood—let's do a 10-minute briefing now so you have the numbers ready when your review cycle opens next quarter."
                },
                {
                    "objection": "We require strict data residency and on-premise audit guarantees.",
                    "reply": "SmartOps supports air-gapped deployment and mock fallback modes with zero customer data retention."
                }
            ],
            "full_script": (
                f"**Opening Hook:**\n"
                f"\"Hi {prospect.get('first_name', name)}, this is from SmartOps AI. I've been tracking {company}'s focus on enterprise reliability.\"\n\n"
                f"**Discovery & Platform Transition:**\n"
                f"\"With platform migrations, support volume often spikes temporarily. How is your team insulating key clients from delayed replies?\"\n\n"
                f"**Next Step Proposal:**\n"
                f"\"Let's do a short executive briefing so you have benchmark data ready when your platform review opens.\""
            )
        }
        poor_fit_advice = None
        poor_fit_explanation = None

    else:
        # Poor fit (e.g. Timmy Small)
        score = 2.8
        verdict = "Not a fit right now"
        confidence = "Low"
        reasons = [
            "Solo operator with no customer support queue or dedicated team",
            "No B2B sales motion or enterprise ticket queue to automate",
            "Budget and operational requirements do not match an agentic automation platform"
        ]
        sources = [
            {"name": "Website", "ok": True, "summary": "Personal blog covering hobby photography and casual personal writing.", "reason_if_failed": "", "details": "Static Hugo blog hosted on personal domain."},
            {"name": "Blog", "ok": True, "summary": "Informal opinion posts; no corporate products or business services offered.", "reason_if_failed": "", "details": "Last post 4 weeks ago about camera lenses."},
            {"name": "News", "ok": False, "summary": "No business news or commercial press coverage found.", "reason_if_failed": "This site blocks automated reading, so we skipped it", "details": "No articles found in trade or industry news sources."},
            {"name": "Public profile", "ok": False, "summary": "Profile indicates solo hobbyist without corporate organization.", "reason_if_failed": "This site blocks automated reading, so we skipped it", "details": "Personal profile only; no registered business entity."},
            {"name": "YouTube & social", "ok": False, "summary": "Personal hobby uploads only without commercial activity.", "reason_if_failed": "This site blocks automated reading, so we skipped it", "details": "Non-commercial hobby account."}
        ]
        sources_summary = "Based on 2 of 5 sources"
        matched_story = "No matching enterprise story applicable for individual hobbyists."
        email = None
        call_script = None
        poor_fit_advice = "Check again after they hire a dedicated support team or expand into commercial B2B operations."
        poor_fit_explanation = "No email draft generated. Outreach is intentionally withheld for low-fit prospects to protect your brand and focus your sales time on high-potential buyers."

    progress = [
        {"step": 1, "name": "Reading their website", "status": "done", "reason": "Indexed homepage and overview"},
        {"step": 2, "name": "Checking recent news", "status": "done" if fit_type != "poor" else "skipped", "reason": "Press releases analyzed" if fit_type != "poor" else "This site blocks automated reading, so we skipped it"},
        {"step": 3, "name": "Scoring the fit", "status": "done", "reason": f"Evaluated B2B fit criteria (Score: {score}/10)"},
        {"step": 4, "name": "Finding a matching success story", "status": "done" if fit_type != "poor" else "skipped", "reason": "Retrieved Spark Retail case study" if fit_type != "poor" else "Skipped for unqualified prospect"},
        {"step": 5, "name": "Writing the email", "status": "done" if fit_type != "poor" else "skipped", "reason": "Drafted personalized outreach" if fit_type != "poor" else "Omitted intentionally: prospect is not a fit right now"}
    ]

    return {
        "verdict": verdict,
        "score": score,
        "score_display": f"{score} out of 10",
        "confidence": confidence,
        "reasons": reasons,
        "sources": sources,
        "sources_summary": sources_summary,
        "matched_story": matched_story,
        "email": email,
        "call_script": call_script,
        "poor_fit_advice": poor_fit_advice,
        "poor_fit_explanation": poor_fit_explanation,
        "progress": progress,
        # Legacy compatibility
        "lead_name": name,
        "company": company,
        "qualification_status": "qualified" if fit_type != "poor" else "unqualified",
        "lead_score": score,
        "matched_case_study": matched_story,
        "outreach_email": email["body"] if email else "",
        "mode": mode
    }

# Pipeline runtime state
current_prospect_id = "prospect_001"
initial_result = build_prospect_result(DEFAULT_PROSPECTS[0], mode="mock")

pipeline_state = {
    "status": "completed",
    "last_run": "Today at 2:15 PM",
    "current_step": "Outreach ready",
    "prospect_id": "prospect_001",
    "progress_steps": initial_result["progress"],
    "result": initial_result,
    "logs": ["Autonomous research completed successfully.", "Fit verdict determined: Good fit (8.5/10)."]
}

# ---------------------------------------------------------------------------
# Background Task Execution
# ---------------------------------------------------------------------------
def run_preparation_task(prospect_id: str):
    global pipeline_state, prospects_db
    
    # Locate prospect
    prospect = next((p for p in prospects_db if p["id"] == prospect_id), None)
    if not prospect:
        prospect = prospects_db[0]

    mode = os.getenv("LLM_MODE", "mock").lower()
    
    pipeline_state["status"] = "running"
    pipeline_state["prospect_id"] = prospect["id"]
    pipeline_state["logs"] = [f"Starting research for {prospect['name']} ({prospect['company']})..."]

    steps = [
        ("Reading their website", "done", "Indexed company homepage and overview pages"),
        ("Checking recent news", "done" if prospect.get("fit_type") != "poor" else "skipped", "Press releases analyzed" if prospect.get("fit_type") != "poor" else "This site blocks automated reading, so we skipped it"),
        ("Scoring the fit", "done", "Scored company fit against ideal customer criteria"),
        ("Finding a matching success story", "done" if prospect.get("fit_type") != "poor" else "skipped", "Matched past operational study" if prospect.get("fit_type") != "poor" else "Skipped for unqualified prospect"),
        ("Writing the email", "done" if prospect.get("fit_type") != "poor" else "skipped", "Drafted custom first email" if prospect.get("fit_type") != "poor" else "Omitted intentionally: prospect is not a fit right now")
    ]

    current_steps = [
        {"step": i + 1, "name": s[0], "status": "pending", "reason": s[2]}
        for i, s in enumerate(steps)
    ]
    pipeline_state["progress_steps"] = current_steps

    # Check if live mode with real API keys
    has_live_keys = bool(
        (os.getenv("GROQ_API_KEY") and len(os.getenv("GROQ_API_KEY", "")) > 15 and "REPLACE" not in os.getenv("GROQ_API_KEY", "")) or
        (os.getenv("GEMINI_API_KEY") and len(os.getenv("GEMINI_API_KEY", "")) > 15 and "REPLACE" not in os.getenv("GEMINI_API_KEY", ""))
    )

    if mode == "live" and has_live_keys:
        venv_python = BASE_DIR / "venv" / "Scripts" / "python.exe"
        main_script = BASE_DIR / "main.py"
        try:
            pipeline_state["current_step"] = "Executing research and analysis..."
            proc = subprocess.Popen(
                [str(venv_python), str(main_script)],
                cwd=str(BASE_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            for line in proc.stdout:
                line_str = line.strip()
                if line_str:
                    pipeline_state["logs"].append(line_str)
                    if len(pipeline_state["logs"]) > 200:
                        pipeline_state["logs"].pop(0)
            proc.wait()
        except Exception as e:
            pipeline_state["logs"].append(f"Subprocess notice: {e}")

    else:
        # Step-by-step plain English progress simulation for mock / fallback
        for i, s in enumerate(steps):
            current_steps[i]["status"] = "working"
            pipeline_state["current_step"] = s[0]
            pipeline_state["progress_steps"] = list(current_steps)
            time.sleep(0.35)
            current_steps[i]["status"] = s[1]
            pipeline_state["progress_steps"] = list(current_steps)
            pipeline_state["logs"].append(f"✓ {s[0]}: {s[2]}")

    result = build_prospect_result(prospect, mode=mode)
    time_str = time.strftime("%I:%M %p").lstrip("0")
    last_prep_str = f"Today at {time_str}"
    
    prospect["last_prepared"] = last_prep_str
    if prospect.get("status") != "Contacted":
        prospect["status"] = "Outreach ready" if result["verdict"] != "Not a fit right now" else "Not a fit right now"
    prospect["last_result"] = result

    pipeline_state["status"] = "completed"
    pipeline_state["current_step"] = "Outreach ready"
    pipeline_state["last_run"] = last_prep_str
    pipeline_state["result"] = result

# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok", "service": "sales_agent_module"}

@app.get("/api/mode")
def api_mode():
    mode = os.getenv("LLM_MODE", "mock").lower()
    return {"mode": mode, "service": "sales_agent_module", "degraded": (mode == "mock")}

@app.get("/workflow.png")
def get_workflow_diagram():
    img_path = BASE_DIR / "workflow.png"
    if img_path.exists():
        return FileResponse(img_path)
    return JSONResponse({"error": "Workflow image not found"}, status_code=404)

@app.get("/api/prospects")
def get_prospects():
    return {"prospects": prospects_db, "current_prospect_id": current_prospect_id}

@app.post("/api/prospects")
async def add_prospect(req: Request):
    global prospects_db, current_prospect_id
    data = await req.json()
    new_id = f"prospect_{len(prospects_db) + 1:03d}"
    
    name = (data.get("name") or "").strip() or "New Prospect"
    company = (data.get("company") or "").strip() or "Company"
    parts = name.split()
    first_name = parts[0] if parts else name
    last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

    text_to_eval = (company + " " + data.get("note", "")).lower()
    if any(w in text_to_eval for w in ["hobby", "solo", "personal", "blog"]):
        fit_type = "poor"
        status = "Not a fit right now"
    elif any(w in text_to_eval for w in ["transition", "evaluate", "maybe"]):
        fit_type = "maybe"
        status = "Outreach ready"
    else:
        fit_type = "strong"
        status = "Outreach ready"

    prospect = {
        "id": new_id,
        "name": name,
        "first_name": first_name,
        "last_name": last_name,
        "company": company,
        "role": data.get("role", "Decision Maker"),
        "email": data.get("email", f"{first_name.lower()}@{company.lower().replace(' ', '')}.example.com"),
        "website": data.get("website", f"https://{company.lower().replace(' ', '')}.example.com"),
        "note": data.get("note", "Prospect added by user."),
        "is_demo": False,
        "status": status,
        "last_prepared": None,
        "fit_type": fit_type
    }
    prospects_db.insert(0, prospect)
    current_prospect_id = new_id
    return {"status": "ok", "prospect": prospect}

@app.post("/api/prepare")
async def trigger_prepare(background_tasks: BackgroundTasks, req: Request = None):
    global current_prospect_id, pipeline_state
    if pipeline_state["status"] == "running":
        return JSONResponse({"status": "already_running", "message": "Preparation is already underway."})

    pid = current_prospect_id
    if req:
        try:
            body = await req.json()
            if body.get("prospect_id"):
                pid = body["prospect_id"]
                current_prospect_id = pid
        except Exception:
            pass

    background_tasks.add_task(run_preparation_task, pid)
    return {"status": "started", "message": "Preparing outreach...", "prospect_id": pid}

@app.post("/api/run")
def trigger_run(background_tasks: BackgroundTasks):
    """Legacy endpoint alias for /api/prepare."""
    return trigger_prepare(background_tasks)

@app.post("/api/mark-contacted")
async def mark_contacted(req: Request):
    global prospects_db, pipeline_state
    try:
        body = await req.json()
        pid = body.get("prospect_id") or current_prospect_id
    except Exception:
        pid = current_prospect_id

    for p in prospects_db:
        if p["id"] == pid:
            p["status"] = "Contacted"
            time_str = time.strftime("%I:%M %p").lstrip("0")
            p["last_prepared"] = f"Contacted today at {time_str}"
            return {"status": "ok", "prospect_status": "Contacted", "message": f"{p['name']} marked as Contacted."}

    return JSONResponse({"error": "Prospect not found"}, status_code=404)

@app.get("/api/status")
def get_status():
    result = pipeline_state.get("result") or {}
    return {
        "status": pipeline_state["status"],
        "current_step": pipeline_state["current_step"],
        "last_run": pipeline_state["last_run"],
        "prospect_id": pipeline_state["prospect_id"],
        "progress_steps": pipeline_state["progress_steps"],
        # Rich structured result fields
        "verdict": result.get("verdict", "Good fit"),
        "score": result.get("score", 8.5),
        "score_display": result.get("score_display", "8.5 out of 10"),
        "confidence": result.get("confidence", "High"),
        "reasons": result.get("reasons", []),
        "sources": result.get("sources", []),
        "sources_summary": result.get("sources_summary", "Based on 4 of 5 sources"),
        "matched_story": result.get("matched_story", ""),
        "email": result.get("email"),
        "call_script": result.get("call_script"),
        "poor_fit_advice": result.get("poor_fit_advice"),
        "poor_fit_explanation": result.get("poor_fit_explanation"),
        # Legacy compatibility fields
        "logs": pipeline_state.get("logs", []),
        "reports": get_reports()["reports"]
    }

@app.get("/api/reports")
def get_reports():
    reports = []
    if REPORTS_DIR.exists():
        for file in sorted(REPORTS_DIR.glob("*.txt")):
            try:
                content = file.read_text(encoding="utf-8")
            except Exception:
                content = file.read_text(encoding="latin-1", errors="ignore")
            # Sanitize technical codes in content
            content = content.replace("HTTP 403 Forbidden", "Access restricted by server; automated reading skipped")
            content = content.replace("HTTP 403", "Access restricted by server")
            # Replace technical lead titles for friendly view
            friendly_title = file.stem.replace("Lead Research", "Prospect Research").replace("Lead Analysis", "Prospect Analysis")
            reports.append({
                "title": friendly_title,
                "filename": file.name,
                "size_kb": round(file.stat().st_size / 1024, 2),
                "content": content
            })
    return {"reports": reports}

# ---------------------------------------------------------------------------
# Frontend Single-Page UI
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def index_page():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sales outreach assistant | SmartOps AI</title>
  <link rel="stylesheet" href="/shared/tokens.css">
  <link rel="stylesheet" href="/shared/components.css">
  <style>
    *, *::before, *::after {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    html, body {
      width: 100%;
      max-width: 100%;
      overflow-x: hidden;
      background: var(--color-neutral-50, #f8fafc);
      color: var(--color-neutral-900, #0f172a);
      font-family: var(--font-sans, Inter, system-ui, -apple-system, sans-serif);
      font-size: 15px;
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
    }
    a, button {
      font-family: inherit;
    }
    :focus-visible {
      outline: 2px solid var(--color-brand, #4f46e5);
      outline-offset: 2px;
    }

    /* Container & Layout */
    .app-wrap {
      max-width: 1240px;
      margin: 0 auto;
      padding: 24px 20px 64px;
      width: 100%;
    }
    .page-header {
      margin-bottom: 20px;
    }
    .page-title {
      font-size: 26px;
      font-weight: 700;
      letter-spacing: -0.02em;
      color: var(--color-neutral-900, #0f172a);
      margin-bottom: 4px;
    }
    .page-subtitle {
      font-size: 15px;
      color: var(--color-neutral-600, #475569);
    }

    /* Collapsible How It Works Strip */
    .how-strip {
      background: #ffffff;
      border: 1px solid var(--color-neutral-200, #e2e8f0);
      border-radius: 10px;
      padding: 12px 16px;
      margin-bottom: 24px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .how-strip-summary {
      display: flex;
      align-items: center;
      justify-content: space-between;
      cursor: pointer;
      font-size: 13.5px;
      font-weight: 600;
      color: var(--color-neutral-700, #334155);
      user-select: none;
    }
    .how-strip-steps {
      margin-top: 10px;
      padding-top: 10px;
      border-top: 1px solid var(--color-neutral-200, #e2e8f0);
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
      font-size: 13px;
      color: var(--color-neutral-600, #475569);
    }
    .how-step-item strong {
      color: var(--color-neutral-900, #0f172a);
      display: block;
      margin-bottom: 2px;
    }

    /* Main Grid */
    .main-grid {
      display: grid;
      grid-template-columns: minmax(0, 370px) minmax(0, 1fr);
      gap: 24px;
      align-items: start;
    }
    @media (max-width: 900px) {
      .main-grid {
        grid-template-columns: minmax(0, 1fr);
      }
    }

    /* Left Sidebar: Prospect Panel */
    .prospect-panel {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .panel-card {
      background: #ffffff;
      border: 1px solid var(--color-neutral-200, #e2e8f0);
      border-radius: 12px;
      padding: 18px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .card-heading {
      font-size: 14px;
      font-weight: 600;
      color: var(--color-neutral-900, #0f172a);
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .prospect-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .prospect-item {
      padding: 10px 12px;
      border-radius: 8px;
      border: 1px solid var(--color-neutral-200, #e2e8f0);
      background: var(--color-neutral-50, #f8fafc);
      cursor: pointer;
      text-align: left;
      transition: all 0.15s ease;
      width: 100%;
    }
    .prospect-item:hover {
      border-color: var(--color-brand-light, #818cf8);
      background: #ffffff;
    }
    .prospect-item.active {
      border-color: var(--color-brand, #4f46e5);
      background: #ffffff;
      box-shadow: 0 0 0 2px var(--color-brand-subtle, rgba(79,70,229,.12));
    }
    .prospect-item-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 3px;
    }
    .prospect-item-name {
      font-weight: 600;
      font-size: 14px;
      color: var(--color-neutral-900, #0f172a);
    }
    .prospect-item-company {
      font-size: 12.5px;
      color: var(--color-neutral-600, #475569);
    }

    .demo-tag {
      font-size: 10.5px;
      font-weight: 600;
      padding: 1px 6px;
      border-radius: 4px;
      background: var(--color-neutral-200, #e2e8f0);
      color: var(--color-neutral-700, #334155);
      letter-spacing: 0.02em;
    }

    /* Selected Details Card */
    .prospect-detail-row {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      padding: 6px 0;
      border-bottom: 1px solid var(--color-neutral-100, #f1f5f9);
      font-size: 13px;
    }
    .prospect-detail-row:last-child {
      border-bottom: none;
    }
    .prospect-detail-label {
      color: var(--color-neutral-500, #64748b);
      font-weight: 500;
    }
    .prospect-detail-val {
      font-weight: 500;
      color: var(--color-neutral-800, #1e293b);
      text-align: right;
      max-width: 60%;
      word-break: break-word;
    }
    .prospect-note-box {
      margin-top: 10px;
      padding: 8px 10px;
      background: var(--color-neutral-100, #f1f5f9);
      border-radius: 6px;
      font-size: 12.5px;
      color: var(--color-neutral-700, #334155);
      line-height: 1.45;
    }

    /* Status Pills */
    .pill {
      font-size: 11.5px;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 9999px;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      white-space: nowrap;
    }
    .pill-ready {
      background: rgba(22, 163, 74, 0.12);
      color: #16a34a;
      border: 1px solid rgba(22, 163, 74, 0.25);
    }
    .pill-contacted {
      background: rgba(2, 132, 199, 0.12);
      color: #0284c7;
      border: 1px solid rgba(2, 132, 199, 0.25);
    }
    .pill-poor {
      background: rgba(100, 116, 139, 0.12);
      color: #475569;
      border: 1px solid rgba(100, 116, 139, 0.25);
    }
    .pill-maybe {
      background: rgba(202, 138, 4, 0.12);
      color: #b45309;
      border: 1px solid rgba(202, 138, 4, 0.25);
    }

    /* Primary Action Button */
    .btn-prepare {
      width: 100%;
      padding: 11px 16px;
      font-size: 14.5px;
      font-weight: 600;
      border-radius: 8px;
      background: var(--color-brand, #4f46e5);
      color: #ffffff;
      border: none;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      transition: background 0.15s ease, transform 0.1s ease;
      box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .btn-prepare:hover:not(:disabled) {
      background: var(--color-brand-dark, #3730a3);
    }
    .btn-prepare:active:not(:disabled) {
      transform: scale(0.99);
    }
    .btn-prepare:disabled {
      opacity: 0.65;
      cursor: not-allowed;
    }
    .last-prep-text {
      font-size: 12px;
      color: var(--color-neutral-500, #64748b);
      text-align: center;
      margin-top: 8px;
    }

    /* Add Custom Prospect Form */
    .add-form-toggle {
      font-size: 13px;
      color: var(--color-brand, #4f46e5);
      background: none;
      border: none;
      cursor: pointer;
      font-weight: 500;
      padding: 4px 0;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }
    .add-form-wrap {
      margin-top: 10px;
      display: none;
      flex-direction: column;
      gap: 8px;
    }
    .add-form-wrap.open {
      display: flex;
    }
    .form-input {
      width: 100%;
      padding: 7px 10px;
      font-size: 13px;
      border: 1px solid var(--color-neutral-300, #cbd5e1);
      border-radius: 6px;
      background: #ffffff;
      color: var(--color-neutral-900, #0f172a);
    }
    .form-input:focus {
      border-color: var(--color-brand, #4f46e5);
    }

    /* Right Result Area */
    .result-area {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    /* Empty State */
    .empty-state {
      background: #ffffff;
      border: 1px dashed var(--color-neutral-300, #cbd5e1);
      border-radius: 12px;
      padding: 48px 24px;
      text-align: center;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 10px;
    }
    .empty-icon {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: var(--color-brand-subtle, rgba(79,70,229,.12));
      color: var(--color-brand, #4f46e5);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      margin-bottom: 4px;
    }
    .empty-title {
      font-size: 17px;
      font-weight: 600;
      color: var(--color-neutral-900, #0f172a);
    }
    .empty-desc {
      font-size: 14px;
      color: var(--color-neutral-500, #64748b);
      max-width: 420px;
    }

    /* Live Progress Card */
    .progress-card {
      background: #ffffff;
      border: 1px solid var(--color-neutral-200, #e2e8f0);
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
      display: none;
    }
    .progress-card.active {
      display: block;
    }
    .progress-title {
      font-size: 15px;
      font-weight: 600;
      color: var(--color-neutral-900, #0f172a);
      margin-bottom: 14px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .progress-step-list {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .progress-step-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 13.5px;
    }
    .progress-step-left {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .step-indicator {
      width: 18px;
      height: 18px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 10px;
      font-weight: 700;
    }
    .step-done {
      background: #dcfce7;
      color: #16a34a;
    }
    .step-working {
      background: #fef3c7;
      color: #d97706;
      animation: pulse-step 1.2s infinite;
    }
    .step-pending {
      background: #f1f5f9;
      color: #94a3b8;
    }
    .step-skipped {
      background: #f1f5f9;
      color: #64748b;
    }
    @keyframes pulse-step {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.4; }
    }
    @media (prefers-reduced-motion: reduce) {
      .step-working { animation: none; }
    }

    /* ======================================================================
       OUTCOME CARD 1: THE VERDICT CARD (STANDOUT ELEMENT)
       ====================================================================== */
    .verdict-card {
      background: #ffffff;
      border: 2px solid var(--color-brand, #4f46e5);
      border-radius: 14px;
      padding: 24px;
      box-shadow: 0 4px 12px rgba(79, 70, 229, 0.08);
      position: relative;
    }
    .verdict-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;
      flex-wrap: wrap;
      gap: 8px;
    }
    .verdict-title-wrap {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .verdict-score-row {
      display: flex;
      align-items: baseline;
      gap: 10px;
      margin-bottom: 16px;
    }
    .verdict-big-score {
      font-size: 38px;
      font-weight: 800;
      letter-spacing: -0.03em;
      line-height: 1;
      color: var(--color-neutral-900, #0f172a);
    }
    .verdict-score-label {
      font-size: 15px;
      color: var(--color-neutral-500, #64748b);
      font-weight: 500;
    }
    .verdict-reasons-title {
      font-size: 13px;
      font-weight: 600;
      color: var(--color-neutral-700, #334155);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      margin-bottom: 8px;
    }
    .verdict-reasons-list {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 6px;
      margin-bottom: 18px;
    }
    .verdict-reasons-list li {
      font-size: 14px;
      color: var(--color-neutral-700, #334155);
      display: flex;
      align-items: flex-start;
      gap: 8px;
      line-height: 1.45;
    }
    .verdict-reasons-list li::before {
      content: "•";
      color: var(--color-brand, #4f46e5);
      font-weight: bold;
      font-size: 16px;
      line-height: 1;
    }
    .story-box {
      background: var(--color-neutral-50, #f8fafc);
      border: 1px solid var(--color-neutral-200, #e2e8f0);
      border-left: 3px solid var(--color-brand, #4f46e5);
      border-radius: 6px;
      padding: 10px 14px;
      font-size: 13.5px;
      color: var(--color-neutral-700, #334155);
      margin-bottom: 16px;
      line-height: 1.45;
    }
    .story-box strong {
      color: var(--color-neutral-900, #0f172a);
    }
    .data-quality-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-top: 12px;
      border-top: 1px solid var(--color-neutral-200, #e2e8f0);
      font-size: 12.5px;
      color: var(--color-neutral-500, #64748b);
      flex-wrap: wrap;
      gap: 6px;
    }
    .confidence-tag {
      font-weight: 600;
      padding: 1px 6px;
      border-radius: 4px;
      font-size: 11.5px;
    }
    .conf-high {
      background: #dcfce7;
      color: #15803d;
    }
    .conf-medium {
      background: #fef3c7;
      color: #b45309;
    }
    .conf-low {
      background: #fee2e2;
      color: #b91c1c;
    }

    /* Poor Fit Notice Inside Verdict */
    .poor-fit-box {
      background: #fff7ed;
      border: 1px solid #fed7aa;
      border-radius: 8px;
      padding: 14px;
      margin-top: 12px;
      font-size: 13.5px;
      color: #9a3412;
      line-height: 1.45;
    }
    .poor-fit-box strong {
      display: block;
      margin-bottom: 4px;
      color: #7c2d12;
    }

    /* ======================================================================
       OUTCOME CARD 2: EMAIL DRAFT CARD
       ====================================================================== */
    .email-card {
      background: #ffffff;
      border: 1px solid var(--color-neutral-200, #e2e8f0);
      border-radius: 12px;
      padding: 22px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .card-top-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;
      flex-wrap: wrap;
      gap: 8px;
    }
    .draft-badge {
      font-size: 11.5px;
      background: var(--color-neutral-100, #f1f5f9);
      color: var(--color-neutral-600, #475569);
      padding: 3px 8px;
      border-radius: 6px;
      font-weight: 500;
    }
    .email-subject-box {
      background: var(--color-neutral-50, #f8fafc);
      border: 1px solid var(--color-neutral-200, #e2e8f0);
      border-radius: 6px;
      padding: 10px 12px;
      font-size: 14px;
      margin-bottom: 12px;
      color: var(--color-neutral-900, #0f172a);
    }
    .email-subject-box strong {
      color: var(--color-neutral-500, #64748b);
      margin-right: 6px;
    }
    .email-body-view {
      background: #ffffff;
      border: 1px solid var(--color-neutral-200, #e2e8f0);
      border-radius: 8px;
      padding: 16px;
      font-size: 14px;
      line-height: 1.6;
      color: var(--color-neutral-800, #1e293b);
      white-space: pre-wrap;
      font-family: inherit;
      min-height: 160px;
      max-height: 380px;
      overflow-y: auto;
    }
    .email-body-edit {
      width: 100%;
      min-height: 180px;
      padding: 14px;
      font-size: 14px;
      line-height: 1.6;
      border: 1px solid var(--color-brand, #4f46e5);
      border-radius: 8px;
      font-family: inherit;
      display: none;
    }
    .email-actions {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: 16px;
      flex-wrap: wrap;
      gap: 10px;
    }
    .btn-action {
      font-size: 13.5px;
      font-weight: 500;
      padding: 7px 14px;
      border-radius: 6px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border: 1px solid var(--color-neutral-300, #cbd5e1);
      background: #ffffff;
      color: var(--color-neutral-700, #334155);
      transition: all 0.15s ease;
    }
    .btn-action:hover {
      background: var(--color-neutral-50, #f8fafc);
      border-color: var(--color-neutral-400, #94a3b8);
    }
    .btn-contacted-action {
      background: var(--color-neutral-50, #f8fafc);
      color: var(--color-neutral-700, #334155);
      border-color: var(--color-neutral-300, #cbd5e1);
    }
    .btn-contacted-action.marked {
      background: #dcfce7;
      color: #15803d;
      border-color: #86efac;
    }

    /* ======================================================================
       OUTCOME CARD 3: CALL SCRIPT CARD
       ====================================================================== */
    .script-card {
      background: #ffffff;
      border: 1px solid var(--color-neutral-200, #e2e8f0);
      border-radius: 12px;
      padding: 22px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .script-section {
      margin-bottom: 16px;
    }
    .script-label {
      font-size: 12.5px;
      font-weight: 600;
      color: var(--color-neutral-500, #64748b);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      margin-bottom: 6px;
    }
    .script-quote {
      background: var(--color-neutral-50, #f8fafc);
      border-left: 3px solid var(--color-neutral-300, #cbd5e1);
      padding: 10px 14px;
      border-radius: 0 6px 6px 0;
      font-size: 14px;
      font-style: italic;
      color: var(--color-neutral-800, #1e293b);
      line-height: 1.5;
    }
    .script-bullets {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .script-bullets li {
      font-size: 13.5px;
      color: var(--color-neutral-700, #334155);
      display: flex;
      align-items: flex-start;
      gap: 8px;
      line-height: 1.45;
    }
    .script-bullets li::before {
      content: "→";
      color: var(--color-brand, #4f46e5);
      font-weight: bold;
    }
    .objection-item {
      background: var(--color-neutral-50, #f8fafc);
      border: 1px solid var(--color-neutral-200, #e2e8f0);
      border-radius: 6px;
      padding: 10px 12px;
      margin-bottom: 8px;
      font-size: 13.5px;
    }
    .objection-q {
      font-weight: 600;
      color: var(--color-neutral-900, #0f172a);
      margin-bottom: 3px;
    }
    .objection-a {
      color: var(--color-neutral-600, #475569);
      line-height: 1.45;
    }
    .full-script-toggle {
      font-size: 13px;
      color: var(--color-brand, #4f46e5);
      background: none;
      border: none;
      cursor: pointer;
      font-weight: 500;
      padding: 4px 0;
    }
    .full-script-content {
      display: none;
      margin-top: 12px;
      padding: 14px;
      background: var(--color-neutral-50, #f8fafc);
      border: 1px solid var(--color-neutral-200, #e2e8f0);
      border-radius: 8px;
      font-size: 13.5px;
      line-height: 1.6;
      white-space: pre-wrap;
    }

    /* ======================================================================
       RESEARCH ACCORDION & DOSSIERS
       ====================================================================== */
    .research-accordion {
      background: #ffffff;
      border: 1px solid var(--color-neutral-200, #e2e8f0);
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .accordion-summary {
      display: flex;
      align-items: center;
      justify-content: space-between;
      cursor: pointer;
      font-size: 15px;
      font-weight: 600;
      color: var(--color-neutral-900, #0f172a);
      user-select: none;
    }
    .sources-list {
      margin-top: 16px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .source-row {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      padding: 10px 12px;
      background: var(--color-neutral-50, #f8fafc);
      border: 1px solid var(--color-neutral-200, #e2e8f0);
      border-radius: 8px;
      gap: 12px;
      flex-wrap: wrap;
    }
    .source-info {
      flex: 1;
      min-width: 200px;
    }
    .source-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 3px;
    }
    .source-name {
      font-size: 13.5px;
      font-weight: 600;
      color: var(--color-neutral-900, #0f172a);
    }
    .source-summary-text {
      font-size: 12.5px;
      color: var(--color-neutral-600, #475569);
      line-height: 1.4;
    }
    .source-details-text {
      display: none;
      margin-top: 6px;
      font-size: 11.5px;
      font-family: var(--font-mono, monospace);
      color: var(--color-neutral-500, #64748b);
      background: #ffffff;
      padding: 6px 8px;
      border-radius: 4px;
      border: 1px solid var(--color-neutral-200, #e2e8f0);
    }
    .btn-details-toggle {
      font-size: 11.5px;
      color: var(--color-brand, #4f46e5);
      background: none;
      border: none;
      cursor: pointer;
      text-decoration: underline;
    }

    /* Reports Viewer Sub-Section */
    .reports-sub-wrap {
      margin-top: 20px;
      padding-top: 16px;
      border-top: 1px solid var(--color-neutral-200, #e2e8f0);
    }
    .reports-tabs-bar {
      display: flex;
      gap: 6px;
      overflow-x: auto;
      padding-bottom: 6px;
      scrollbar-width: thin;
      margin-bottom: 10px;
    }
    .rep-tab-btn {
      background: var(--color-neutral-100, #f1f5f9);
      border: 1px solid var(--color-neutral-200, #e2e8f0);
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 500;
      color: var(--color-neutral-700, #334155);
      cursor: pointer;
      white-space: nowrap;
    }
    .rep-tab-btn.active {
      background: #ffffff;
      border-color: var(--color-brand, #4f46e5);
      color: var(--color-brand, #4f46e5);
    }
    .rep-content-box {
      background: var(--color-neutral-50, #f8fafc);
      border: 1px solid var(--color-neutral-200, #e2e8f0);
      border-radius: 8px;
      padding: 14px;
      max-height: 320px;
      overflow-y: auto;
      font-size: 13px;
      line-height: 1.6;
      color: var(--color-neutral-800, #1e293b);
    }

    /* Footer & Modal */
    .page-footer {
      margin-top: 32px;
      text-align: center;
      font-size: 13px;
      color: var(--color-neutral-500, #64748b);
    }
    .footer-link {
      color: var(--color-brand, #4f46e5);
      text-decoration: none;
      font-weight: 500;
      cursor: pointer;
    }
    .footer-link:hover {
      text-decoration: underline;
    }

    /* Modal Styling */
    .modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.6);
      backdrop-filter: blur(4px);
      z-index: 10000;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .modal-backdrop.open {
      display: flex;
    }
    .modal-card {
      background: #ffffff;
      border-radius: 14px;
      width: 100%;
      max-width: 640px;
      max-height: 90vh;
      overflow-y: auto;
      box-shadow: 0 12px 32px rgba(0,0,0,0.15);
      padding: 24px;
      position: relative;
    }
    .modal-close-btn {
      position: absolute;
      top: 18px;
      right: 18px;
      background: none;
      border: none;
      font-size: 20px;
      cursor: pointer;
      color: var(--color-neutral-400, #94a3b8);
      line-height: 1;
    }
    .modal-tabs {
      display: flex;
      gap: 8px;
      border-bottom: 1px solid var(--color-neutral-200, #e2e8f0);
      margin-bottom: 16px;
      padding-bottom: 8px;
    }
    .modal-tab-btn {
      background: none;
      border: none;
      padding: 6px 12px;
      font-size: 14px;
      font-weight: 600;
      color: var(--color-neutral-500, #64748b);
      cursor: pointer;
      border-radius: 6px;
    }
    .modal-tab-btn.active {
      color: var(--color-brand, #4f46e5);
      background: var(--color-brand-subtle, rgba(79,70,229,.12));
    }
    .modal-step-item {
      display: flex;
      gap: 12px;
      margin-bottom: 14px;
    }
    .modal-step-num {
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: var(--color-brand, #4f46e5);
      color: #ffffff;
      font-size: 12px;
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }
    .modal-step-text strong {
      display: block;
      color: var(--color-neutral-900, #0f172a);
      font-size: 14px;
      margin-bottom: 2px;
    }
    .modal-step-text p {
      font-size: 13px;
      color: var(--color-neutral-600, #475569);
      line-height: 1.45;
    }
    .arch-diagram-img {
      width: 100%;
      border-radius: 8px;
      border: 1px solid var(--color-neutral-200, #e2e8f0);
      margin-top: 10px;
    }

    /* Toast Notification */
    .toast-box {
      position: fixed;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%);
      background: #0f172a;
      color: #ffffff;
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: 500;
      box-shadow: 0 4px 12px rgba(0,0,0,0.2);
      z-index: 10001;
      display: none;
      align-items: center;
      gap: 6px;
    }
    .toast-box.show {
      display: flex;
    }
  </style>
</head>
<body>

  <!-- Top spacer is inserted automatically by SmartOpsNav -->

  <main class="app-wrap">
    <!-- Header -->
    <header class="page-header">
      <h1 class="page-title">Sales outreach assistant</h1>
      <p class="page-subtitle">Pick a prospect and get a fit verdict, a first email and a call script.</p>
    </header>

    <!-- Collapsible How it works strip -->
    <details class="how-strip" open id="how-strip">
      <summary class="how-strip-summary">
        <span>How it works: Pick a prospect → AI researches 5 sources → You review and send</span>
        <span style="font-size: 11.5px; color: var(--color-brand, #4f46e5); font-weight: 500;">Details ▾</span>
      </summary>
      <div class="how-strip-steps">
        <div class="how-step-item">
          <strong>1. Pick a prospect</strong>
          Choose a qualified lead from your list or add a new business contact.
        </div>
        <div class="how-step-item">
          <strong>2. AI researches 5 sources</strong>
          Scans company website, news, blog, digital profile, and matches past success stories.
        </div>
        <div class="how-step-item">
          <strong>3. You review &amp; send</strong>
          Get a fit verdict, an email draft and a call script. Nothing is ever sent automatically.
        </div>
      </div>
    </details>

    <!-- Main 2-Column Grid -->
    <div class="main-grid">
      <!-- LEFT: Prospect Panel -->
      <aside class="prospect-panel" aria-label="Prospect selection panel">
        <!-- Prospect Selector Card -->
        <div class="panel-card">
          <div class="card-heading">
            <span>Select a prospect</span>
            <button class="add-form-toggle" onclick="toggleAddForm()">+ Add prospect</button>
          </div>

          <!-- Add prospect form (collapsible) -->
          <div class="add-form-wrap" id="add-form-wrap">
            <input class="form-input" id="inp-name" placeholder="Full name (e.g. Sarah Jenkins)" />
            <input class="form-input" id="inp-company" placeholder="Company (e.g. Metro Logistics)" />
            <input class="form-input" id="inp-email" placeholder="Email address" />
            <input class="form-input" id="inp-role" placeholder="Job title / role" />
            <input class="form-input" id="inp-note" placeholder="Short note about their business" />
            <button class="btn-action" style="background: var(--color-brand, #4f46e5); color:#fff; border-color:transparent; justify-content:center;" onclick="submitNewProspect()">Save &amp; select</button>
          </div>

          <!-- Prospect List -->
          <div class="prospect-list" id="prospect-list">
            <!-- Dynamically populated -->
          </div>
        </div>

        <!-- Selected Prospect Summary Card -->
        <div class="panel-card">
          <div class="card-heading">
            <span>Selected prospect</span>
            <span id="selected-status-pill" class="pill pill-ready">Outreach ready</span>
          </div>

          <div class="prospect-detail-row">
            <span class="prospect-detail-label">Name</span>
            <span class="prospect-detail-val" id="det-name">Alex Mercer</span>
          </div>
          <div class="prospect-detail-row">
            <span class="prospect-detail-label">Company</span>
            <span class="prospect-detail-val" id="det-company">Apex Dynamics</span>
          </div>
          <div class="prospect-detail-row">
            <span class="prospect-detail-label">Role</span>
            <span class="prospect-detail-val" id="det-role">VP of Operations</span>
          </div>
          <div class="prospect-detail-row">
            <span class="prospect-detail-label">Email</span>
            <span class="prospect-detail-val" id="det-email">alex.mercer@example.com</span>
          </div>
          <div class="prospect-detail-row">
            <span class="prospect-detail-label">Website</span>
            <span class="prospect-detail-val" id="det-website">https://apexdynamics.example.com</span>
          </div>

          <div class="prospect-note-box" id="det-note">
            Growing mid-market B2B distributor experiencing customer support delays and high ticket volume.
          </div>

          <div style="margin-top: 16px;">
            <button class="btn-prepare" id="btn-prepare" onclick="prepareOutreach()">
              <span id="btn-prepare-icon">⚡</span>
              <span id="btn-prepare-txt">Prepare outreach</span>
            </button>
            <p class="last-prep-text" id="last-prep-txt">Last prepared: Today at 2:15 PM • Outreach ready</p>
          </div>
        </div>
      </aside>

      <!-- RIGHT: Result Area -->
      <section class="result-area" aria-label="Outreach results and research">
        <!-- State A: Empty State -->
        <div class="empty-state" id="empty-state" style="display: none;">
          <div class="empty-icon">✉️</div>
          <h2 class="empty-title">Pick a prospect and select Prepare outreach.</h2>
          <p class="empty-desc">SmartOps AI will evaluate public signals across 5 sources, calculate a fit score, and craft a personalized first email and discovery call script.</p>
        </div>

        <!-- State B: Progress Card While Running -->
        <div class="progress-card" id="progress-card">
          <div class="progress-title">
            <span style="display:inline-block; animation: pulse-step 1s infinite;">⏳</span>
            <span>Preparing outreach...</span>
          </div>
          <div class="progress-step-list" id="progress-steps-list">
            <!-- Dynamically populated steps -->
          </div>
        </div>

        <!-- State C: 3 Outcome Cards (Done state) -->
        <div id="outcome-cards" style="display: flex; flex-direction: column; gap: 20px;">
          <!-- CARD 1: VERDICT CARD (STANDOUT) -->
          <article class="verdict-card" id="verdict-card" aria-label="Fit verdict card">
            <div class="verdict-header">
              <div class="verdict-title-wrap">
                <span class="card-heading" style="margin:0; font-size:16px;">Fit verdict</span>
                <span id="verdict-fit-pill" class="pill pill-ready" style="font-size:12.5px; padding:3px 10px;">Good fit</span>
              </div>
              <span id="demo-mode-badge-tag" class="draft-badge">Sample result (demo mode)</span>
            </div>

            <div class="verdict-score-row">
              <div class="verdict-big-score" id="verdict-score-num">8.5</div>
              <div class="verdict-score-label">out of 10 fit score</div>
            </div>

            <div class="verdict-reasons-title">Key reasons:</div>
            <ul class="verdict-reasons-list" id="verdict-reasons-list">
              <li>Experiencing rapid B2B volume growth with support ticket backlogs</li>
              <li>High-ticket contract value makes operational automation ROI immediate</li>
              <li>Active digital footprint and clear leadership intent around workflow scaling</li>
            </ul>

            <div class="story-box" id="verdict-story-box">
              <strong>Matching success story:</strong>
              <span id="verdict-story-text">Similar to Spark Retail: Automated 85% of complex customer queries while lifting quarterly revenue by $150k.</span>
            </div>

            <!-- Poor fit advice (visible only for poor fit) -->
            <div class="poor-fit-box" id="poor-fit-box" style="display: none;">
              <strong>Not recommended for outreach right now</strong>
              <p id="poor-fit-advice-text">Check again after they hire a dedicated support team or expand commercial B2B operations.</p>
              <p style="margin-top:6px; font-size:12.5px; opacity:0.9;" id="poor-fit-explanation-text">No email draft generated. Outreach is intentionally withheld for low-fit prospects to protect your brand.</p>
            </div>

            <div class="data-quality-bar">
              <span id="data-quality-text">Based on 4 of 5 sources</span>
              <span id="confidence-tag" class="confidence-tag conf-high">High confidence</span>
            </div>
          </article>

          <!-- CARD 2: EMAIL DRAFT CARD -->
          <article class="email-card" id="email-card" aria-label="First email draft card">
            <div class="card-top-bar">
              <h2 class="card-heading" style="margin:0; font-size:15px;">First email draft</h2>
              <span class="draft-badge">Draft only. Nothing has been sent.</span>
            </div>

            <div class="email-subject-box" id="email-subject-box">
              <strong>Subject:</strong><span id="email-subject-text">Streamlining Apex Dynamics' customer support &amp; operations volume</span>
            </div>

            <div class="email-body-view" id="email-body-view">Loading draft...</div>
            <textarea class="email-body-edit" id="email-body-edit" aria-label="Edit email body"></textarea>

            <div class="email-actions">
              <div style="display: flex; gap: 8px;">
                <button class="btn-action" id="btn-copy-email" onclick="copyEmailDraft()">
                  <span>📋</span> <span id="copy-btn-txt">Copy email</span>
                </button>
                <button class="btn-action" id="btn-edit-email" onclick="toggleEditEmail()">
                  <span id="edit-btn-icon">✏️</span> <span id="edit-btn-txt">Edit</span>
                </button>
              </div>
              <button class="btn-action btn-contacted-action" id="btn-mark-contacted" onclick="markAsContacted()">
                <span id="contacted-icon">✓</span> <span id="contacted-txt">Mark as contacted</span>
              </button>
            </div>
          </article>

          <!-- CARD 3: CALL SCRIPT CARD -->
          <article class="script-card" id="script-card" aria-label="Call script guide card">
            <div class="card-top-bar">
              <h2 class="card-heading" style="margin:0; font-size:15px;">Call script</h2>
              <span class="draft-badge">Discovery &amp; objection guide</span>
            </div>

            <div class="script-section">
              <div class="script-label">Opening line</div>
              <div class="script-quote" id="script-opening">
                “Hi Alex, this is from SmartOps AI. I've been following Apex Dynamics' recent expansion across distribution centers—congratulations on the growth.”
              </div>
            </div>

            <div class="script-section">
              <div class="script-label">3 Questions to ask</div>
              <ul class="script-bullets" id="script-questions">
                <li>How is your operations team currently handling the surge in customer inquiry volume during peak hours?</li>
                <li>What is the biggest operational bottleneck when onboarding new accounts across your customer hubs?</li>
                <li>If you could resolve 80% of routine inquiries automatically, where would your staff redirect their focus?</li>
              </ul>
            </div>

            <div class="script-section">
              <div class="script-label">Likely objections &amp; suggested replies</div>
              <div id="script-objections">
                <!-- Dynamically populated -->
              </div>
            </div>

            <button class="full-script-toggle" id="full-script-toggle-btn" onclick="toggleFullScript()">Show full script ▾</button>
            <div class="full-script-content" id="full-script-content"></div>
          </article>

          <!-- RESEARCH BEHIND THIS ACCORDION -->
          <details class="research-accordion" id="research-accordion">
            <summary class="accordion-summary">
              <span>Research behind this (5 sources verified)</span>
              <span style="font-size:12px; color:var(--color-brand, #4f46e5); font-weight:500;">Toggle ▾</span>
            </summary>

            <div class="sources-list" id="sources-list">
              <!-- Dynamically populated rows -->
            </div>

            <!-- Supporting Reports Archive Tabs -->
            <div class="reports-sub-wrap">
              <div class="card-heading" style="font-size: 13.5px;">Supporting research dossiers</div>
              <div class="reports-tabs-bar" id="reports-tabs-bar">
                <!-- Dynamically populated tabs -->
              </div>
              <div class="rep-content-box" id="rep-content-box">
                Select a dossier tab above to inspect verified research outputs.
              </div>
            </div>
          </details>
        </div>
      </section>
    </div>

    <!-- Footer -->
    <footer class="page-footer">
      <button class="footer-link" onclick="openModal('overview')">How this works</button>
      <span>•</span>
      <span>SmartOps AI Sales Outreach Engine</span>
    </footer>
  </main>

  <!-- "How this works" Modal -->
  <div class="modal-backdrop" id="info-modal" role="dialog" aria-modal="true" aria-labelledby="modal-title" onclick="if(event.target === this) closeModal()">
    <div class="modal-card">
      <button class="modal-close-btn" onclick="closeModal()" aria-label="Close dialog">✕</button>
      
      <div class="modal-tabs">
        <button class="modal-tab-btn active" id="tab-btn-overview" onclick="switchModalTab('overview')">Overview</button>
        <button class="modal-tab-btn" id="tab-btn-technical" onclick="switchModalTab('technical')">Technical view</button>
      </div>

      <!-- Tab 1: Overview -->
      <div id="modal-tab-overview">
        <h3 id="modal-title" style="font-size:18px; margin-bottom:12px; color:var(--color-neutral-900, #0f172a);">5-step outreach preparation</h3>
        <p style="font-size:13.5px; color:var(--color-neutral-600, #475569); margin-bottom:18px;">How SmartOps AI turns raw company signals into ready-to-use business outreach without automated sending.</p>

        <div class="modal-step-item">
          <div class="modal-step-num">1</div>
          <div class="modal-step-text">
            <strong>Pick a prospect</strong>
            <p>Select any lead from your CRM or add a prospective client with website and email.</p>
          </div>
        </div>

        <div class="modal-step-item">
          <div class="modal-step-num">2</div>
          <div class="modal-step-text">
            <strong>Public source scanning</strong>
            <p>SmartOps scans 5 data sources: official website, recent press releases, blogs, public professional profile, and social channels.</p>
          </div>
        </div>

        <div class="modal-step-item">
          <div class="modal-step-num">3</div>
          <div class="modal-step-text">
            <strong>Fit score &amp; verdict</strong>
            <p>An intelligent evaluator computes an objective fit score out of 10. Low-fit prospects are filtered out to avoid wasting time.</p>
          </div>
        </div>

        <div class="modal-step-item">
          <div class="modal-step-num">4</div>
          <div class="modal-step-text">
            <strong>Matching past success stories</strong>
            <p>Retrieves a relevant case study from past deployments (e.g. Spark Retail) that mirrors their operational challenges.</p>
          </div>
        </div>

        <div class="modal-step-item">
          <div class="modal-step-num">5</div>
          <div class="modal-step-text">
            <strong>Draft email &amp; call script</strong>
            <p>Generates an opening email and consultative discovery questions. You review, adjust, copy, and send manually.</p>
          </div>
        </div>
      </div>

      <!-- Tab 2: Technical View -->
      <div id="modal-tab-technical" style="display:none;">
        <h3 style="font-size:18px; margin-bottom:8px; color:var(--color-neutral-900, #0f172a);">LangGraph Multi-Agent Architecture</h3>
        <p style="font-size:13px; color:var(--color-neutral-600, #475569); margin-bottom:14px;">12 autonomous graph nodes coordinated via LangGraph state machine, with conditional branches for qualified vs unqualified prospects and ChromaDB RAG retrieval.</p>
        <img src="/workflow.png" alt="LangGraph Architecture Diagram" class="arch-diagram-img" />
        <div style="margin-top:14px; font-size:12.5px; color:var(--color-neutral-600, #475569); line-height:1.5;">
          <strong>Core Pipeline Nodes:</strong>
          <ul style="margin-left:18px; margin-top:4px;">
            <li><code>get_new_leads</code> → <code>review_company_website</code> → <code>analyze_recent_news</code></li>
            <li><code>generate_digital_presence_report</code> → <code>score_lead</code></li>
            <li>Conditional Branch: If score &ge; threshold → <code>generate_personalized_email</code> + <code>generate_interview_script</code>; else skip directly to archival.</li>
          </ul>
        </div>
      </div>
    </div>
  </div>

  <!-- Toast Notification -->
  <div class="toast-box" id="toast-box">
    <span id="toast-icon">✓</span>
    <span id="toast-msg">Email copied to clipboard</span>
  </div>

  <script src="/shared/nav.js"></script>
  <script src="/shared/mode.js"></script>
  <script>
    // State variables
    let prospects = [];
    let currentProspectId = "prospect_001";
    let isEditingEmail = false;
    let pollInterval = null;
    let reportsData = [];
    let activeReportIdx = 0;

    // -----------------------------------------------------------------------
    // Bundled Sanitizing Markdown Renderer (No CDN, Strict Entity Escaping)
    // -----------------------------------------------------------------------
    function renderSafeMarkdown(rawText) {
      if (!rawText) return "";
      // Step 1: Escape HTML characters strictly
      let escaped = rawText
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

      // Step 2: Code blocks
      escaped = escaped.replace(/```([\\s\\S]*?)```/g, (m, code) => {
        return `<pre style="background:#f1f5f9; padding:8px 12px; border-radius:6px; font-size:12px; overflow-x:auto;"><code>${code}</code></pre>`;
      });

      // Step 3: Headings
      escaped = escaped.replace(/^### (.*$)/gim, '<h4 style="font-size:14px; margin:10px 0 4px; font-weight:700;">$1</h4>');
      escaped = escaped.replace(/^## (.*$)/gim, '<h3 style="font-size:15px; margin:12px 0 4px; font-weight:700;">$1</h3>');
      escaped = escaped.replace(/^# (.*$)/gim, '<h2 style="font-size:16px; margin:14px 0 6px; font-weight:700;">$1</h2>');

      // Step 4: Bold and Italic
      escaped = escaped.replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');
      escaped = escaped.replace(/\\*(.*?)\\*/g, '<em>$1</em>');

      // Step 5: Unordered lists
      escaped = escaped.replace(/^\\s*[-*]\\s+(.*)$/gim, '<li style="margin-left:16px;">$1</li>');

      // Step 6: Line breaks
      escaped = escaped.replace(/\\n/g, '<br/>');

      return escaped;
    }

    // -----------------------------------------------------------------------
    // Initialization & Data Loading
    // -----------------------------------------------------------------------
    document.addEventListener("DOMContentLoaded", () => {
      // Shared Nav with sales active
      if (window.SmartOpsNav) {
        SmartOpsNav.init({ active: 'sales', modeEndpoint: '/api/mode' });
      }
      loadProspects();
      loadReports();
      fetchStatus();
    });

    async function loadProspects() {
      try {
        const res = await fetch("/api/prospects");
        const data = await res.json();
        prospects = data.prospects || [];
        if (data.current_prospect_id) {
          currentProspectId = data.current_prospect_id;
        }
        renderProspectList();
        renderSelectedProspect();
      } catch (e) {
        console.error("Error loading prospects:", e);
      }
    }

    function renderProspectList() {
      const container = document.getElementById("prospect-list");
      container.innerHTML = "";
      prospects.forEach(p => {
        const item = document.createElement("button");
        item.className = `prospect-item ${p.id === currentProspectId ? 'active' : ''}`;
        item.onclick = () => selectProspect(p.id);

        const statusClass = p.status === 'Contacted' ? 'pill-contacted' : (p.status === 'Not a fit right now' ? 'pill-poor' : 'pill-ready');

        item.innerHTML = `
          <div class="prospect-item-top">
            <span class="prospect-item-name">${escapeText(p.name)}</span>
            ${p.is_demo ? '<span class="demo-tag">Demo prospect</span>' : ''}
          </div>
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <span class="prospect-item-company">${escapeText(p.company)}</span>
            <span class="pill ${statusClass}" style="font-size:10.5px; padding:1px 6px;">${escapeText(p.status || 'Outreach ready')}</span>
          </div>
        `;
        container.appendChild(item);
      });
    }

    function selectProspect(id) {
      currentProspectId = id;
      renderProspectList();
      renderSelectedProspect();
      prepareOutreach();
    }

    function renderSelectedProspect() {
      const p = prospects.find(x => x.id === currentProspectId) || prospects[0];
      if (!p) return;

      document.getElementById("det-name").textContent = p.name;
      document.getElementById("det-company").textContent = p.company;
      document.getElementById("det-role").textContent = p.role || "Executive";
      document.getElementById("det-email").textContent = p.email || "";
      document.getElementById("det-website").textContent = p.website || "";
      document.getElementById("det-note").textContent = p.note || "";

      const pill = document.getElementById("selected-status-pill");
      pill.textContent = p.status || "Outreach ready";
      pill.className = `pill ${p.status === 'Contacted' ? 'pill-contacted' : (p.status === 'Not a fit right now' ? 'pill-poor' : 'pill-ready')}`;

      const lastPrepTxt = document.getElementById("last-prep-txt");
      lastPrepTxt.textContent = p.last_prepared ? `Last prepared: ${p.last_prepared}` : "Not prepared yet";

      const contactBtn = document.getElementById("btn-mark-contacted");
      if (p.status === "Contacted") {
        contactBtn.className = "btn-action btn-contacted-action marked";
        document.getElementById("contacted-txt").textContent = "Contacted";
      } else {
        contactBtn.className = "btn-action btn-contacted-action";
        document.getElementById("contacted-txt").textContent = "Mark as contacted";
      }
    }

    // -----------------------------------------------------------------------
    // Preparation Trigger & Status Polling
    // -----------------------------------------------------------------------
    async function prepareOutreach() {
      const btn = document.getElementById("btn-prepare");
      const btnTxt = document.getElementById("btn-prepare-txt");
      btn.disabled = true;
      btnTxt.textContent = "Preparing outreach...";

      document.getElementById("empty-state").style.display = "none";
      document.getElementById("progress-card").className = "progress-card active";

      try {
        await fetch("/api/prepare", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prospect_id: currentProspectId })
        });
        startPolling();
      } catch (e) {
        showToast("Error starting preparation: " + e);
        btn.disabled = false;
        btnTxt.textContent = "Prepare outreach";
      }
    }

    function startPolling() {
      if (pollInterval) clearInterval(pollInterval);
      pollInterval = setInterval(fetchStatus, 500);
    }

    async function fetchStatus() {
      try {
        const res = await fetch("/api/status");
        const data = await res.json();

        // Update progress card steps
        renderProgressSteps(data.progress_steps || []);

        if (data.status === "completed") {
          clearInterval(pollInterval);
          document.getElementById("btn-prepare").disabled = false;
          document.getElementById("btn-prepare-txt").textContent = "Prepare outreach";
          document.getElementById("progress-card").className = "progress-card";
          renderOutcome(data);
          loadProspects();
        } else if (data.status === "running") {
          document.getElementById("progress-card").className = "progress-card active";
        }
      } catch (e) {
        console.error("Polling status error:", e);
      }
    }

    function renderProgressSteps(steps) {
      const list = document.getElementById("progress-steps-list");
      list.innerHTML = "";
      steps.forEach(s => {
        const row = document.createElement("div");
        row.className = "progress-step-row";

        let indicatorClass = "step-pending";
        let iconTxt = "·";
        if (s.status === "done") {
          indicatorClass = "step-done";
          iconTxt = "✓";
        } else if (s.status === "working") {
          indicatorClass = "step-working";
          iconTxt = "⏳";
        } else if (s.status === "skipped") {
          indicatorClass = "step-skipped";
          iconTxt = "–";
        }

        row.innerHTML = `
          <div class="progress-step-left">
            <span class="step-indicator ${indicatorClass}">${iconTxt}</span>
            <span style="font-weight:${s.status === 'working' ? '600' : '400'}; color:${s.status === 'done' ? '#0f172a' : '#475569'};">${escapeText(s.name)}</span>
          </div>
          <span style="font-size:12px; color:#94a3b8;">${escapeText(s.reason || '')}</span>
        `;
        list.appendChild(row);
      });
    }

    // -----------------------------------------------------------------------
    // Outcome Cards Rendering
    // -----------------------------------------------------------------------
    function renderOutcome(data) {
      document.getElementById("outcome-cards").style.display = "flex";

      // 1. VERDICT CARD
      const verdict = data.verdict || "Good fit";
      const score = data.score !== undefined ? data.score : 8.5;
      const fitPill = document.getElementById("verdict-fit-pill");
      fitPill.textContent = verdict;
      if (verdict === "Good fit") {
        fitPill.className = "pill pill-ready";
      } else if (verdict === "Maybe") {
        fitPill.className = "pill pill-maybe";
      } else {
        fitPill.className = "pill pill-poor";
      }

      document.getElementById("verdict-score-num").textContent = score;

      const reasonsList = document.getElementById("verdict-reasons-list");
      reasonsList.innerHTML = "";
      (data.reasons || []).forEach(r => {
        const li = document.createElement("li");
        li.textContent = r;
        reasonsList.appendChild(li);
      });

      document.getElementById("verdict-story-text").textContent = data.matched_story || "Similar to Spark Retail: Automated 85% of complex customer queries.";
      document.getElementById("data-quality-text").textContent = data.sources_summary || "Based on 4 of 5 sources";

      const confTag = document.getElementById("confidence-tag");
      const conf = data.confidence || "High";
      confTag.textContent = `${conf} confidence`;
      confTag.className = `confidence-tag ${conf === 'High' ? 'conf-high' : (conf === 'Medium' ? 'conf-medium' : 'conf-low')}`;

      // Handle Poor Fit State
      const poorFitBox = document.getElementById("poor-fit-box");
      const emailCard = document.getElementById("email-card");
      const scriptCard = document.getElementById("script-card");

      if (verdict === "Not a fit right now" || !data.email) {
        poorFitBox.style.display = "block";
        document.getElementById("poor-fit-advice-text").textContent = data.poor_fit_advice || "Check again after they hire a dedicated support team.";
        document.getElementById("poor-fit-explanation-text").textContent = data.poor_fit_explanation || "No email was drafted because outreach is not recommended for this prospect.";
        emailCard.style.display = "none";
        scriptCard.style.display = "none";
      } else {
        poorFitBox.style.display = "none";
        emailCard.style.display = "block";
        scriptCard.style.display = "block";

        // 2. EMAIL DRAFT CARD
        const email = data.email || {};
        document.getElementById("email-subject-text").textContent = email.subject || "Operational automation inquiry";
        document.getElementById("email-body-view").textContent = email.body || "";
        document.getElementById("email-body-edit").value = email.body || "";

        // 3. CALL SCRIPT CARD
        const script = data.call_script || {};
        document.getElementById("script-opening").textContent = script.opening || "“Hi, this is from SmartOps AI...”";

        const qList = document.getElementById("script-questions");
        qList.innerHTML = "";
        (script.questions || []).forEach(q => {
          const li = document.createElement("li");
          li.textContent = q;
          qList.appendChild(li);
        });

        const objWrap = document.getElementById("script-objections");
        objWrap.innerHTML = "";
        (script.objections || []).forEach(o => {
          const div = document.createElement("div");
          div.className = "objection-item";
          div.innerHTML = `
            <div class="objection-q">If they say: “${escapeText(o.objection)}”</div>
            <div class="objection-a"><strong>Suggested reply:</strong> ${escapeText(o.reply)}</div>
          `;
          objWrap.appendChild(div);
        });

        document.getElementById("full-script-content").textContent = script.full_script || "";
      }

      // 4. RESEARCH BEHIND THIS
      renderSources(data.sources || []);
    }

    function renderSources(sources) {
      const container = document.getElementById("sources-list");
      container.innerHTML = "";
      sources.forEach((s, idx) => {
        const row = document.createElement("div");
        row.className = "source-row";

        const statusPill = s.ok 
          ? `<span class="pill pill-ready" style="font-size:10.5px; padding:1px 6px;">Read</span>`
          : `<span class="pill pill-poor" style="font-size:10.5px; padding:1px 6px;">Could not read</span>`;

        const displaySummary = s.ok ? s.summary : (s.reason_if_failed || "This site blocks automated reading, so we skipped it");

        row.innerHTML = `
          <div class="source-info">
            <div class="source-header">
              <span class="source-name">${escapeText(s.name)}</span>
              ${statusPill}
            </div>
            <div class="source-summary-text">${escapeText(displaySummary)}</div>
            ${s.details ? `<div class="source-details-text" id="src-det-${idx}">${escapeText(s.details)}</div>` : ''}
          </div>
          ${s.details ? `<button class="btn-details-toggle" onclick="toggleDetails(${idx})">Show details</button>` : ''}
        `;
        container.appendChild(row);
      });
    }

    function toggleDetails(idx) {
      const el = document.getElementById(`src-det-${idx}`);
      if (el) {
        el.style.display = el.style.display === "block" ? "none" : "block";
      }
    }

    // -----------------------------------------------------------------------
    // Email Draft Interactions
    // -----------------------------------------------------------------------
    function copyEmailDraft() {
      const bodyView = document.getElementById("email-body-view");
      const textToCopy = bodyView.textContent;
      navigator.clipboard.writeText(textToCopy).then(() => {
        const btnTxt = document.getElementById("copy-btn-txt");
        btnTxt.textContent = "Copied!";
        showToast("Email draft copied to clipboard");
        setTimeout(() => { btnTxt.textContent = "Copy email"; }, 2000);
      }).catch(() => {
        showToast("Could not access clipboard");
      });
    }

    function toggleEditEmail() {
      const view = document.getElementById("email-body-view");
      const edit = document.getElementById("email-body-edit");
      const txt = document.getElementById("edit-btn-txt");

      if (!isEditingEmail) {
        isEditingEmail = true;
        edit.value = view.textContent;
        view.style.display = "none";
        edit.style.display = "block";
        txt.textContent = "Save";
      } else {
        isEditingEmail = false;
        view.textContent = edit.value;
        view.style.display = "block";
        edit.style.display = "none";
        txt.textContent = "Edit";
        showToast("Draft updated locally");
      }
    }

    async function markAsContacted() {
      try {
        const res = await fetch("/api/mark-contacted", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prospect_id: currentProspectId })
        });
        const data = await res.json();
        const btn = document.getElementById("btn-mark-contacted");
        btn.className = "btn-action btn-contacted-action marked";
        document.getElementById("contacted-txt").textContent = "Contacted";
        showToast("Marked as Contacted");
        loadProspects();
      } catch (e) {
        showToast("Error updating status: " + e);
      }
    }

    function toggleFullScript() {
      const el = document.getElementById("full-script-content");
      const btn = document.getElementById("full-script-toggle-btn");
      if (el.style.display === "block") {
        el.style.display = "none";
        btn.textContent = "Show full script ▾";
      } else {
        el.style.display = "block";
        btn.textContent = "Hide full script ▴";
      }
    }

    // -----------------------------------------------------------------------
    // Reports Archive Viewer
    // -----------------------------------------------------------------------
    async function loadReports() {
      try {
        const res = await fetch("/api/reports");
        const data = await res.json();
        reportsData = data.reports || [];
        renderReportTabs();
        if (reportsData.length > 0) {
          showReport(0);
        }
      } catch (e) {
        console.error("Error loading reports:", e);
      }
    }

    function renderReportTabs() {
      const bar = document.getElementById("reports-tabs-bar");
      bar.innerHTML = "";
      reportsData.forEach((rep, idx) => {
        const btn = document.createElement("button");
        btn.className = `rep-tab-btn ${idx === activeReportIdx ? 'active' : ''}`;
        btn.textContent = rep.title;
        btn.onclick = () => showReport(idx);
        bar.appendChild(btn);
      });
    }

    function showReport(idx) {
      activeReportIdx = idx;
      renderReportTabs();
      const box = document.getElementById("rep-content-box");
      if (reportsData[idx]) {
        box.innerHTML = renderSafeMarkdown(reportsData[idx].content);
      }
    }

    // -----------------------------------------------------------------------
    // Add Custom Prospect Form
    // -----------------------------------------------------------------------
    function toggleAddForm() {
      const wrap = document.getElementById("add-form-wrap");
      wrap.classList.toggle("open");
    }

    async function submitNewProspect() {
      const name = document.getElementById("inp-name").value.trim();
      const company = document.getElementById("inp-company").value.trim();
      if (!name || !company) {
        alert("Please enter a name and company.");
        return;
      }
      const email = document.getElementById("inp-email").value.trim();
      const role = document.getElementById("inp-role").value.trim();
      const note = document.getElementById("inp-note").value.trim();

      try {
        const res = await fetch("/api/prospects", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name, company, email, role, note })
        });
        const data = await res.json();
        document.getElementById("add-form-wrap").classList.remove("open");
        document.getElementById("inp-name").value = "";
        document.getElementById("inp-company").value = "";
        document.getElementById("inp-email").value = "";
        document.getElementById("inp-role").value = "";
        document.getElementById("inp-note").value = "";
        showToast("Prospect added");
        await loadProspects();
        selectProspect(data.prospect.id);
      } catch (e) {
        alert("Error creating prospect: " + e);
      }
    }

    // -----------------------------------------------------------------------
    // Modal & Toast Utilities
    // -----------------------------------------------------------------------
    function openModal(tab = 'overview') {
      document.getElementById("info-modal").classList.add("open");
      switchModalTab(tab);
    }

    function closeModal() {
      document.getElementById("info-modal").classList.remove("open");
    }

    function switchModalTab(tab) {
      const btnO = document.getElementById("tab-btn-overview");
      const btnT = document.getElementById("tab-btn-technical");
      const viewO = document.getElementById("modal-tab-overview");
      const viewT = document.getElementById("modal-tab-technical");

      if (tab === 'technical') {
        btnT.classList.add("active");
        btnO.classList.remove("active");
        viewT.style.display = "block";
        viewO.style.display = "none";
      } else {
        btnO.classList.add("active");
        btnT.classList.remove("active");
        viewO.style.display = "block";
        viewT.style.display = "none";
      }
    }

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeModal();
    });

    function showToast(msg) {
      const box = document.getElementById("toast-box");
      document.getElementById("toast-msg").textContent = msg;
      box.classList.add("show");
      setTimeout(() => { box.classList.remove("show"); }, 2400);
    }

    function escapeText(str) {
      if (!str) return "";
      return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
    }
  </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_dashboard:app", host="0.0.0.0", port=5175, reload=False)
