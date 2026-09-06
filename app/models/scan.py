"""
Pydantic request/response schemas for the scan/analysis endpoint.
Equivalent to DTOs in ABS_Server.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class PayloadType(str, Enum):
    URL = "URL"
    UPI = "UPI"
    TEXT = "TEXT"
    WIFI = "WIFI"
    UNKNOWN = "UNKNOWN"


class RiskLevel(str, Enum):
    SAFE = "Safe"
    SUSPICIOUS = "Suspicious"
    DANGEROUS = "Dangerous"


class AnalyzeRequest(BaseModel):
    raw_content: str = Field(..., description="Raw decoded string from the scanned QR code")
    user_id: Optional[str] = Field(None, description="Firebase UID of the scanning user, if authenticated")


class RiskFactor(BaseModel):
    code: str          # e.g. "SUSPICIOUS_DOMAIN"
    label: str         # e.g. "Suspicious Domain"
    triggered: bool
    detail: str = ""   # human-readable explanation, differs based on triggered state

class AnalyzeResponse(BaseModel):
    payload_type: PayloadType
    raw_content: str
    risk_level: RiskLevel
    confidence: int  # 0-100
    score: int
    reasons: list[RiskFactor]
    domain: Optional[str] = None
    domain_age_days: Optional[int] = None
    is_https: Optional[bool] = None
    scanned_at: datetime = Field(default_factory=datetime.utcnow)

class AssistantRequest(BaseModel):
    message: str
    scan_context: Optional[str] = None


class AssistantResponse(BaseModel):
    reply: str    