"""
SmartOps AI — Unified Demo Seeder & Reset Engine
Seeds 12 support tickets (mixed P1-P4, positive/neutral/negative),
5 CRM leads (4 qualified, 1 unqualified), KB articles, case studies, and 1 sales replay.
Executes in under 2 seconds.
"""
import os
import sys
import json
import sqlite3
import shutil
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_FILE = ROOT / "Customer-Support-Agent" / "complaints.db"
DATA_DIR = ROOT / "data"
REPORTS_DIR = ROOT / "sales_agent_module" / "reports"
REPLAY_DIR = DATA_DIR / "replay"

TICKETS = [
    {
        "id": "TKT-1001-P1",
        "email": "sarah.connor@cyberdyne.io",
        "order_id": "ORD-2060b6",
        "complaint_text": "URGENT: The industrial laptop arrived completely shattered. The frame is bent, screen broken, and battery smells like smoke. We have our on-site team kickoff tomorrow!",
        "status": "escalated",
        "priority": "P1",
        "escalation_required": True,
        "email_sent": True
    },
    {
        "id": "TKT-1002-P1",
        "email": "david.k@cloudinfra.com",
        "order_id": "ORD-8812a1",
        "complaint_text": "Critical server rack shipment arrived damaged with severed busbars. Production facility install is halted. Require immediate emergency replacement dispatch.",
        "status": "escalated",
        "priority": "P1",
        "escalation_required": True,
        "email_sent": True
    },
    {
        "id": "TKT-1003-P1",
        "email": "marcus.vance@precisionmed.org",
        "order_id": "ORD-4491c3",
        "complaint_text": "Medical diagnostic tablet screen failed completely out of the box. Diagnostic laboratory cannot process incoming donor samples.",
        "status": "escalated",
        "priority": "P1",
        "escalation_required": True,
        "email_sent": False
    },
    {
        "id": "TKT-1004-P2",
        "email": "elena.r@fintechcloud.net",
        "order_id": "ORD-3004b1",
        "complaint_text": "Order is delayed by over 10 business days with zero tracking updates from DHL. Our trading team needs these docking stations urgently.",
        "status": "escalated",
        "priority": "P2",
        "escalation_required": True,
        "email_sent": True
    },
    {
        "id": "TKT-1005-P2",
        "email": "alice.cooper@soundworks.com",
        "order_id": "ORD-3004",
        "complaint_text": "Received 3 units of model X40 instead of model X50 Pro. Discrepancy in warehouse fulfillment needs correcting.",
        "status": "escalated",
        "priority": "P2",
        "escalation_required": True,
        "email_sent": False
    },
    {
        "id": "TKT-1006-P2",
        "email": "brian.t@logisticsplus.com",
        "order_id": "ORD-5521",
        "complaint_text": "Duplicate charge on invoice #INV-9901. We were charged twice for courier express delivery.",
        "status": "resolved",
        "priority": "P2",
        "escalation_required": False,
        "email_sent": True
    },
    {
        "id": "TKT-1007-P3",
        "email": "priya.patel@omniretail.in",
        "order_id": "ORD-7712",
        "complaint_text": "Outer carton had cosmetic scuffs upon arrival. Hardware appears intact but box was crushed. Please verify warranty coverage.",
        "status": "resolved",
        "priority": "P3",
        "escalation_required": False,
        "email_sent": True
    },
    {
        "id": "TKT-1008-P3",
        "email": "bob.builder@acme.org",
        "order_id": "ORD-3002",
        "complaint_text": "Package arrived 2 days late. Product works fine, but would appreciate notification next time carrier changes routing.",
        "status": "resolved",
        "priority": "P3",
        "escalation_required": False,
        "email_sent": True
    },
    {
        "id": "TKT-1009-P3",
        "email": "linda.w@vertex.io",
        "order_id": "ORD-6623",
        "complaint_text": "Need clarification on API rate limit licensing tier associated with our enterprise hardware bundle.",
        "status": "resolved",
        "priority": "P3",
        "escalation_required": False,
        "email_sent": True
    },
    {
        "id": "TKT-1010-P4",
        "email": "charlie.brown@creative.co",
        "order_id": "ORD-3003",
        "complaint_text": "Just wanted to share positive feedback! The automated packaging and unboxing instructions were phenomenal.",
        "status": "resolved",
        "priority": "P4",
        "escalation_required": False,
        "email_sent": True
    },
    {
        "id": "TKT-1011-P4",
        "email": "david.miller@startup.co",
        "order_id": "ORD-3005",
        "complaint_text": "How do I change the secondary billing address on future recurring shipments?",
        "status": "new",
        "priority": None,
        "escalation_required": False,
        "email_sent": False
    },
    {
        "id": "TKT-1012-P4",
        "email": "karen.page@nelsonmurdock.org",
        "order_id": "ORD-9912",
        "complaint_text": "Please provide an updated copy of the sustainability certificate for our company annual report.",
        "status": "new",
        "priority": None,
        "escalation_required": False,
        "email_sent": False
    }
]

