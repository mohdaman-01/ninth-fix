"""
Admin dashboard endpoints for monitoring and analytics
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.db.session import get_db
from app.core.security import require_admin, get_current_active_user
from app.models.user import User
from app.models.certificate import Certificate, VerifiedRecord, Alert, AIPrediction
from app.schemas.certificate import DashboardStats, VerificationTrend, InstitutionStats
from datetime import datetime, timedelta
from typing import List, Optional

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get overall dashboard statistics"""
    
    try:
        # Total certificates
        total_certificates = db.query(Certificate).count()
        
        # Verified certificates
        verified_certificates = db.query(Certificate).filter(
            Certificate.status == "verified"
        ).count()
        
        # Forged certificates
        forged_certificates = db.query(Certificate).filter(
            Certificate.status == "forged"
        ).count()
        
        # Pending certificates
        pending_certificates = db.query(Certificate).filter(
            Certificate.status == "pending"
        ).count()
        
        # Total alerts
        total_alerts = db.query(Alert).count()
        
        # Critical alerts
        critical_alerts = db.query(Alert).filter(
            Alert.level == "critical"
        ).count()
        
        # Calculate rates
        verification_rate = verified_certificates / total_certificates if total_certificates > 0 else 0
        forgery_rate = forged_certificates / total_certificates if total_certificates > 0 else 0
        
        return DashboardStats(
            total_certificates=total_certificates,
            verified_certificates=verified_certificates,
            forged_certificates=forged_certificates,
            pending_certificates=pending_certificates,
            total_alerts=total_alerts,
            critical_alerts=critical_alerts,
            verification_rate=verification_rate,
            forgery_rate=forgery_rate
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting dashboard stats: {str(e)}"
        )

@router.get("/trends", response_model=List[VerificationTrend])
async def get_verification_trends(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get verification trends over time"""
    
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get daily verification counts
        trends = []
        current_date = start_date
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            
            verified_count = db.query(Certificate).filter(
                and_(
                    Certificate.status == "verified",
                    Certificate.processed_at >= current_date,
                    Certificate.processed_at < next_date
                )
            ).count()
            
            forged_count = db.query(Certificate).filter(
                and_(
                    Certificate.status == "forged",
                    Certificate.processed_at >= current_date,
                    Certificate.processed_at < next_date
                )
            ).count()
            
            pending_count = db.query(Certificate).filter(
                and_(
                    Certificate.status == "pending",
                    Certificate.submitted_at >= current_date,
                    Certificate.submitted_at < next_date
                )
            ).count()
            
            trends.append(VerificationTrend(
                date=current_date,
                verified_count=verified_count,
                forged_count=forged_count,
                pending_count=pending_count
            ))
            
            current_date = next_date
        
        return trends
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting trends: {str(e)}"
        )

@router.get("/institutions", response_model=List[InstitutionStats])
async def get_institution_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get statistics by institution"""
    
    try:
        # Get institution statistics from verified records
        institution_stats = db.query(
            VerifiedRecord.issuer,
            func.count(VerifiedRecord.id).label('total_uploads'),
            func.count(Certificate.id).label('verified_certificates'),
            func.count(
                func.case(
                    (Certificate.status == "forged", Certificate.id),
                    else_=None
                )
            ).label('forged_certificates')
        ).outerjoin(
            Certificate, 
            VerifiedRecord.cert_number == Certificate.id  # This might need adjustment based on your schema
        ).group_by(VerifiedRecord.issuer).all()
        
        stats = []
        for stat in institution_stats:
            total_uploads = stat.total_uploads or 0
            verified_certificates = stat.verified_certificates or 0
            forged_certificates = stat.forged_certificates or 0
            
            verification_rate = verified_certificates / total_uploads if total_uploads > 0 else 0
            forgery_rate = forged_certificates / total_uploads if total_uploads > 0 else 0
            
            stats.append(InstitutionStats(
                institution_name=stat.issuer,
                total_uploads=total_uploads,
                verification_rate=verification_rate,
                forgery_rate=forgery_rate
            ))
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting institution stats: {str(e)}"
        )

@router.get("/alerts")
async def get_recent_alerts(
    limit: int = Query(50, ge=1, le=200),
    level: Optional[str] = Query(None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get recent alerts"""
    
    try:
        query = db.query(Alert).order_by(Alert.flagged_at.desc())
        
        if level:
            query = query.filter(Alert.level == level)
        
        alerts = query.limit(limit).all()
        
        return {
            "alerts": [
                {
                    "id": str(alert.id),
                    "certificate_id": str(alert.cert_id),
                    "reason": alert.reason,
                    "level": alert.level,
                    "flagged_at": alert.flagged_at,
                    "resolved": alert.resolved,
                    "resolved_at": alert.resolved_at
                }
                for alert in alerts
            ],
            "count": len(alerts)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting alerts: {str(e)}"
        )

@router.get("/ai-predictions")
async def get_ai_predictions_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get AI predictions statistics"""
    
    try:
        # Total predictions
        total_predictions = db.query(AIPrediction).count()
        
        # Average confidence
        avg_confidence = db.query(func.avg(AIPrediction.confidence_score)).scalar() or 0
        
        # Predictions by model version
        model_versions = db.query(
            AIPrediction.model_version,
            func.count(AIPrediction.id).label('count')
        ).group_by(AIPrediction.model_version).all()
        
        # High confidence predictions (>0.8)
        high_confidence = db.query(AIPrediction).filter(
            AIPrediction.confidence_score > 0.8
        ).count()
        
        return {
            "total_predictions": total_predictions,
            "average_confidence": round(avg_confidence, 3),
            "high_confidence_predictions": high_confidence,
            "model_versions": [
                {"version": version, "count": count}
                for version, count in model_versions
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting AI predictions stats: {str(e)}"
        )

@router.get("/users")
async def get_user_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get user statistics"""
    
    try:
        from app.models.user import User
        
        # Total users
        total_users = db.query(User).count()
        
        # Users by role
        role_stats = db.query(
            User.role,
            func.count(User.id).label('count')
        ).group_by(User.role).all()
        
        # Active users (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        active_users = db.query(User).filter(
            User.created_at >= thirty_days_ago
        ).count()
        
        return {
            "total_users": total_users,
            "active_users_30_days": active_users,
            "users_by_role": [
                {"role": role, "count": count}
                for role, count in role_stats
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user stats: {str(e)}"
        )

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Resolve an alert"""
    
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        alert.resolved = True
        alert.resolved_at = datetime.now()
        db.commit()
        
        return {"message": "Alert resolved successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resolving alert: {str(e)}"
        )
