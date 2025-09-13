"""
Setup script for Certificate Verification System
"""

from setuptools import setup, find_packages

setup(
    name="certificate-verification-system",
    version="1.0.0",
    description="Smart, scalable, and secure certificate verification system",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "fastapi==0.111.0",
        "uvicorn[standard]==0.30.1",
        "pydantic==2.8.2",
        "pydantic-settings==2.2.1",
        "python-multipart==0.0.9",
        "pillow==10.4.0",
        "pytesseract==0.3.10",
        "opencv-python-headless==4.10.0.84",
        "numpy==2.0.1",
        "psycopg[binary]==3.2.10",
        "sqlalchemy==2.0.32",
        "alembic==1.13.2",
        "redis==5.0.7",
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4",
        "email-validator==2.2.0",
        "python-dotenv==1.0.1",
        "httpx==0.27.0",
        "boto3==1.34.154",
        "minio==7.2.7",
        "celery==5.4.0",
        "sentry-sdk==2.13.0",
        "aiofiles==24.1.0",
        "google-auth==2.25.2",
    ],
    extras_require={
        "dev": [
            "pytest==7.4.3",
            "pytest-asyncio==0.21.1",
            "black==23.9.1",
            "flake8==6.1.0",
            "mypy==1.6.1",
        ]
    },
    entry_points={
        "console_scripts": [
            "cert-verify=app.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
