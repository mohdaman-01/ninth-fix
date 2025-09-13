"""
Google authentication service
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserProfile
from app.core.security import verify_google_token, create_access_token
from datetime import timedelta
from app.core.config import settings

class GoogleAuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, id_token: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with Google ID token"""
        google_data = verify_google_token(id_token)
        if not google_data:
            return None

        # Check if user exists
        user = self.db.query(User).filter(
            User.google_id == google_data['google_id']
        ).first()

        if not user:
            # Create new user
            user_data = UserCreate(
                google_id=google_data['google_id'],
                email=google_data['email'],
                name=google_data['name'],
                picture_url=google_data.get('picture_url'),
                email_verified=google_data.get('email_verified', False)
            )
            user = self._create_user(user_data)
        else:
            # Update existing user info
            user.name = google_data['name']
            user.picture_url = google_data.get('picture_url')
            self.db.commit()

        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserProfile.from_orm(user)
        }

    def _create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        user = User(
            google_id=user_data.google_id,
            email=user_data.email,
            name=user_data.name,
            picture_url=user_data.picture_url,
            role=user_data.role
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def update_user_role(self, user_id: str, role: str) -> Optional[User]:
        """Update user role (admin only)"""
        user = self.get_user_by_id(user_id)
        if user:
            user.role = role
            self.db.commit()
            self.db.refresh(user)
        return user
