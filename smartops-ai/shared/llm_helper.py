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
    if (groq_key and not groq_key.startswith("gsk_REPLACE")) or (gemini_key and not gemini_key.startswith("AIza_REPLACE")):
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
    """Generates realistic structured sales research and outreach."""
    score = 8.5 if is_qualified else 3.2
    qualification = "qualified" if is_qualified else "unqualified"
    case_study = "Spark Retail (85% query resolution, 210% engagement lift, $150k quarterly lift)"
    
    email = (
        f"Subject: Scaling {company}'s operations with autonomous multi-agent pipelines\n\n"
        f"Hi {lead_name},\n\n"
        f"I came across {company}'s recent expansion and noticed opportunities to accelerate your customer triage and B2B workflow.\n\n"
        f"Using our multi-agent architecture (similar to how Spark Retail automated 85% of complex customer queries while lifting revenue by $150k/quarter), "
        f"SmartOps AI integrates triage, research, and outreach seamlessly.\n\n"
        f"Would you be open to a brief 10-minute walkthrough this Thursday?\n\n"
        f"Best,\nSmartOps Sales Intelligence Team"
    )
    
    return {
        "lead_name": lead_name,
        "company": company,
        "qualification_status": qualification,
        "lead_score": score,
        "matched_case_study": case_study,
        "outreach_email": email,
        "steps": [
            {"step": 1, "name": "Lead Profiling", "detail": f"Synthesized public business signals for {company}"},
            {"step": 2, "name": "B2B Qualification", "detail": f"Score {score}/10 -> {qualification.upper()}"},
            {"step": 3, "name": "RAG Case Study Retrieval", "detail": f"ChromaDB matched '{case_study}'"},
            {"step": 4, "name": "SPIN Email Synthesis", "detail": "Generated personalized outreach draft"}
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
