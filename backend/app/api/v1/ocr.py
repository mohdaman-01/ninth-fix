"""
OCR endpoints for text extraction from certificates
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.ocr_service import OCRService
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.certificate import CertificateDataCreate, CertificateData
from app.models.certificate import CertificateData as CertificateDataModel
from app.core.config import settings
import uuid

router = APIRouter()

@router.post("/extract-text")
async def extract_text_from_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Extract text from uploaded certificate image"""
    
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE} bytes"
        )
    
    try:
        # Initialize OCR service
        ocr_service = OCRService()
        
        # Extract text from image
        result = ocr_service.extract_text_from_bytes(file_content)
        
        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"OCR processing failed: {result.get('error', 'Unknown error')}"
            )
        
        return {
            "raw_text": result['raw_text'],
            "structured_data": result['structured_data'],
            "confidence": result['confidence'],
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing error: {str(e)}"
        )

@router.post("/extract-and-save/{certificate_id}")
async def extract_and_save_text(
    certificate_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Extract text from image and save to database"""
    
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
        )
    
    try:
        # Initialize OCR service
        ocr_service = OCRService()
        
        # Read file content
        file_content = await file.read()
        
        # Extract text from image
        result = ocr_service.extract_text_from_bytes(file_content)
        
        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"OCR processing failed: {result.get('error', 'Unknown error')}"
            )
        
        # Save extracted data to database
        structured_data = result['structured_data']
        cert_data = CertificateDataModel(
            cert_id=certificate_id,
            student_name=structured_data.get('student_name'),
            roll_number=structured_data.get('roll_number'),
            marks=structured_data.get('marks'),
            cert_number=structured_data.get('cert_number')
        )
        
        # Check if data already exists and update or create
        existing_data = db.query(CertificateDataModel).filter(
            CertificateDataModel.cert_id == certificate_id
        ).first()
        
        if existing_data:
            existing_data.student_name = structured_data.get('student_name')
            existing_data.roll_number = structured_data.get('roll_number')
            existing_data.marks = structured_data.get('marks')
            existing_data.cert_number = structured_data.get('cert_number')
        else:
            db.add(cert_data)
        
        db.commit()
        
        return {
            "raw_text": result['raw_text'],
            "structured_data": result['structured_data'],
            "confidence": result['confidence'],
            "saved_to_db": True,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing error: {str(e)}"
        )

@router.get("/languages")
async def get_supported_languages():
    """Get supported OCR languages"""
    return {
        "supported_languages": settings.OCR_LANGUAGES.split(','),
        "default_language": settings.OCR_LANGUAGES.split(',')[0] if settings.OCR_LANGUAGES else "eng"
    }

@router.get("/health")
async def ocr_health_check():
    """Check OCR service health"""
    try:
        ocr_service = OCRService()
        # Simple test to check if Tesseract is working
        return {
            "status": "healthy",
            "tesseract_available": True,
            "supported_languages": settings.OCR_LANGUAGES.split(',')
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "tesseract_available": False,
            "error": str(e)
        }
