"""
Alert management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.db.session import get_db
from app.core.security import get_current_active_user, require_admin
from app.models.user import User
from app.models.certificate import Alert, Certificate
from app.schemas.certificate import Alert as AlertSchema, AlertLevel
from datetime import datetime, timedelta
from typing import List, Optional

router = APIRouter()

@router.get("/", response_model=List[AlertSchema])
async def get_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    level: Optional[AlertLevel] = Query(None),
    resolved: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get alerts with filtering options"""
    
    try:
        query = db.query(Alert)
        
        # Apply filters
        if level:
            query = query.filter(Alert.level == level)
        
        if resolved is not None:
            query = query.filter(Alert.resolved == resolved)
        
        # Order by most recent first
        query = query.order_by(Alert.flagged_at.desc())
        
        # Apply pagination
        alerts = query.offset(skip).limit(limit).all()
        
        return alerts
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting alerts: {str(e)}"
        )

@router.get("/{alert_id}", response_model=AlertSchema)
async def get_alert(
    alert_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific alert by ID"""
    
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        return alert
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting alert: {str(e)}"
        )

@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Resolve an alert (admin only)"""
    
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        if alert.resolved:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Alert is already resolved"
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

@router.post("/{alert_id}/unresolve")
async def unresolve_alert(
    alert_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Unresolve an alert (admin only)"""
    
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        if not alert.resolved:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Alert is not resolved"
            )
        
        alert.resolved = False
        alert.resolved_at = None
        db.commit()
        
        return {"message": "Alert unresolved successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error unresolving alert: {str(e)}"
        )

@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete an alert (admin only)"""
    
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        db.delete(alert)
        db.commit()
        
        return {"message": "Alert deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting alert: {str(e)}"
        )

@router.get("/certificate/{certificate_id}")
async def get_certificate_alerts(
    certificate_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all alerts for a specific certificate"""
    
    try:
        # Check if certificate exists and user has access
        certificate = db.query(Certificate).filter(Certificate.id == certificate_id).first()
        if not certificate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Certificate not found"
            )
        
        # Check if user has access to this certificate
        if current_user.role != "admin" and str(certificate.uploader_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        alerts = db.query(Alert).filter(
            Alert.cert_id == certificate_id
        ).order_by(Alert.flagged_at.desc()).all()
        
        return {
            "certificate_id": certificate_id,
            "alerts": [
                {
                    "id": str(alert.id),
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
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting certificate alerts: {str(e)}"
        )

@router.get("/stats/summary")
async def get_alert_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get alert summary statistics"""
    
    try:
        # Total alerts
        total_alerts = db.query(Alert).count()
        
        # Unresolved alerts
        unresolved_alerts = db.query(Alert).filter(Alert.resolved == False).count()
        
        # Critical alerts
        critical_alerts = db.query(Alert).filter(Alert.level == AlertLevel.CRITICAL).count()
        
        # Warning alerts
        warning_alerts = db.query(Alert).filter(Alert.level == AlertLevel.WARNING).count()
        
        # Alerts from last 24 hours
        twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
        recent_alerts = db.query(Alert).filter(
            Alert.flagged_at >= twenty_four_hours_ago
        ).count()
        
        # Alerts from last 7 days
        seven_days_ago = datetime.now() - timedelta(days=7)
        weekly_alerts = db.query(Alert).filter(
            Alert.flagged_at >= seven_days_ago
        ).count()
        
        return {
            "total_alerts": total_alerts,
            "unresolved_alerts": unresolved_alerts,
            "critical_alerts": critical_alerts,
            "warning_alerts": warning_alerts,
            "recent_alerts_24h": recent_alerts,
            "recent_alerts_7d": weekly_alerts,
            "resolution_rate": (total_alerts - unresolved_alerts) / total_alerts if total_alerts > 0 else 0
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting alert summary: {str(e)}"
        )

@router.post("/bulk-resolve")
async def bulk_resolve_alerts(
    alert_ids: List[str],
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Bulk resolve multiple alerts (admin only)"""
    
    try:
        if len(alert_ids) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many alerts. Maximum 100 per request."
            )
        
        alerts = db.query(Alert).filter(Alert.id.in_(alert_ids)).all()
        
        resolved_count = 0
        for alert in alerts:
            if not alert.resolved:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                resolved_count += 1
        
        db.commit()
        
        return {
            "message": f"Bulk resolve completed",
            "total_requested": len(alert_ids),
            "resolved": resolved_count,
            "already_resolved": len(alert_ids) - resolved_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error bulk resolving alerts: {str(e)}"
        )
