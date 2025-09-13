"""
Certificate verification endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.verification_service import VerificationService
from app.core.security import get_current_active_user, require_institution_or_admin
from app.models.user import User
from app.schemas.certificate import VerificationRequest, VerificationResponse
from typing import List

router = APIRouter()

@router.post("/certificate/{certificate_id}", response_model=VerificationResponse)
async def verify_certificate(
    certificate_id: str,
    verification_request: VerificationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Verify a certificate against verified records"""
    
    try:
        verification_service = VerificationService(db)
        result = verification_service.verify_certificate(certificate_id, verification_request)
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification error: {str(e)}"
        )

@router.post("/bulk", response_model=dict)
async def bulk_verify_certificates(
    certificate_ids: List[str],
    current_user: User = Depends(require_institution_or_admin),
    db: Session = Depends(get_db)
):
    """Bulk verify multiple certificates"""
    
    if len(certificate_ids) > 100:  # Limit bulk operations
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Too many certificates. Maximum 100 per request."
        )
    
    try:
        verification_service = VerificationService(db)
        results = verification_service.bulk_verify_certificates(certificate_ids)
        
        # Calculate summary statistics
        total = len(results)
        verified = sum(1 for r in results.values() if r.is_verified)
        failed = total - verified
        
        return {
            "total_certificates": total,
            "verified": verified,
            "failed": failed,
            "verification_rate": verified / total if total > 0 else 0,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk verification error: {str(e)}"
        )

@router.get("/certificate/{certificate_id}/status")
async def get_verification_status(
    certificate_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get verification status of a certificate"""
    
    try:
        verification_service = VerificationService(db)
        
        # Get basic verification info
        from app.models.certificate import Certificate, CertificateData, Alert, AIPrediction
        
        certificate = db.query(Certificate).filter(Certificate.id == certificate_id).first()
        if not certificate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Certificate not found"
            )
        
        cert_data = db.query(CertificateData).filter(CertificateData.cert_id == certificate_id).first()
        alerts = db.query(Alert).filter(Alert.cert_id == certificate_id).all()
        ai_prediction = db.query(AIPrediction).filter(AIPrediction.cert_id == certificate_id).first()
        
        return {
            "certificate_id": certificate_id,
            "status": certificate.status,
            "submitted_at": certificate.submitted_at,
            "processed_at": certificate.processed_at,
            "has_extracted_data": cert_data is not None,
            "alert_count": len(alerts),
            "has_ai_prediction": ai_prediction is not None,
            "ai_confidence": ai_prediction.confidence_score if ai_prediction else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting verification status: {str(e)}"
        )

@router.get("/search")
async def search_verified_records(
    student_name: str = None,
    roll_number: str = None,
    cert_number: str = None,
    issuer: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Search verified records"""
    
    try:
        from app.models.certificate import VerifiedRecord
        from sqlalchemy import and_, or_
        
        query = db.query(VerifiedRecord)
        conditions = []
        
        if student_name:
            conditions.append(VerifiedRecord.student_name.ilike(f"%{student_name}%"))
        if roll_number:
            conditions.append(VerifiedRecord.roll_number.ilike(f"%{roll_number}%"))
        if cert_number:
            conditions.append(VerifiedRecord.cert_number.ilike(f"%{cert_number}%"))
        if issuer:
            conditions.append(VerifiedRecord.issuer.ilike(f"%{issuer}%"))
        
        if conditions:
            query = query.filter(and_(*conditions))
        
        records = query.limit(50).all()
        
        return {
            "count": len(records),
            "records": [
                {
                    "id": str(record.id),
                    "student_name": record.student_name,
                    "roll_number": record.roll_number,
                    "cert_number": record.cert_number,
                    "issuer": record.issuer,
                    "issued_at": record.issued_at
                }
                for record in records
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search error: {str(e)}"
        )
