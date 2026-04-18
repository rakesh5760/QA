from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database.db import engine, Base, get_db
from backend.models.db_models import TestResult
from backend.services.playwright_service import analyze_website
import json

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI-Based Intelligent QA Automation API")

@app.get("/")
def read_root():
    return {"message": "API is running"}

@app.get("/db-test")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        # Create a sample record
        sample_result = TestResult(
            url="https://example.com",
            result_json=json.dumps({"status": "test", "score": 100})
        )
        db.add(sample_result)
        db.commit()
        db.refresh(sample_result)
        
        return {
            "status": "success",
            "message": "Database connection and insert successful",
            "inserted_id": sample_result.id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Pydantic model for input
class AnalysisRequest(BaseModel):
    url: str

@app.post("/analyze-basic")
async def analyze_basic(request: AnalysisRequest, db: Session = Depends(get_db)):
    try:
        # 1. Perform analysis
        results = await analyze_website(request.url)
        
        # 2. Save result to database
        new_result = TestResult(
            url=request.url,
            result_json=json.dumps(results)
        )
        db.add(new_result)
        db.commit()
        db.refresh(new_result)
        
        # 3. Add DB ID to response
        results["id"] = new_result.id
        results["created_at"] = new_result.created_at.isoformat()
        
        return results
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e) or "Internal Server Error - Check console for logs")

@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    """
    Fetches all past analysis results.
    """
    try:
        records = db.query(TestResult).order_by(TestResult.created_at.desc()).all()
        history = []
        for record in records:
            history.append({
                "id": record.id,
                "url": record.url,
                "created_at": record.created_at.isoformat(),
                "result": json.loads(record.result_json) if record.result_json else {}
            })
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")

@app.get("/history/{record_id}")
def get_history_detail(record_id: int, db: Session = Depends(get_db)):
    """
    Fetches a specific past analysis result by ID.
    """
    record = db.query(TestResult).filter(TestResult.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    return {
        "id": record.id,
        "url": record.url,
        "created_at": record.created_at.isoformat(),
        "result": json.loads(record.result_json) if record.result_json else {}
    }
