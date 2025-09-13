"""
Certificate schemas for request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum

class CertificateStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    FORGED = "forged"

class AlertLevel(str, Enum):
    WARNING = "warning"
    CRITICAL = "critical"

# Certificate schemas
class CertificateBase(BaseModel):
    filename: str
    file_url: str

class CertificateCreate(CertificateBase):
    pass

class CertificateUpdate(BaseModel):
    status: Optional[CertificateStatus] = None
    extracted_text: Optional[str] = None

class CertificateInDB(CertificateBase):
    id: UUID
    uploader_id: UUID
    extracted_text: Optional[str] = None
    status: CertificateStatus
    submitted_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Certificate(CertificateInDB):
    pass

# Certificate data schemas
class CertificateDataBase(BaseModel):
    student_name: Optional[str] = None
    roll_number: Optional[str] = None
    marks: Optional[str] = None
    cert_number: Optional[str] = None

class CertificateDataCreate(CertificateDataBase):
    cert_id: UUID

class CertificateDataUpdate(CertificateDataBase):
    pass

class CertificateDataInDB(CertificateDataBase):
    id: UUID
    cert_id: UUID
    extracted_at: datetime

    class Config:
        from_attributes = True

class CertificateData(CertificateDataInDB):
    pass

# Verified record schemas
class VerifiedRecordBase(BaseModel):
    student_name: str
    roll_number: str
    marks: Optional[str] = None
    cert_number: str
    issuer: str
    issued_at: datetime

class VerifiedRecordCreate(VerifiedRecordBase):
    pass

class VerifiedRecordUpdate(BaseModel):
    student_name: Optional[str] = None
    roll_number: Optional[str] = None
    marks: Optional[str] = None
    cert_number: Optional[str] = None
    issuer: Optional[str] = None
    issued_at: Optional[datetime] = None

class VerifiedRecordInDB(VerifiedRecordBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class VerifiedRecord(VerifiedRecordInDB):
    pass

# Alert schemas
class AlertBase(BaseModel):
    reason: str
    level: AlertLevel

class AlertCreate(AlertBase):
    cert_id: UUID

class AlertUpdate(BaseModel):
    resolved: Optional[bool] = None

class AlertInDB(AlertBase):
    id: UUID
    cert_id: UUID
    flagged_at: datetime
    resolved: bool
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Alert(AlertInDB):
    pass

# AI Prediction schemas
class AIPredictionBase(BaseModel):
    probability: float = Field(..., ge=0.0, le=1.0)
    model_version: str
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    model_metadata: Optional[str] = None

class AIPredictionCreate(AIPredictionBase):
    cert_id: UUID

class AIPredictionInDB(AIPredictionBase):
    id: UUID
    cert_id: UUID
    predicted_at: datetime

    class Config:
        from_attributes = True

class AIPrediction(AIPredictionInDB):
    pass

# Verification schemas
class VerificationRequest(BaseModel):
    student_name: Optional[str] = None
    roll_number: Optional[str] = None
    cert_number: Optional[str] = None
    issuer: Optional[str] = None

class VerificationResponse(BaseModel):
    is_verified: bool
    confidence_score: float
    matched_record: Optional[VerifiedRecord] = None
    mismatches: List[str] = []
    alerts: List[Alert] = []
    ai_prediction: Optional[AIPrediction] = None

# Upload schemas
class BulkUploadRequest(BaseModel):
    records: List[VerifiedRecordCreate]

class BulkUploadResponse(BaseModel):
    success_count: int
    error_count: int
    errors: List[str] = []

# Dashboard schemas
class DashboardStats(BaseModel):
    total_certificates: int
    verified_certificates: int
    forged_certificates: int
    pending_certificates: int
    total_alerts: int
    critical_alerts: int
    verification_rate: float
    forgery_rate: float

class VerificationTrend(BaseModel):
    date: datetime
    verified_count: int
    forged_count: int
    pending_count: int

class InstitutionStats(BaseModel):
    institution_name: str
    total_uploads: int
    verification_rate: float
    forgery_rate: float
