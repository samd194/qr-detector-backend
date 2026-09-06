"""
API route for analyzing scanned QR content.
Kept thin — no business logic here, just request handling + persistence.
"""
from fastapi import APIRouter, HTTPException

from app.models.scan import AnalyzeRequest, AnalyzeResponse
from app.services.risk_engine import analyze_content
from app.firebase import db

router = APIRouter(prefix="/scan", tags=["Scan"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    if not request.raw_content or not request.raw_content.strip():
        raise HTTPException(status_code=400, detail="raw_content cannot be empty")

    result = await analyze_content(request.raw_content)

    # Persist the scan to Firestore (skip if no user_id — anonymous scan)
    if request.user_id:
        db.collection("scans").add({
            "user_id": request.user_id,
            "raw_content": result.raw_content,
            "payload_type": result.payload_type.value,
            "risk_level": result.risk_level.value,
            "confidence": result.confidence,
            "score": result.score,
            "domain": result.domain,
            "reasons": [r.model_dump() for r in result.reasons],
            "scanned_at": result.scanned_at,
        })

    return result