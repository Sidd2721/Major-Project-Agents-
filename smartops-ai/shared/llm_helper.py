"""
SmartOps AI — Shared LLM Helper & Mode Manager
Provides unified LLM mode handling ('live', 'mock', 'replay'),
provider failover (Groq -> Gemini -> Mock), and dynamic model resolution.
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("smartops.llm")

def get_llm_mode() -> str:
    """Returns 'live', 'mock', or 'replay'. Defaults to 'mock' if no keys set."""
    mode = os.getenv("LLM_MODE", "").lower().strip()
    if mode in {"live", "mock", "replay"}:
        return mode
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("GOOGLE_API_KEY", "").strip()
    if (groq_key and "REPLACE" not in groq_key and "your_" not in groq_key and len(groq_key) > 15) or \
       (gemini_key and "REPLACE" not in gemini_key and "your_" not in gemini_key and len(gemini_key) > 15):
        return "live"
    return "mock"

def resolve_groq_model(api_key: str) -> str:
    """Dynamically resolves the active Groq model."""
    preferred = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "llama-3.1-70b-versatile",
        "mixtral-8x7b-32768"
    ]
    custom = os.getenv("GROQ_MODEL")
    if custom and not any(bad in custom for bad in ["gpt-oss", "qwen3.8"]):
        return custom
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        models = [m.id for m in client.models.list().data]
        for p in preferred:
            if p in models:
                return p
        if models:
            return models[0]
    except Exception as e:
        logger.warning(f"Could not query Groq models dynamically: {e}")
    return preferred[0]

def resolve_gemini_model(api_key: str) -> str:
    """Dynamically resolves active Gemini model."""
    preferred = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
    custom = os.getenv("GEMINI_MODEL")
    if custom and not any(bad in custom for bad in ["3.8", "3.5"]):
        return custom
    return preferred[0]

def mock_support_triage(complaint_text: str) -> Dict[str, Any]:
    """Generates deterministic, realistic triage result for Support Agent."""
    text_lower = complaint_text.lower()
    
    # Priority & sentiment detection
    is_p1 = any(w in text_lower for w in ["broken", "damage", "urgent", "fire", "smoke", "shattered", "emergency"])
    is_p2 = any(w in text_lower for w in ["delay", "wrong", "missing", "refund", "not working", "defect"])
    
    if is_p1:
        priority = "P1"
        priority_reason = "Physical defect / severe product damage detected with immediate replacement urgency"
        sentiment = "Negative"
        category = "Hardware / Defect"
        actions = ["1. Escalate to Tier-2 supervisor", "2. Issue prepaid return label", "3. Expedite replacement dispatch"]
    elif is_p2:
        priority = "P2"
        priority_reason = "Delivery discrepancy or service disruption impacting customer workflow"
        sentiment = "Negative"
        category = "Shipping & Logistics"
        actions = ["1. Trace tracking status with courier", "2. Verify order contents in warehouse log", "3. Issue customer goodwill credit"]
    else:
        priority = "P3"
        priority_reason = "Standard customer inquiry or cosmetic question"
        sentiment = "Neutral"
        category = "General Inquiry"
        actions = ["1. Provide standard operating guidance", "2. Check customer account history"]

    response_email = (
        f"Dear Customer,\n\n"
        f"Thank you for contacting SmartOps Support regarding your order. We have logged your ticket with priority {priority} "
        f"({priority_reason}).\n\n"
        f"Our support team has taken the following immediate steps:\n"
        f"{chr(10).join(actions)}\n\n"
        f"You can track real-time progress through our customer portal. A representative will update you within 2 hours.\n\n"
        f"Best regards,\nSmartOps Support AI Agent"
    )

    return {
        "is_valid": True,
        "validation_reason": "Legitimate business support request",
        "category": category,
        "sentiment": sentiment,
        "priority": priority,
        "priority_reason": priority_reason,
        "reevaluated_priority": priority,
        "escalation_required": (priority in ["P1", "P2"]),
        "suggestions": actions,
        "response_email": response_email,
        "mode": "mock"
    }

def mock_sales_run(lead_name: str, company: str, is_qualified: bool = True) -> Dict[str, Any]:
    """Generates realistic structured sales research and outreach with plain-language fields."""
    if is_qualified:
        score = 8.5
        verdict = "Good fit"
        confidence = "High"
        reasons = [
            "Experiencing rapid B2B volume growth with support ticket backlogs",
            "High-ticket contract value makes operational automation ROI immediate",
            "Active digital footprint and clear leadership intent around workflow scaling"
        ]
        sources = [
            {"name": "Website", "ok": True, "summary": "Company runs active multi-region operations with digital customer touchpoints.", "reason_if_failed": ""},
            {"name": "Blog", "ok": True, "summary": "Recent articles discuss scaling customer onboarding and workflow challenges.", "reason_if_failed": ""},
            {"name": "News", "ok": True, "summary": "Recent press releases announce operational expansion and team growth.", "reason_if_failed": ""},
            {"name": "Public profile", "ok": True, "summary": f"{lead_name} leads operational strategy and systems modernization.", "reason_if_failed": ""},
            {"name": "YouTube & social", "ok": False, "summary": "No active dedicated video channel found.", "reason_if_failed": "This site blocks automated reading, so we skipped it"}
        ]
        sources_summary = "Based on 4 of 5 sources"
        matched_story = "Similar to Spark Retail: Automated 85% of complex customer queries while lifting quarterly revenue by $150k."
        email = {
            "subject": f"Streamlining {company}'s customer support & operations volume",
            "body": (
                f"Hi {lead_name},\n\n"
                f"I noticed {company} is growing rapidly and handling higher customer inquiry volumes. Many operational leaders face communication delays during rapid scaling.\n\n"
                f"At SmartOps AI, we help businesses automate triage and customer follow-ups (similar to Spark Retail, which achieved 85% automated query resolution). "
                f"We'd love to share a 10-minute walkthrough of how our multi-agent workflows could lighten your team's support load.\n\n"
                f"Would you be open to a brief chat this Thursday?\n\n"
                f"Best,\nSmartOps AI Sales Team"
            )
        }
        legacy_email = email["body"]
        call_script = {
            "opening": f"Hi {lead_name}, this is from SmartOps AI. I've been following {company}'s recent growth—congratulations on the expansion.",
            "questions": [
                "How is your operations team currently handling the surge in customer inquiry volume during peak hours?",
                "What is the biggest operational bottleneck when onboarding new accounts across your customer hubs?",
                "If you could resolve 80% of routine inquiries automatically, where would your staff redirect their focus?"
            ],
            "objections": [
                {"objection": "We already have an existing CRM / ticketing setup.", "reply": "SmartOps doesn't replace your CRM; it works alongside it to triage tickets and draft responses automatically before your reps touch them."},
                {"objection": "Our team doesn't have bandwidth for a heavy software implementation.", "reply": "Setup takes under 2 hours with our lightweight API adapters, and there are no complex workflow overhauls required."}
            ]
        }
        poor_fit_advice = None
        poor_fit_explanation = None
    else:
        score = 2.8
        verdict = "Not a fit right now"
        confidence = "Low"
        reasons = [
            "Solo operator with no customer support queue or dedicated team",
            "No B2B sales motion or enterprise ticket queue to automate",
            "Budget and operational requirements do not match an agentic automation platform"
        ]
        sources = [
            {"name": "Website", "ok": True, "summary": "Personal site covering hobby topics and casual personal writing.", "reason_if_failed": ""},
            {"name": "Blog", "ok": True, "summary": "Informal opinion posts; no corporate products or business services offered.", "reason_if_failed": ""},
            {"name": "News", "ok": False, "summary": "Search returned zero verified press releases or commercial coverage.", "reason_if_failed": "This site blocks automated reading, so we skipped it"},
            {"name": "Public profile", "ok": False, "summary": "Profile indicates solo hobbyist without corporate organization.", "reason_if_failed": "This site blocks automated reading, so we skipped it"},
            {"name": "YouTube & social", "ok": False, "summary": "Personal hobby uploads only without commercial activity.", "reason_if_failed": "This site blocks automated reading, so we skipped it"}
        ]
        sources_summary = "Based on 2 of 5 sources"
        matched_story = "No matching enterprise story applicable."
        email = None
        legacy_email = ""
        call_script = None
        poor_fit_advice = "Check again after they hire a dedicated support team or expand commercial B2B operations."
        poor_fit_explanation = "No email was drafted because outreach is not recommended for this prospect. Preparing outreach for low-fit leads wastes time and risks company reputation."

    qualification = "qualified" if is_qualified else "unqualified"
    case_study = matched_story
    
    progress = [
        {"step": 1, "name": "Reading their website", "status": "done", "reason": "Indexed homepage and overview"},
        {"step": 2, "name": "Checking recent news", "status": "done" if is_qualified else "skipped", "reason": "Press releases analyzed" if is_qualified else "This site blocks automated reading, so we skipped it"},
        {"step": 3, "name": "Scoring the fit", "status": "done", "reason": f"Evaluated B2B fit criteria (Score: {score}/10)"},
        {"step": 4, "name": "Finding a matching success story", "status": "done" if is_qualified else "skipped", "reason": "Retrieved Spark Retail case study" if is_qualified else "Skipped for unqualified prospect"},
        {"step": 5, "name": "Writing the email", "status": "done" if is_qualified else "skipped", "reason": "Drafted personalized outreach" if is_qualified else "Omitted intentionally: prospect is not a fit right now"}
    ]

    return {
        # New plain-language result fields
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
        # Legacy compatibility fields
        "lead_name": lead_name,
        "company": company,
        "qualification_status": qualification,
        "lead_score": score,
        "matched_case_study": case_study,
        "outreach_email": legacy_email,
        "steps": [
            {"step": 1, "name": "Reading their website", "detail": f"Synthesized public business signals for {company}"},
            {"step": 2, "name": "Scoring the fit", "detail": f"Score {score}/10 -> {verdict}"},
            {"step": 3, "name": "Finding a matching success story", "detail": f"Matched '{case_study}'"},
            {"step": 4, "name": "Writing the email", "detail": "Generated personalized outreach draft" if is_qualified else "Skipped"}
        ],
        "mode": "mock"
    }

def get_support_db_context() -> str:
    """Reads compact summary from Support SQLite DB for Voice Agent grounding."""
    try:
        import sqlite3
        db_path = Path(__file__).resolve().parent.parent / "Customer-Support-Agent" / "complaints.db"
        if not db_path.exists():
            return "Support Database: 0 open tickets recorded."
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*), SUM(CASE WHEN priority='P1' THEN 1 ELSE 0 END), SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END) FROM complaints")
        row = cursor.fetchone()
        conn.close()
        total, p1_count, pending = row[0] or 0, row[1] or 0, row[2] or 0
        return f"Support System Snapshot: {total} total tickets recorded ({pending} pending, {p1_count} critical P1 tickets)."
    except Exception as e:
        return f"Support System: SQLite online (summary unavailable: {e})."
