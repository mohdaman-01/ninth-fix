# Railway Deployment Guide

## Files Added/Modified for Railway Deployment

1. **nixpacks.toml** - Nixpacks configuration for Railway
2. **railway.toml** - Railway-specific deployment settings
3. **start.sh** - Startup script to handle directory structure
4. **Dockerfile** - Alternative Docker deployment option
5. **.env.example** - Environment variables template
6. **requirements.txt** - Added gunicorn for production

## Deployment Steps

### 1. Connect to Railway
1. Go to [railway.app](https://railway.app)
2. Sign up/login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository

### 2. Configure Environment Variables
In Railway dashboard, go to Variables tab and add:

**Required:**
- `GOOGLE_CLIENT_ID` - Your Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Your Google OAuth client secret
- `SECRET_KEY` - A secure random string for JWT tokens

**Optional (Railway provides automatically):**
- `DATABASE_URL` - PostgreSQL connection (add PostgreSQL service)
- `REDIS_URL` - Redis connection (add Redis service)

### 3. Add Services
1. **PostgreSQL**: Click "New" → "Database" → "Add PostgreSQL"
2. **Redis** (optional): Click "New" → "Database" → "Add Redis"

### 4. Deploy
Railway will automatically deploy when you push to your main branch.

## Troubleshooting

### Build Failures
- Check the build logs in Railway dashboard
- Ensure all environment variables are set
- Verify the nixpacks.toml configuration

### Runtime Issues
- Check application logs in Railway dashboard
- Verify database connection
- Ensure health check endpoint `/health` is accessible

### Common Issues
1. **Import errors**: Check PYTHONPATH in nixpacks.toml
2. **Database connection**: Ensure DATABASE_URL is set correctly
3. **OCR issues**: Tesseract is included in nixpacks.toml
4. **File permissions**: Use the start.sh script for proper setup

## Health Check
The app includes a health check endpoint at `/health` that Railway uses to verify deployment success.

## Alternative: Docker Deployment
If nixpacks continues to fail, you can use the included Dockerfile:
1. In Railway dashboard, go to Settings
2. Change "Builder" from "Nixpacks" to "Dockerfile"
3. Redeploy

## Support
- Railway docs: https://docs.railway.app
- FastAPI docs: https://fastapi.tiangolo.com
- Check Railway community Discord for help