# Certificate Verification System

A smart, scalable, and secure certificate verification system built with FastAPI that includes OCR text extraction, verification against verified records, and AI-powered authenticity detection.

## Features

- **Google OAuth Authentication** - Secure user authentication with role-based access control
- **OCR Text Extraction** - Extract text from certificate images using Tesseract
- **Certificate Verification** - Match extracted data against verified records
- **Bulk Upload** - Institutions can upload verified records in bulk (CSV/JSON)
- **AI Integration** - Pluggable AI module for certificate authenticity prediction
- **Admin Dashboard** - Comprehensive monitoring and analytics
- **Alert System** - Automated alerts for suspicious activities
- **RESTful API** - Well-documented API with OpenAPI/Swagger documentation

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                        # Entry point
│   ├── core/
│   │   ├── config.py                  # Configuration settings
│   │   └── security.py                # Authentication & authorization
│   ├── api/v1/
│   │   ├── auth_google.py             # Google Sign-In endpoints
│   │   ├── ocr.py                     # OCR text extraction
│   │   ├── verify.py                  # Certificate verification
│   │   ├── upload.py                  # File upload & bulk upload
│   │   ├── dashboard.py               # Admin dashboard
│   │   ├── alerts.py                  # Alert management
│   │   └── ai_module.py               # AI/ML integration
│   ├── services/
│   │   ├── google_auth.py             # Google authentication service
│   │   ├── ocr_service.py             # OCR processing
│   │   ├── verification_service.py    # Certificate verification logic
│   │   ├── uploader_service.py        # File upload handling
│   │   └── ai_service.py              # AI/ML service
│   ├── schemas/
│   │   ├── user.py                    # User data schemas
│   │   ├── certificate.py             # Certificate schemas
│   │   └── ai_model.py                # AI model schemas
│   ├── models/
│   │   ├── user.py                    # User database model
│   │   └── certificate.py             # Certificate database models
│   └── db/
│       ├── base.py                    # SQLAlchemy base
│       └── session.py                 # Database session
├── requirements.txt                   # Python dependencies
├── setup.py                          # Package setup
├── env.example                       # Environment variables template
├── Procfile                          # Heroku deployment
├── runtime.txt                       # Python version
└── README.md                         # This file
```

## Database Schema

### Tables

1. **users** - Google-authenticated users
2. **certificates** - Uploaded certificate files and metadata
3. **certificate_data** - Extracted OCR data from certificates
4. **verified_records** - Official verified records from institutions
5. **alerts** - System alerts and warnings
6. **ai_predictions** - AI model predictions (future)

### Relationships

- users (1) ────< certificates (N)
- certificates (1) ────< certificate_data (1)
- certificates (1) ────< alerts (N)
- certificates (1) ────< ai_predictions (1)

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Redis (optional, for caching)
- Tesseract OCR

### Setup

1. **Clone and navigate to the project:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR:**
   - **Windows:** Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - **Ubuntu/Debian:** `sudo apt-get install tesseract-ocr tesseract-ocr-eng`
   - **macOS:** `brew install tesseract`

5. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

6. **Set up database:**
   ```bash
   # Create PostgreSQL database
   createdb certificate_verification
   
   # Run database migrations (if using Alembic)
   alembic upgrade head
   ```

7. **Run the application:**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

## Configuration

### Environment Variables

Copy `env.example` to `.env` and configure:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/certificate_verification

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# OCR
TESSERACT_CMD=/usr/bin/tesseract  # Path to tesseract executable
OCR_LANGUAGES=eng

# File Storage
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=jpg,jpeg,png,pdf

# Security
SECRET_KEY=your-secret-key-change-in-production
```

## API Documentation

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Usage

### 1. Authentication

```bash
# Google Sign-In
POST /api/v1/auth/google
{
  "id_token": "google_id_token"
}
```

### 2. Upload Certificate

```bash
# Upload certificate file
POST /api/v1/upload/certificate
Content-Type: multipart/form-data
file: certificate_image.jpg
```

### 3. Extract Text (OCR)

```bash
# Extract text from image
POST /api/v1/ocr/extract-text
Content-Type: multipart/form-data
file: certificate_image.jpg
```

### 4. Verify Certificate

```bash
# Verify certificate
POST /api/v1/verify/certificate/{certificate_id}
{
  "student_name": "John Doe",
  "roll_number": "2023001",
  "cert_number": "CERT-2023-001"
}
```

### 5. Bulk Upload Verified Records

```bash
# Upload verified records (institutions only)
POST /api/v1/upload/verified-records/bulk
[
  {
    "student_name": "John Doe",
    "roll_number": "2023001",
    "cert_number": "CERT-2023-001",
    "issuer": "University of Example",
    "issued_at": "2023-06-15T00:00:00"
  }
]
```

## User Roles

- **admin** - Full system access, dashboard, user management
- **institution** - Upload verified records, view analytics
- **employer** - Upload certificates for verification

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black app/
flake8 app/
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## Deployment

### Heroku

1. Create Heroku app
2. Set environment variables
3. Deploy:
   ```bash
   git push heroku main
   ```

### Local Production

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Future Enhancements

- [ ] Blockchain integration for certificate immutability
- [ ] Advanced AI/ML models for forgery detection
- [ ] Real-time notifications
- [ ] Mobile app integration
- [ ] Advanced analytics and reporting
- [ ] Multi-language OCR support
- [ ] Certificate templates and validation rules

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For support and questions, please open an issue on GitHub.
