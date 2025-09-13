"""
Google authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import GoogleAuthRequest, GoogleAuthResponse, UserProfile
from app.services.google_auth import GoogleAuthService
from app.core.security import get_current_active_user
from app.models.user import User
from app.core.config import settings
import urllib.parse

router = APIRouter()

@router.get("/google")
async def google_oauth_redirect():
    """Redirect to Google OAuth"""
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables."
        )
    
    # Google OAuth URL
    google_oauth_url = "https://accounts.google.com/o/oauth2/auth"
    
    # OAuth parameters
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": f"{settings.BASE_URL}/api/v1/auth/google/callback",
        "scope": "openid email profile",
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent"
    }
    
    # Build the OAuth URL
    oauth_url = f"{google_oauth_url}?{urllib.parse.urlencode(params)}"
    
    return RedirectResponse(url=oauth_url)

@router.get("/google/callback")
async def google_oauth_callback(
    code: str = None,
    error: str = None,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback"""
    if error:
        # Redirect to frontend with error
        frontend_url = "https://nova-s-25029.netlify.app/sign-in?error=" + urllib.parse.quote(error)
        return RedirectResponse(url=frontend_url)
    
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code not provided"
        )
    
    try:
        # Exchange code for tokens (this would need Google OAuth service implementation)
        auth_service = GoogleAuthService(db)
        result = auth_service.exchange_code_for_token(code)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to authenticate with Google"
            )
        
        # Redirect to frontend with success
        frontend_url = f"https://nova-s-25029.netlify.app/?token={result.access_token}&user={urllib.parse.quote(result.user.json())}"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        # Redirect to frontend with error
        frontend_url = f"https://nova-s-25029.netlify.app/sign-in?error={urllib.parse.quote(str(e))}"
        return RedirectResponse(url=frontend_url)

@router.post("/google", response_model=GoogleAuthResponse)
async def google_auth(
    auth_request: GoogleAuthRequest,
    db: Session = Depends(get_db)
):
    """Authenticate user with Google ID token"""
    auth_service = GoogleAuthService(db)
    
    result = auth_service.authenticate_user(auth_request.id_token)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )
    
    return result

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user profile"""
    return UserProfile.from_orm(current_user)

@router.post("/logout")
async def logout():
    """Logout user (client-side token removal)"""
    return {"message": "Logged out successfully"}

@router.get("/verify-token")
async def verify_token(
    current_user: User = Depends(get_current_active_user)
):
    """Verify if token is valid"""
    return {"valid": True, "user_id": str(current_user.id)}