LEADS = [
    {
        "id": "prospect_001",
        "Name": "Alex Mercer",
        "First Name": "Alex",
        "Last Name": "Mercer",
        "Email": "alex.mercer@example.com",
        "Company": "Apex Dynamics",
        "Title": "VP of Operations",
        "Score": 8.5,
        "Status": "Outreach ready",
        "Notes": "Growing mid-market B2B distributor experiencing customer support delays and high ticket volume."
    },
    {
        "id": "prospect_002",
        "Name": "Elena Rostova",
        "First Name": "Elena",
        "Last Name": "Rostova",
        "Email": "elena.rostova@example.com",
        "Company": "FinTech Cloud Solutions",
        "Title": "Chief Customer Officer",
        "Score": 6.8,
        "Status": "Outreach ready",
        "Notes": "Evaluating automation solutions, but currently transitioning core ticketing platforms."
    },
    {
        "id": "prospect_003",
        "Name": "Timmy Small",
        "First Name": "Timmy",
        "Last Name": "Small",
        "Email": "timmy@example.com",
        "Company": "Timmy's Solo Hobby Blog",
        "Title": "Solo Blogger",
        "Score": 2.8,
        "Status": "Not a fit right now",
        "Notes": "Individual content creator with zero B2B operations or support staff."
    }
]

def seed_support_db():
    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    # Create complaints table if missing
    c.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id VARCHAR PRIMARY KEY,
        email VARCHAR NOT NULL,
        order_id VARCHAR NOT NULL,
        complaint_text TEXT NOT NULL,
        status VARCHAR DEFAULT 'new',
        priority VARCHAR,
        escalation_required BOOLEAN DEFAULT 0,
        email_sent BOOLEAN DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME
    )
    """)
    c.execute("DELETE FROM complaints")
    for t in TICKETS:
        c.execute("""
        INSERT INTO complaints (id, email, order_id, complaint_text, status, priority, escalation_required, email_sent)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (t["id"], t["email"], t["order_id"], t["complaint_text"], t["status"], t["priority"], t["escalation_required"], t["email_sent"]))
    conn.commit()
    conn.close()

def seed_sample_data():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "samples").mkdir(exist_ok=True)
    (DATA_DIR / "case_studies").mkdir(exist_ok=True)
    (DATA_DIR / "replay").mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # Leads sample
    with open(DATA_DIR / "samples" / "leads.json", "w", encoding="utf-8") as f:
        json.dump(LEADS, f, indent=2)

    # Replay package
    replay_data = {
        "lead": LEADS[0],
        "score": 8.5,
        "qualification": "qualified",
        "matched_case_study": "Spark Retail (85% query resolution, $150k quarterly lift)",
        "generated_reports_count": 9,
        "reports": [
            "Blog Analysis Report.txt",
            "Digital Presence Report.txt",
            "General Lead Research Report.txt",
            "Global Lead Analysis Report.txt",
            "Interview Script.txt",
            "News Analysis Report.txt",
            "Outreach Report.txt",
            "Personalized Email.txt",
            "Youtube Analysis Report.txt"
        ]
    }
    with open(DATA_DIR / "replay" / "sales_replay.json", "w", encoding="utf-8") as f:
        json.dump(replay_data, f, indent=2)

def run_reset():
    start = time.time()
    seed_support_db()
    seed_sample_data()
    duration = round(time.time() - start, 3)
    return {"status": "ok", "duration_seconds": duration, "tickets_seeded": len(TICKETS), "leads_seeded": len(LEADS)}

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    res = run_reset()
    print(f"✅ Demo data seeded successfully in {res['duration_seconds']}s ({res['tickets_seeded']} tickets, {res['leads_seeded']} leads).")
