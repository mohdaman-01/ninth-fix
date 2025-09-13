"""
File upload and bulk data upload endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.uploader_service import UploaderService
from app.core.security import get_current_active_user, require_institution_or_admin
from app.models.user import User
from app.schemas.certificate import BulkUploadResponse, VerifiedRecordCreate
from typing import List
import json

router = APIRouter()

@router.post("/certificate")
async def upload_certificate(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload a single certificate file"""
    
    try:
        uploader_service = UploaderService(db)
        result = await uploader_service.upload_certificate_file(file, str(current_user.id))
        
        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['error']
            )
        
        return {
            "message": "Certificate uploaded successfully",
            "certificate_id": result['certificate_id'],
            "file_path": result['file_path']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload error: {str(e)}"
        )

@router.post("/verified-records/bulk", response_model=BulkUploadResponse)
async def bulk_upload_verified_records(
    records: List[VerifiedRecordCreate],
    current_user: User = Depends(require_institution_or_admin),
    db: Session = Depends(get_db)
):
    """Bulk upload verified records (institutions only)"""
    
    if len(records) > 1000:  # Limit bulk uploads
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Too many records. Maximum 1000 per request."
        )
    
    try:
        uploader_service = UploaderService(db)
        result = uploader_service.bulk_upload_verified_records(records, str(current_user.id))
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk upload error: {str(e)}"
        )

@router.post("/verified-records/csv", response_model=BulkUploadResponse)
async def upload_csv_records(
    file: UploadFile = File(...),
    current_user: User = Depends(require_institution_or_admin),
    db: Session = Depends(get_db)
):
    """Upload verified records from CSV file"""
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file"
        )
    
    try:
        uploader_service = UploaderService(db)
        result = uploader_service.upload_csv_records(file, str(current_user.id))
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CSV upload error: {str(e)}"
        )

@router.post("/verified-records/json", response_model=BulkUploadResponse)
async def upload_json_records(
    file: UploadFile = File(...),
    current_user: User = Depends(require_institution_or_admin),
    db: Session = Depends(get_db)
):
    """Upload verified records from JSON file"""
    
    if not file.filename.endswith('.json'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a JSON file"
        )
    
    try:
        uploader_service = UploaderService(db)
        result = uploader_service.upload_json_records(file, str(current_user.id))
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"JSON upload error: {str(e)}"
        )

@router.get("/my-certificates")
async def get_my_certificates(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get certificates uploaded by current user"""
    
    try:
        uploader_service = UploaderService(db)
        certificates = uploader_service.get_uploader_certificates(str(current_user.id), skip, limit)
        
        return {
            "certificates": [
                {
                    "id": str(cert.id),
                    "filename": cert.filename,
                    "status": cert.status,
                    "submitted_at": cert.submitted_at,
                    "processed_at": cert.processed_at
                }
                for cert in certificates
            ],
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting certificates: {str(e)}"
        )

@router.get("/my-stats")
async def get_my_upload_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get upload statistics for current user"""
    
    try:
        uploader_service = UploaderService(db)
        stats = uploader_service.get_uploader_stats(str(current_user.id))
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting stats: {str(e)}"
        )

@router.delete("/certificate/{certificate_id}")
async def delete_certificate(
    certificate_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a certificate (only by uploader)"""
    
    try:
        uploader_service = UploaderService(db)
        success = uploader_service.delete_certificate(certificate_id, str(current_user.id))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Certificate not found or access denied"
            )
        
        return {"message": "Certificate deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting certificate: {str(e)}"
        )

@router.get("/templates/csv")
async def download_csv_template():
    """Download CSV template for bulk upload"""
    
    template_data = {
        "student_name": "John Doe",
        "roll_number": "2023001",
        "marks": "85%",
        "cert_number": "CERT-2023-001",
        "issuer": "University of Example",
        "issued_at": "2023-06-15T00:00:00"
    }
    
    # Return template as JSON (frontend can convert to CSV)
    return {
        "template": template_data,
        "instructions": [
            "Download this template and fill in your data",
            "Ensure dates are in ISO format (YYYY-MM-DDTHH:MM:SS)",
            "All fields except 'marks' are required",
            "Upload the completed CSV file using the /upload/verified-records/csv endpoint"
        ]
    }

@router.get("/templates/json")
async def download_json_template():
    """Download JSON template for bulk upload"""
    
    template_data = [
        {
            "student_name": "John Doe",
            "roll_number": "2023001",
            "marks": "85%",
            "cert_number": "CERT-2023-001",
            "issuer": "University of Example",
            "issued_at": "2023-06-15T00:00:00"
        },
        {
            "student_name": "Jane Smith",
            "roll_number": "2023002",
            "marks": "92%",
            "cert_number": "CERT-2023-002",
            "issuer": "University of Example",
            "issued_at": "2023-06-15T00:00:00"
        }
    ]
    
    return {
        "template": template_data,
        "instructions": [
            "Use this template format for JSON uploads",
            "Ensure dates are in ISO format (YYYY-MM-DDTHH:MM:SS)",
            "All fields except 'marks' are required",
            "Upload the completed JSON file using the /upload/verified-records/json endpoint"
        ]
    }
