"""
Certificate verification service
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.certificate import Certificate, CertificateData, VerifiedRecord, Alert, AIPrediction
from app.models.user import User
from app.schemas.certificate import VerificationRequest, VerificationResponse, AlertLevel
from app.core.config import settings
from difflib import SequenceMatcher
import re

class VerificationService:
    def __init__(self, db: Session):
        self.db = db

    def verify_certificate(self, cert_id: str, verification_request: VerificationRequest) -> VerificationResponse:
        """Verify a certificate against verified records"""
        certificate = self.db.query(Certificate).filter(Certificate.id == cert_id).first()
        if not certificate:
            raise ValueError("Certificate not found")

        # Get certificate data
        cert_data = self.db.query(CertificateData).filter(CertificateData.cert_id == cert_id).first()
        
        # Get verification criteria
        criteria = self._build_verification_criteria(verification_request, cert_data)
        
        # Find matching verified records
        matches = self._find_matching_records(criteria)
        
        # Calculate verification result
        verification_result = self._calculate_verification_result(certificate, cert_data, matches)
        
        # Create alerts if needed
        alerts = self._create_alerts_if_needed(certificate, verification_result)
        
        # Get AI prediction if available
        ai_prediction = self._get_ai_prediction(cert_id)
        
        return VerificationResponse(
            is_verified=verification_result['is_verified'],
            confidence_score=verification_result['confidence_score'],
            matched_record=verification_result.get('matched_record'),
            mismatches=verification_result.get('mismatches', []),
            alerts=alerts,
            ai_prediction=ai_prediction
        )

    def _build_verification_criteria(self, request: VerificationRequest, cert_data: Optional[CertificateData]) -> Dict[str, str]:
        """Build verification criteria from request and certificate data"""
        criteria = {}
        
        # Use request data first, fallback to certificate data
        criteria['student_name'] = request.student_name or (cert_data.student_name if cert_data else None)
        criteria['roll_number'] = request.roll_number or (cert_data.roll_number if cert_data else None)
        criteria['cert_number'] = request.cert_number or (cert_data.cert_number if cert_data else None)
        criteria['issuer'] = request.issuer
        
        return {k: v for k, v in criteria.items() if v}

    def _find_matching_records(self, criteria: Dict[str, str]) -> List[VerifiedRecord]:
        """Find verified records matching the criteria"""
        if not criteria:
            return []

        query = self.db.query(VerifiedRecord)
        
        # Build dynamic query based on available criteria
        conditions = []
        
        if 'student_name' in criteria:
            conditions.append(
                or_(
                    VerifiedRecord.student_name.ilike(f"%{criteria['student_name']}%"),
                    self._fuzzy_match_condition(VerifiedRecord.student_name, criteria['student_name'])
                )
            )
        
        if 'roll_number' in criteria:
            conditions.append(
                or_(
                    VerifiedRecord.roll_number.ilike(f"%{criteria['roll_number']}%"),
                    VerifiedRecord.roll_number == criteria['roll_number']
                )
            )
        
        if 'cert_number' in criteria:
            conditions.append(VerifiedRecord.cert_number == criteria['cert_number'])
        
        if 'issuer' in criteria:
            conditions.append(VerifiedRecord.issuer.ilike(f"%{criteria['issuer']}%"))
        
        if conditions:
            query = query.filter(and_(*conditions))
        
        return query.limit(10).all()

    def _fuzzy_match_condition(self, column, value: str, threshold: float = 0.8):
        """Create a fuzzy match condition for database query"""
        # This is a simplified version - in production, you might want to use
        # PostgreSQL's similarity functions or implement a more sophisticated matching
        return column.ilike(f"%{value}%")

    def _calculate_verification_result(self, certificate: Certificate, cert_data: Optional[CertificateData], matches: List[VerifiedRecord]) -> Dict[str, Any]:
        """Calculate verification result based on matches"""
        if not matches:
            return {
                'is_verified': False,
                'confidence_score': 0.0,
                'mismatches': ['No matching verified records found']
            }

        best_match = None
        best_score = 0.0
        mismatches = []

        for match in matches:
            score, match_mismatches = self._calculate_match_score(cert_data, match)
            if score > best_score:
                best_score = score
                best_match = match
                mismatches = match_mismatches

        is_verified = best_score >= settings.VERIFICATION_THRESHOLD

        return {
            'is_verified': is_verified,
            'confidence_score': best_score,
            'matched_record': best_match,
            'mismatches': mismatches
        }

    def _calculate_match_score(self, cert_data: Optional[CertificateData], verified_record: VerifiedRecord) -> Tuple[float, List[str]]:
        """Calculate match score between certificate data and verified record"""
        if not cert_data:
            return 0.0, ['No certificate data available']

        score = 0.0
        total_fields = 0
        mismatches = []

        # Compare student name
        if cert_data.student_name and verified_record.student_name:
            total_fields += 1
            name_similarity = self._calculate_similarity(cert_data.student_name, verified_record.student_name)
            if name_similarity >= 0.8:
                score += name_similarity
            else:
                mismatches.append(f"Student name mismatch: '{cert_data.student_name}' vs '{verified_record.student_name}'")

        # Compare roll number
        if cert_data.roll_number and verified_record.roll_number:
            total_fields += 1
            if cert_data.roll_number.lower() == verified_record.roll_number.lower():
                score += 1.0
            else:
                mismatches.append(f"Roll number mismatch: '{cert_data.roll_number}' vs '{verified_record.roll_number}'")

        # Compare certificate number
        if cert_data.cert_number and verified_record.cert_number:
            total_fields += 1
            if cert_data.cert_number.lower() == verified_record.cert_number.lower():
                score += 1.0
            else:
                mismatches.append(f"Certificate number mismatch: '{cert_data.cert_number}' vs '{verified_record.cert_number}'")

        # Compare marks (optional)
        if cert_data.marks and verified_record.marks:
            total_fields += 0.5  # Lower weight for marks
            marks_similarity = self._calculate_similarity(cert_data.marks, verified_record.marks)
            if marks_similarity >= 0.7:
                score += marks_similarity * 0.5
            else:
                mismatches.append(f"Marks mismatch: '{cert_data.marks}' vs '{verified_record.marks}'")

        if total_fields == 0:
            return 0.0, ['No comparable fields found']

        return score / total_fields, mismatches

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        # Normalize strings
        str1 = re.sub(r'[^\w\s]', '', str1.lower().strip())
        str2 = re.sub(r'[^\w\s]', '', str2.lower().strip())
        
        return SequenceMatcher(None, str1, str2).ratio()

    def _create_alerts_if_needed(self, certificate: Certificate, verification_result: Dict[str, Any]) -> List[Alert]:
        """Create alerts if verification fails or shows suspicious patterns"""
        alerts = []
        
        if not verification_result['is_verified']:
            # Create critical alert for failed verification
            alert = Alert(
                cert_id=certificate.id,
                reason="Certificate verification failed - no matching verified records",
                level=AlertLevel.CRITICAL
            )
            self.db.add(alert)
            alerts.append(alert)
        
        # Check for suspicious patterns
        if verification_result.get('confidence_score', 0) < 0.5:
            alert = Alert(
                cert_id=certificate.id,
                reason=f"Low confidence score: {verification_result['confidence_score']:.2f}",
                level=AlertLevel.WARNING
            )
            self.db.add(alert)
            alerts.append(alert)
        
        # Check for multiple mismatches
        mismatches = verification_result.get('mismatches', [])
        if len(mismatches) > 2:
            alert = Alert(
                cert_id=certificate.id,
                reason=f"Multiple mismatches detected: {len(mismatches)} issues",
                level=AlertLevel.CRITICAL
            )
            self.db.add(alert)
            alerts.append(alert)
        
        self.db.commit()
        return alerts

    def _get_ai_prediction(self, cert_id: str) -> Optional[AIPrediction]:
        """Get AI prediction for certificate if available"""
        return self.db.query(AIPrediction).filter(AIPrediction.cert_id == cert_id).first()

    def bulk_verify_certificates(self, certificate_ids: List[str]) -> Dict[str, VerificationResponse]:
        """Bulk verify multiple certificates"""
        results = {}
        
        for cert_id in certificate_ids:
            try:
                certificate = self.db.query(Certificate).filter(Certificate.id == cert_id).first()
                if certificate:
                    cert_data = self.db.query(CertificateData).filter(CertificateData.cert_id == cert_id).first()
                    verification_request = VerificationRequest(
                        student_name=cert_data.student_name if cert_data else None,
                        roll_number=cert_data.roll_number if cert_data else None,
                        cert_number=cert_data.cert_number if cert_data else None
                    )
                    results[cert_id] = self.verify_certificate(cert_id, verification_request)
                else:
                    results[cert_id] = VerificationResponse(
                        is_verified=False,
                        confidence_score=0.0,
                        mismatches=["Certificate not found"]
                    )
            except Exception as e:
                results[cert_id] = VerificationResponse(
                    is_verified=False,
                    confidence_score=0.0,
                    mismatches=[f"Verification error: {str(e)}"]
                )
        
        return results
