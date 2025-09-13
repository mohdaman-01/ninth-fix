"""
AI/ML module endpoints for future AI integration
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.ai_service import AIService
from app.core.security import get_current_active_user, require_admin
from app.models.user import User
from app.schemas.ai_model import (
    AIModelInput, AIModelOutput, AIModelConfig, AIModelStatus,
    AIModelRequest, AIModelResponse, AIModelEvaluation
)
from typing import List, Optional
import uuid

router = APIRouter()

@router.get("/status", response_model=AIModelStatus)
async def get_ai_model_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get AI model status and availability"""
    
    try:
        ai_service = AIService(db)
        return ai_service.get_model_status()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting AI model status: {str(e)}"
        )

@router.post("/predict/{certificate_id}", response_model=AIModelResponse)
async def predict_certificate_authenticity(
    certificate_id: str,
    request: AIModelRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Predict certificate authenticity using AI model"""
    
    try:
        ai_service = AIService(db)
        
        # Get certificate details
        from app.models.certificate import Certificate
        certificate = db.query(Certificate).filter(Certificate.id == certificate_id).first()
        if not certificate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Certificate not found"
            )
        
        # Check if prediction already exists and force_reprocess is False
        if not request.force_reprocess:
            existing_prediction = ai_service.get_certificate_predictions(certificate_id)
            if existing_prediction:
                # Return most recent prediction
                latest = existing_prediction[0]
                return AIModelResponse(
                    certificate_id=certificate_id,
                    prediction=AIModelOutput(
                        probability=latest.probability,
                        confidence_score=latest.confidence_score,
                        prediction="genuine" if latest.probability > 0.5 else "forged",
                        features=None,
                        model_version=latest.model_version,
                        processing_time=0.0
                    ),
                    processing_time=0.0,
                    timestamp=latest.predicted_at
                )
        
        # Run AI prediction
        prediction = ai_service.predict_certificate_authenticity(
            certificate_id, 
            certificate.file_url, 
            certificate.extracted_text
        )
        
        if not prediction:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI model is not available"
            )
        
        # Convert to response format
        prediction_output = AIModelOutput(
            probability=prediction.probability,
            confidence_score=prediction.confidence_score,
            prediction="genuine" if prediction.probability > 0.5 else "forged",
            features=None,
            model_version=prediction.model_version,
            processing_time=0.0  # Placeholder
        )
        
        return AIModelResponse(
            certificate_id=certificate_id,
            prediction=prediction_output,
            processing_time=0.0,  # Placeholder
            timestamp=prediction.predicted_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error predicting certificate authenticity: {str(e)}"
        )

@router.post("/predict/batch")
async def batch_predict_certificates(
    certificate_ids: List[str],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Batch predict multiple certificates"""
    
    try:
        if len(certificate_ids) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many certificates. Maximum 50 per request."
            )
        
        ai_service = AIService(db)
        results = ai_service.batch_predict_certificates(certificate_ids)
        
        return {
            "total_certificates": len(certificate_ids),
            "predictions": results,
            "successful_predictions": sum(1 for r in results.values() if r is not None),
            "failed_predictions": sum(1 for r in results.values() if r is None)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error batch predicting certificates: {str(e)}"
        )

@router.get("/predictions/{certificate_id}")
async def get_certificate_predictions(
    certificate_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all AI predictions for a certificate"""
    
    try:
        ai_service = AIService(db)
        predictions = ai_service.get_certificate_predictions(certificate_id)
        
        return {
            "certificate_id": certificate_id,
            "predictions": [
                {
                    "id": str(pred.id),
                    "probability": pred.probability,
                    "confidence_score": pred.confidence_score,
                    "model_version": pred.model_version,
                    "predicted_at": pred.predicted_at
                }
                for pred in predictions
            ],
            "count": len(predictions)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting certificate predictions: {str(e)}"
        )

@router.get("/config", response_model=AIModelConfig)
async def get_ai_model_config(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get AI model configuration (admin only)"""
    
    try:
        ai_service = AIService(db)
        return ai_service.model_config
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting AI model config: {str(e)}"
        )

@router.put("/config", response_model=AIModelConfig)
async def update_ai_model_config(
    config: AIModelConfig,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update AI model configuration (admin only)"""
    
    try:
        ai_service = AIService(db)
        success = ai_service.update_model_config(config)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update model configuration"
            )
        
        return ai_service.model_config
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating AI model config: {str(e)}"
        )

@router.get("/evaluation", response_model=AIModelEvaluation)
async def get_model_evaluation(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get AI model evaluation metrics (admin only)"""
    
    try:
        ai_service = AIService(db)
        evaluation = ai_service.get_model_evaluation()
        
        return AIModelEvaluation(
            accuracy=evaluation['accuracy'],
            precision=evaluation['precision'],
            recall=evaluation['recall'],
            f1_score=evaluation['f1_score'],
            confusion_matrix=[[0, 0], [0, 0]],  # Placeholder
            evaluation_date=evaluation['evaluation_date'],
            test_samples=evaluation['test_samples'],
            model_version=evaluation['model_version']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting model evaluation: {str(e)}"
        )

@router.post("/retrain")
async def retrain_model(
    training_data: List[dict],
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Retrain AI model with new data (admin only)"""
    
    try:
        if len(training_data) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient training data. Minimum 10 samples required."
            )
        
        ai_service = AIService(db)
        success = ai_service.retrain_model(training_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Model retraining failed"
            )
        
        return {
            "message": "Model retraining initiated successfully",
            "training_samples": len(training_data),
            "status": "in_progress"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retraining model: {str(e)}"
        )

@router.get("/health")
async def ai_health_check(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """AI module health check"""
    
    try:
        ai_service = AIService(db)
        status = ai_service.get_model_status()
        
        return {
            "status": "healthy" if status.is_available else "unhealthy",
            "model_available": status.is_available,
            "model_version": status.model_version,
            "last_updated": status.last_updated,
            "error": status.error_message
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "model_available": False,
            "error": str(e)
        }
