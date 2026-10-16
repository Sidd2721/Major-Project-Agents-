from Backend.db import SessionLocal
from Backend.crud import (get_new_complaints, mark_complaint_as_spam,update_complaint_result,update_complaint_status,mark_email_sent)

from Agent.graph import build_graph
from FinalisingAgent.resolution import decide_resolution
from Email.email_service import send_email

app = build_graph()


def process_complaints():
    db = SessionLocal()
    complaints = get_new_complaints(db)

    if not complaints:
        db.close()
        return

    print(f"Found {len(complaints)} new complaints")

    for c in complaints:
        print(f"\nProcessing complaint {c.id}")

        # Run agent
        try:
            import os, sys
            from pathlib import Path
            mode = os.getenv("LLM_MODE", "mock").lower()
            groq_key = os.getenv("GROQ_API_KEY", "").strip()
            if mode == "mock" or not groq_key or "placeholder" in groq_key:
                root_path = Path(__file__).resolve().parent.parent.parent
                if str(root_path) not in sys.path:
                    sys.path.insert(0, str(root_path))
                from shared.llm_helper import mock_support_triage
                result = mock_support_triage(c.complaint_text)
            else:
                result = app.invoke({"complaint_text": c.complaint_text})

            if result.get("is_valid") is False:
                print(f"🛑 Spam detected: {result.get('validation_reason')}")
                mark_complaint_as_spam(db, c.id, result.get("validation_reason"))
                continue

        except Exception as e:
            print(f"⚠️ Agent live call failed, falling back to mock: {e}")
            import sys
            from pathlib import Path
            root_path = Path(__file__).resolve().parent.parent.parent
            if str(root_path) not in sys.path:
                sys.path.insert(0, str(root_path))
            from shared.llm_helper import mock_support_triage
            result = mock_support_triage(c.complaint_text)
        
        priority = result.get("reevaluated_priority")
        escalated = result.get("escalation_required")
        email_body = result.get("response_email")

        # Phase 5 decision
        decision = decide_resolution(
            complaint=c.complaint_text,
            priority=priority,
            escalated=escalated
        )

        # Phase 6: Send email
        subject = "Regarding your recent support request"

        send_email(
            to_email=c.email,
            subject=subject,
            body=email_body
        )

        mark_email_sent(db, c.id)

        # Update status
        if decision.auto_resolve:
            update_complaint_status(db, c.id, "resolved")
            print("✅ Auto-resolved & email sent")
        else:
            update_complaint_status(db, c.id, "escalated")
            print("🚨 Escalated & acknowledgement email sent")

        update_complaint_result(
            db,
            complaint_id=c.id,
            priority=priority,
            escalated=not decision.auto_resolve
        )

    db.close()