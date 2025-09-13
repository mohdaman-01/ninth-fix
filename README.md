# 🎓 Certificate Verification System

A smart, scalable, and secure certificate verification system built with FastAPI that includes OCR text extraction, verification against verified records, and AI-powered authenticity detection.

## 🌟 Features

- **🔐 Google OAuth Authentication** - Secure user authentication with role-based access control
- **📄 OCR Text Extraction** - Extract text from certificate images using Tesseract
- **✅ Certificate Verification** - Match extracted data against verified records
- **📤 Bulk Upload** - Institutions can upload verified records in bulk (CSV/JSON)
- **🤖 AI Integration** - Pluggable AI module for certificate authenticity prediction
- **📊 Admin Dashboard** - Comprehensive monitoring and analytics
- **🚨 Alert System** - Automated alerts for suspicious activities
- **🌐 RESTful API** - Well-documented API with OpenAPI/Swagger documentation

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with Python 3.11+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: Google OAuth with JWT tokens
- **OCR**: Tesseract for text extraction
- **Storage**: Local file storage (configurable for S3/MinIO)
- **AI Ready**: Pluggable AI/ML module for future enhancements

### Frontend (Netlify)
- **Deployment**: https://nova-s-25029.netlify.app
- **Integration**: RESTful API calls to FastAPI backend

## 📁 Project Structure

```
certificate-verification-system/
├── .gitignore                 # Comprehensive security exclusions
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── backend/                   # FastAPI Backend
│   ├── app/
│   │   ├── main.py           # FastAPI application entry point
│   │   ├── core/             # Configuration and security
│   │   ├── api/v1/           # API endpoints
│   │   ├── services/         # Business logic
│   │   ├── schemas/          # Pydantic models
│   │   ├── models/           # Database models
│   │   └── db/               # Database configuration
│   ├── .gitignore            # Backend-specific exclusions
│   ├── README.md             # Backend documentation
│   ├── run.py                # Easy startup script
│   ├── init_db.py            # Database initialization
│   └── env.example           # Environment variables template
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 12+
- Tesseract OCR
- Git

### Backend Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/certificate-verification-system.git
   cd certificate-verification-system
   ```

2. **Set up virtual environment:**
   ```bash
   cd backend
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
   - **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr tesseract-ocr-eng`
   - **macOS**: `brew install tesseract`

5. **Configure environment:**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

6. **Set up database:**
   ```bash
   # Create PostgreSQL database
   createdb certificate_verification
   
   # Initialize database
   python init_db.py
   ```

7. **Run the application:**
   ```bash
   python run.py
   ```

8. **Access API documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 🔧 Configuration

### Environment Variables

Copy `backend/env.example` to `backend/.env` and configure:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/certificate_verification

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# OCR
TESSERACT_CMD=/usr/bin/tesseract
OCR_LANGUAGES=eng

# File Storage
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=jpg,jpeg,png,pdf

# Security
SECRET_KEY=your-secret-key-change-in-production
```

## 📚 API Documentation

### Authentication
- `POST /api/v1/auth/google` - Google Sign-In
- `GET /api/v1/auth/me` - Get current user profile

### OCR
- `POST /api/v1/ocr/extract-text` - Extract text from images
- `POST /api/v1/ocr/extract-and-save/{cert_id}` - Extract and save to DB

### Verification
- `POST /api/v1/verify/certificate/{cert_id}` - Verify certificate
- `POST /api/v1/verify/bulk` - Bulk verification

### Upload
- `POST /api/v1/upload/certificate` - Upload certificate file
- `POST /api/v1/upload/verified-records/bulk` - Bulk upload verified records

### Admin Dashboard
- `GET /api/v1/dashboard/stats` - Dashboard statistics
- `GET /api/v1/dashboard/trends` - Verification trends

### Alerts
- `GET /api/v1/alerts/` - Get alerts
- `POST /api/v1/alerts/{alert_id}/resolve` - Resolve alert

### AI Module
- `GET /api/v1/ai/status` - AI model status
- `POST /api/v1/ai/predict/{cert_id}` - Predict authenticity

## 🗄️ Database Schema

### Tables
- **users** - Google-authenticated users with roles
- **certificates** - Uploaded certificate files and metadata
- **certificate_data** - Extracted OCR data
- **verified_records** - Official verified records from institutions
- **alerts** - System alerts and warnings
- **ai_predictions** - AI model predictions (future-ready)

### Relationships
- users (1) ────< certificates (N)
- certificates (1) ────< certificate_data (1)
- certificates (1) ────< alerts (N)
- certificates (1) ────< ai_predictions (1)

## 👥 User Roles

- **admin** - Full system access, dashboard, user management
- **institution** - Upload verified records, view analytics
- **employer** - Upload certificates for verification

## 🔒 Security Features

- JWT token-based authentication
- Role-based access control (RBAC)
- CORS protection
- Input validation with Pydantic
- File upload security
- Environment variable protection
- Comprehensive .gitignore

## 🚀 Deployment

### Heroku
1. Create Heroku app
2. Set environment variables
3. Deploy: `git push heroku main`

### Local Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For support and questions, please open an issue on GitHub.

## 🔗 Links

- **Frontend**: https://nova-s-25029.netlify.app
- **API Documentation**: http://localhost:8000/docs (when running locally)
- **Backend Repository**: This repository

---

**Built with ❤️ using FastAPI, PostgreSQL, and modern web technologies**
