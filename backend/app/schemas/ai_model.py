"""
AI/ML model schemas for future AI integration
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

class AIModelInput(BaseModel):
    """Input schema for AI model inference"""
    image_url: str
    extracted_text: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AIModelOutput(BaseModel):
    """Output schema for AI model inference"""
    probability: float = Field(..., ge=0.0, le=1.0)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    prediction: str  # "genuine", "forged", "uncertain"
    features: Optional[Dict[str, Any]] = None
    model_version: str
    processing_time: float

class AIModelConfig(BaseModel):
    """Configuration for AI model"""
    model_name: str
    version: str
    threshold: float = Field(0.5, ge=0.0, le=1.0)
    enabled: bool = True
    batch_size: int = Field(1, ge=1, le=100)
    max_processing_time: float = Field(30.0, ge=1.0, le=300.0)

class AIModelStatus(BaseModel):
    """Status of AI model service"""
    is_available: bool
    model_version: Optional[str] = None
    last_updated: Optional[datetime] = None
    error_message: Optional[str] = None
    performance_metrics: Optional[Dict[str, float]] = None

class AIModelTrainingData(BaseModel):
    """Schema for AI model training data"""
    image_url: str
    label: str  # "genuine" or "forged"
    metadata: Optional[Dict[str, Any]] = None
    verified_by: str
    verified_at: datetime

class AIModelEvaluation(BaseModel):
    """Schema for AI model evaluation results"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    confusion_matrix: List[List[int]]
    evaluation_date: datetime
    test_samples: int
    model_version: str

class AIModelRequest(BaseModel):
    """Request schema for AI model inference"""
    certificate_id: UUID
    force_reprocess: bool = False

class AIModelResponse(BaseModel):
    """Response schema for AI model inference"""
    certificate_id: UUID
    prediction: AIModelOutput
    processing_time: float
    timestamp: datetime
