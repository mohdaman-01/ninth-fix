"""
Certificate models for uploaded certificates and verification data
"""

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    uploader_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_url = Column(Text, nullable=False)
    extracted_text = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="pending")  # pending, verified, forged
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    uploader = relationship("User", back_populates="certificates")
    certificate_data = relationship("CertificateData", back_populates="certificate", uselist=False)
    alerts = relationship("Alert", back_populates="certificate")
    ai_predictions = relationship("AIPrediction", back_populates="certificate")

    def __repr__(self):
        return f"<Certificate(id={self.id}, filename={self.filename}, status={self.status})>"

class CertificateData(Base):
    __tablename__ = "certificate_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cert_id = Column(UUID(as_uuid=True), ForeignKey("certificates.id"), nullable=False)
    student_name = Column(String, nullable=True)
    roll_number = Column(String, nullable=True)
    marks = Column(String, nullable=True)
    cert_number = Column(String, nullable=True)
    extracted_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    certificate = relationship("Certificate", back_populates="certificate_data")

    def __repr__(self):
        return f"<CertificateData(id={self.id}, student_name={self.student_name})>"

class VerifiedRecord(Base):
    __tablename__ = "verified_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_name = Column(String, nullable=False, index=True)
    roll_number = Column(String, nullable=False, index=True)
    marks = Column(String, nullable=True)
    cert_number = Column(String, nullable=False, unique=True, index=True)
    issuer = Column(String, nullable=False)
    issued_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<VerifiedRecord(id={self.id}, student_name={self.student_name}, cert_number={self.cert_number})>"

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cert_id = Column(UUID(as_uuid=True), ForeignKey("certificates.id"), nullable=False)
    reason = Column(Text, nullable=False)
    level = Column(String, nullable=False)  # warning, critical
    flagged_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    certificate = relationship("Certificate", back_populates="alerts")

    def __repr__(self):
        return f"<Alert(id={self.id}, level={self.level}, reason={self.reason})>"

class AIPrediction(Base):
    __tablename__ = "ai_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cert_id = Column(UUID(as_uuid=True), ForeignKey("certificates.id"), nullable=False)
    probability = Column(Float, nullable=False)  # Likelihood it's genuine (0-1)
    model_version = Column(String, nullable=False)
    predicted_at = Column(DateTime(timezone=True), server_default=func.now())
    confidence_score = Column(Float, nullable=True)
    model_metadata = Column(Text, nullable=True)  # JSON string for additional model info

    # Relationships
    certificate = relationship("Certificate", back_populates="ai_predictions")

    def __repr__(self):
        return f"<AIPrediction(id={self.id}, probability={self.probability}, model_version={self.model_version})>"
