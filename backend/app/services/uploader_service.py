"""
Upload service for bulk certificate uploads and file management
"""

import os
import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.models.certificate import VerifiedRecord, Certificate, CertificateData
from app.models.user import User
from app.schemas.certificate import VerifiedRecordCreate, BulkUploadResponse
from app.core.config import settings
import csv
import json
from datetime import datetime
import aiofiles

class UploaderService:
    def __init__(self, db: Session):
        self.db = db

    async def upload_certificate_file(self, file: UploadFile, uploader_id: str) -> Dict[str, Any]:
        """Upload a single certificate file"""
        try:
            # Validate file
            if not self._validate_file(file):
                return {"success": False, "error": "Invalid file type or size"}

            # Generate unique filename
            file_extension = file.filename.split('.')[-1].lower()
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            
            # Save file
            file_path = await self._save_file(file, unique_filename)
            
            # Create certificate record
            certificate = Certificate(
                uploader_id=uploader_id,
                filename=file.filename,
                file_url=file_path,
                status="pending"
            )
            
            self.db.add(certificate)
            self.db.commit()
            self.db.refresh(certificate)
            
            return {
                "success": True,
                "certificate_id": str(certificate.id),
                "file_path": file_path
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def bulk_upload_verified_records(self, records: List[VerifiedRecordCreate], uploader_id: str) -> BulkUploadResponse:
        """Bulk upload verified records from institutions"""
        success_count = 0
        error_count = 0
        errors = []

        for record_data in records:
            try:
                # Check if record already exists
                existing = self.db.query(VerifiedRecord).filter(
                    VerifiedRecord.cert_number == record_data.cert_number
                ).first()
                
                if existing:
                    errors.append(f"Certificate {record_data.cert_number} already exists")
                    error_count += 1
                    continue

                # Create verified record
                verified_record = VerifiedRecord(
                    student_name=record_data.student_name,
                    roll_number=record_data.roll_number,
                    marks=record_data.marks,
                    cert_number=record_data.cert_number,
                    issuer=record_data.issuer,
                    issued_at=record_data.issued_at
                )
                
                self.db.add(verified_record)
                success_count += 1
                
            except Exception as e:
                errors.append(f"Error processing record {record_data.cert_number}: {str(e)}")
                error_count += 1

        try:
            self.db.commit()
        except Exception as e:
            errors.append(f"Database commit error: {str(e)}")
            error_count += success_count
            success_count = 0

        return BulkUploadResponse(
            success_count=success_count,
            error_count=error_count,
            errors=errors
        )

    def upload_csv_records(self, file: UploadFile, uploader_id: str) -> BulkUploadResponse:
        """Upload verified records from CSV file"""
        try:
            # Read CSV content
            content = file.file.read().decode('utf-8')
            csv_reader = csv.DictReader(content.splitlines())
            
            records = []
            for row in csv_reader:
                try:
                    record = VerifiedRecordCreate(
                        student_name=row.get('student_name', ''),
                        roll_number=row.get('roll_number', ''),
                        marks=row.get('marks', ''),
                        cert_number=row.get('cert_number', ''),
                        issuer=row.get('issuer', ''),
                        issued_at=datetime.fromisoformat(row.get('issued_at', ''))
                    )
                    records.append(record)
                except Exception as e:
                    continue  # Skip invalid rows
            
            return self.bulk_upload_verified_records(records, uploader_id)
            
        except Exception as e:
            return BulkUploadResponse(
                success_count=0,
                error_count=1,
                errors=[f"CSV processing error: {str(e)}"]
            )

    def upload_json_records(self, file: UploadFile, uploader_id: str) -> BulkUploadResponse:
        """Upload verified records from JSON file"""
        try:
            # Read JSON content
            content = file.file.read().decode('utf-8')
            data = json.loads(content)
            
            records = []
            for item in data:
                try:
                    record = VerifiedRecordCreate(
                        student_name=item.get('student_name', ''),
                        roll_number=item.get('roll_number', ''),
                        marks=item.get('marks', ''),
                        cert_number=item.get('cert_number', ''),
                        issuer=item.get('issuer', ''),
                        issued_at=datetime.fromisoformat(item.get('issued_at', ''))
                    )
                    records.append(record)
                except Exception as e:
                    continue  # Skip invalid items
            
            return self.bulk_upload_verified_records(records, uploader_id)
            
        except Exception as e:
            return BulkUploadResponse(
                success_count=0,
                error_count=1,
                errors=[f"JSON processing error: {str(e)}"]
            )

    def _validate_file(self, file: UploadFile) -> bool:
        """Validate uploaded file"""
        # Check file extension
        if not file.filename:
            return False
            
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in settings.ALLOWED_EXTENSIONS:
            return False
        
        # Check file size (this is a basic check, actual size validation should be done at the API level)
        return True

    async def _save_file(self, file: UploadFile, filename: str) -> str:
        """Save uploaded file to storage"""
        # Create upload directory if it doesn't exist
        os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
        
        file_path = os.path.join(settings.UPLOAD_FOLDER, filename)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return file_path

    def get_uploader_certificates(self, uploader_id: str, skip: int = 0, limit: int = 100) -> List[Certificate]:
        """Get certificates uploaded by a specific user"""
        return self.db.query(Certificate).filter(
            Certificate.uploader_id == uploader_id
        ).offset(skip).limit(limit).all()

    def get_uploader_stats(self, uploader_id: str) -> Dict[str, Any]:
        """Get upload statistics for a user"""
        total_certificates = self.db.query(Certificate).filter(
            Certificate.uploader_id == uploader_id
        ).count()
        
        verified_certificates = self.db.query(Certificate).filter(
            Certificate.uploader_id == uploader_id,
            Certificate.status == "verified"
        ).count()
        
        forged_certificates = self.db.query(Certificate).filter(
            Certificate.uploader_id == uploader_id,
            Certificate.status == "forged"
        ).count()
        
        pending_certificates = self.db.query(Certificate).filter(
            Certificate.uploader_id == uploader_id,
            Certificate.status == "pending"
        ).count()
        
        return {
            "total_certificates": total_certificates,
            "verified_certificates": verified_certificates,
            "forged_certificates": forged_certificates,
            "pending_certificates": pending_certificates,
            "verification_rate": verified_certificates / total_certificates if total_certificates > 0 else 0,
            "forgery_rate": forged_certificates / total_certificates if total_certificates > 0 else 0
        }

    def delete_certificate(self, cert_id: str, uploader_id: str) -> bool:
        """Delete a certificate (only by uploader or admin)"""
        certificate = self.db.query(Certificate).filter(
            Certificate.id == cert_id,
            Certificate.uploader_id == uploader_id
        ).first()
        
        if not certificate:
            return False
        
        # Delete associated data
        self.db.query(CertificateData).filter(CertificateData.cert_id == cert_id).delete()
        
        # Delete certificate
        self.db.delete(certificate)
        self.db.commit()
        
        # Delete file from storage
        try:
            if os.path.exists(certificate.file_url):
                os.remove(certificate.file_url)
        except Exception:
            pass  # File deletion is not critical
        
        return True
