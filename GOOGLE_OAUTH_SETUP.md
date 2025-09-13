# Google OAuth Setup Guide

## 🔑 Environment Variables Needed

You need these 3 variables for Railway:

1. **SECRET_KEY** - Generated above ✅
2. **GOOGLE_CLIENT_ID** - From Google Cloud Console
3. **GOOGLE_CLIENT_SECRET** - From Google Cloud Console

## 🚀 Step-by-Step Google OAuth Setup

### Step 1: Go to Google Cloud Console
1. Visit: https://console.cloud.google.com/
2. Sign in with your Google account

### Step 2: Create or Select a Project
1. Click the project dropdown (top left)
2. Click "New Project" or select existing project
3. Give it a name like "Certificate Verification System"
4. Click "Create"

### Step 3: Enable Google+ API
1. Go to "APIs & Services" → "Library"
2. Search for "Google+ API"
3. Click on it and press "Enable"
4. Also enable "Google Identity" if available

### Step 4: Create OAuth Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client IDs"
3. If prompted, configure OAuth consent screen first:
   - Choose "External" user type
   - Fill in app name: "Certificate Verification System"
   - Add your email as developer contact
   - Save and continue through the steps

### Step 5: Configure OAuth Client
1. Application type: **Web application**
2. Name: "Certificate Verification Web Client"
3. **Authorized JavaScript origins:**
   ```
   https://your-railway-app-name.railway.app
   http://localhost:8000
   ```
4. **Authorized redirect URIs:**
   ```
   https://your-railway-app-name.railway.app/api/v1/auth/google/callback
   http://localhost:8000/api/v1/auth/google/callback
   ```
5. Click "Create"

### Step 6: Copy Credentials
1. A popup will show your credentials
2. **Copy the Client ID** - this is your `GOOGLE_CLIENT_ID`
3. **Copy the Client Secret** - this is your `GOOGLE_CLIENT_SECRET`
4. Click "OK"

## 📝 Railway Environment Variables

Add these in Railway Dashboard → Variables:

```
SECRET_KEY=Ny5FR2AS2eCX07AvEsd7UfWKgdzD-xWYGdVfAOaolaI
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwxyz
```

## 🔧 Update Redirect URIs Later

After Railway deployment:
1. Get your Railway app URL (e.g., `https://cert-verify-api-production.railway.app`)
2. Go back to Google Cloud Console → Credentials
3. Edit your OAuth client
4. Update the redirect URIs with your actual Railway URL:
   ```
   https://your-actual-railway-url.railway.app/api/v1/auth/google/callback
   ```

## ✅ Test OAuth Setup

After deployment, test the OAuth flow:
1. Visit: `https://your-app.railway.app/docs`
2. Try the Google authentication endpoints
3. Check if login redirects work properly

## 🚨 Security Notes

- Keep CLIENT_SECRET private
- Never commit these to git
- Use different credentials for development/production
- Regularly rotate your SECRET_KEY

## 📞 Support

If you get stuck:
- Google Cloud Console Help: https://cloud.google.com/support
- OAuth 2.0 Documentation: https://developers.google.com/identity/protocols/oauth2