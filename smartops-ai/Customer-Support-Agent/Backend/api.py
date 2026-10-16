from fastapi import FastAPI,HTTPException,Query
from pydantic import BaseModel, EmailStr
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from .db import SessionLocal, engine
from .models import Base
from .crud import create_complaint,get_all_complaints,get_complaint_by_id,get_complaints_by_email,update_complaint,delete_complaint,get_metrics_summary,get_status_breakdown,get_priority_breakdown,get_daily_trend
from .schemas import ComplaintResponse,ComplaintUpdate,MetricsSummary,StatusBreakdown,PriorityBreakdown,DailyTrend
from typing import List, Optional

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Complaint Ingestion API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ComplaintInput(BaseModel):
    email: EmailStr
    order_id: str
    complaint_text: str


@app.post("/complaints")
def submit_complaint(data: ComplaintInput):
    db = SessionLocal()
    complaint = create_complaint(
        db,
        data.email,
        data.order_id,
        data.complaint_text
    )
    db.close()

    return {
        "message": "Complaint submitted successfully",
        "complaint_id": complaint.id
    }

@app.get("/complaints", response_model=List[ComplaintResponse])
def list_complaints(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None)
):
    db = SessionLocal()
    complaints = get_all_complaints(db, status, priority)
    db.close()
    return complaints


@app.get("/complaints/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(complaint_id: str):
    db = SessionLocal()
    complaint = get_complaint_by_id(db, complaint_id)
    db.close()

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    return complaint


@app.patch("/complaints/{complaint_id}", response_model=ComplaintResponse)
def update_complaint_api(
    complaint_id: str,
    data: ComplaintUpdate
):
    db = SessionLocal()
    complaint = update_complaint(
        db,
        complaint_id,
        data.status,
        data.priority
    )
    db.close()

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    return complaint


@app.delete("/complaints/{complaint_id}")
def delete_complaint_api(complaint_id: str):
    db = SessionLocal()
    success = delete_complaint(db, complaint_id)
    db.close()

    if not success:
        raise HTTPException(status_code=404, detail="Complaint not found")

    return {"message": "Complaint deleted successfully"}


@app.get(
    "/complaints/by-email/{email}",
    response_model=List[ComplaintResponse]
)
def get_complaints_for_customer(email: str):
    db = SessionLocal()
    complaints = get_complaints_by_email(db, email)
    db.close()
    return complaints

@app.get("/analytics/summary", response_model=MetricsSummary)
def analytics_summary():
    db = SessionLocal()
    data = get_metrics_summary(db)
    db.close()
    return data


@app.get("/analytics/status", response_model=StatusBreakdown)
def analytics_by_status():
    db = SessionLocal()
    data = get_status_breakdown(db)
    db.close()
    return {"by_status": data}


@app.get("/analytics/priority", response_model=PriorityBreakdown)
def analytics_by_priority():
    db = SessionLocal()
    data = get_priority_breakdown(db)
    db.close()
    return {"by_priority": data}


@app.get("/analytics/trends", response_model=List[DailyTrend])
def analytics_trends():
    db = SessionLocal()
    data = get_daily_trend(db)
    db.close()
    return data


# ── Health, mode & admin demo reset endpoints ─────────────────────────
import os as _os
from fastapi import Header

@app.get("/health")
def health():
    return {"status": "ok", "service": "customer-support-agent"}

@app.get("/api/mode")
def api_mode():
    mode = _os.getenv("LLM_MODE", "mock").lower()
    return {"mode": mode, "service": "customer-support-agent", "degraded": (mode == "mock")}

@app.post("/demo/reset")
def demo_reset(
    authorization: Optional[str] = Header(None),
    x_admin_key: Optional[str] = Header(None),
    key: Optional[str] = Query(None)
):
    expected = _os.getenv("ADMIN_KEY", "smartops-admin-2026")
    provided = x_admin_key or key
    if not provided and authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() in ["bearer", "basic"]:
            provided = parts[1]
        else:
            provided = authorization
    if provided != expected:
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid admin key")
    
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    from scripts.seed_demo import run_reset
    result = run_reset()
    return result
