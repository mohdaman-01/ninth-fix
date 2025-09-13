# 🚀 Heroku Deployment Guide

## Prerequisites
- Heroku CLI installed
- Git repository pushed to GitHub
- Heroku account

## Quick Deployment

### 1. Create Heroku App
```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:mini

# Add Redis addon (optional)
heroku addons:create heroku-redis:mini
```

### 2. Set Environment Variables
```bash
# Required
heroku config:set SECRET_KEY="your-secret-key-here"
heroku config:set DATABASE_URL="$(heroku config:get DATABASE_URL)"

# Optional
heroku config:set GOOGLE_CLIENT_ID="your-google-client-id"
heroku config:set GOOGLE_CLIENT_SECRET="your-google-client-secret"
heroku config:set DEBUG="False"
heroku config:set ALLOWED_ORIGINS="https://nova-s-25029.netlify.app,http://localhost:3000"
```

### 3. Deploy
```bash
# Add Heroku remote
heroku git:remote -a your-app-name

# Deploy
git push heroku main

# Run database migrations
heroku run python init_db.py
```

### 4. Open App
```bash
heroku open
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | JWT secret key |
| `DATABASE_URL` | Yes | PostgreSQL URL (auto-set by Heroku) |
| `GOOGLE_CLIENT_ID` | No | Google OAuth Client ID |
| `GOOGLE_CLIENT_SECRET` | No | Google OAuth Client Secret |
| `DEBUG` | No | Debug mode (default: False) |
| `ALLOWED_ORIGINS` | No | CORS allowed origins |

## Troubleshooting

### Common Issues

1. **Build Fails**: Check buildpacks order
2. **Database Connection**: Ensure DATABASE_URL is set
3. **OCR Not Working**: Check Tesseract installation
4. **CORS Issues**: Update ALLOWED_ORIGINS

### Logs
```bash
# View logs
heroku logs --tail

# View specific logs
heroku logs --tail --source app
```

### Database
```bash
# Access database
heroku pg:psql

# Reset database
heroku pg:reset DATABASE_URL
```

## Production Checklist

- [ ] Environment variables set
- [ ] Database initialized
- [ ] CORS configured
- [ ] Google OAuth configured (if using)
- [ ] File upload limits set
- [ ] Monitoring enabled
- [ ] SSL certificate active

## Scaling

```bash
# Scale web dynos
heroku ps:scale web=2

# Scale worker dynos (if using Celery)
heroku ps:scale worker=1
```

## Monitoring

- **Heroku Dashboard**: Monitor app performance
- **Logs**: `heroku logs --tail`
- **Metrics**: `heroku metrics`

## Support

For deployment issues, check:
1. Heroku logs
2. Build logs
3. Environment variables
4. Database connectivity
