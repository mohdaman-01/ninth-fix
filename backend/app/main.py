"""
FastAPI Certificate Verification System
Main application entry point
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import os
from dotenv import load_dotenv

from app.core.config import settings
from app.api.v1 import auth_google, ocr, verify, upload, dashboard, alerts, ai_module

# Load environment variables
load_dotenv()

# Initialize database (with error handling)
try:
    from app.db.session import engine
    from app.db.base import Base
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database connected and tables created")
except Exception as e:
    print(f"⚠️ Database connection failed: {e}")
    print("App will start without database - add PostgreSQL service in Railway")

# Initialize FastAPI app
app = FastAPI(
    title="Certificate Verification System",
    description="Smart, scalable, and secure certificate verification system",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.ALLOWED_HOSTS
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth_google.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(ocr.router, prefix="/api/v1/ocr", tags=["OCR"])
app.include_router(verify.router, prefix="/api/v1/verify", tags=["Verification"])
app.include_router(upload.router, prefix="/api/v1/upload", tags=["Upload"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(ai_module.router, prefix="/api/v1/ai", tags=["AI Module"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Certificate Verification System API", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    # Check database connection
    db_status = "disconnected"
    try:
        from app.db.session import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "database": db_status,
        "services": {
            "ocr": "available",
            "verification": "available" if db_status == "connected" else "limited",
            "ai_module": "available"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
