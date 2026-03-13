from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import get_db
from risk_scoring import get_current_business_health
from ai_service import generate_ai_response
from sqlalchemy.orm import Session
from models import SystemMetric, SOCAlert, ERPReport
import datetime

app = FastAPI(title="Conversational CIO API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    role: str = "CIO" # Basic RBAC mock, could be 'CIO', 'CTO', 'Operations'

class IngestMetricRequest(BaseModel):
    component: str
    metric_name: str
    metric_value: float

@app.get("/")
def root():
    return {"message": "Conversational CIO Backend is running."}

@app.get("/api/dashboard")
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """
    Returns the high-level business health needed for the executive dashboard.
    """
    try:
        health = get_current_business_health(db)
        return health
    except Exception as e:
        # Fallback if DB is not setup yet (e.g. MySQL issues on user's machine)
        import random
        return {
            "risk_score": random.randint(30, 85),
            "risk_level": "Medium",
            "anomalies_detected": [f"Database error ({e}), showing mocked health status."],
            "mocked_response": True
        }

@app.post("/api/chat")
def chat_with_cio(request: QueryRequest):
    """
    The main RAG conversational endpoint.
    """
    # Simple RBAC: If role is low-level, we could filter context, but for MVP we just log it.
    if request.role not in ["CIO", "CTO", "Executive"]:
        raise HTTPException(status_code=403, detail="Unauthorized role for Strategic AI insights.")
    
    # Generate Response
    try:
        ai_reply = generate_ai_response(request.query)
        return {"response": ai_reply, "role_context": request.role}
    except Exception as e:
        return {"response": f"AI Engine encountered an error: {e}", "role_context": request.role}

@app.post("/api/ingest")
def data_ingestion_webhook(data: IngestMetricRequest, db: Session = Depends(get_db)):
    """
    Receives incoming telemetry/metrics from external sources (e.g., AWS, SAP).
    In a real system, this triggers ETL to Vector DB.
    """
    try:
        new_metric = SystemMetric(
            component=data.component, 
            metric_name=data.metric_name, 
            metric_value=data.metric_value,
            timestamp=datetime.datetime.utcnow()
        )
        db.add(new_metric)
        db.commit()
        # Optionally here you would also call ETL script or LangChain upsert to re-vectorize
        return {"status": "success", "message": "Metric ingested."}
    except Exception as e:
        # DB Error fallback
        return {"status": "error", "message": str(e)}
