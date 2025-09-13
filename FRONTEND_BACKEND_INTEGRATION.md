# 🔗 Frontend-Backend Integration Guide

## Your Setup:
- **Frontend**: https://github.com/mohdaman-01/sih_project (Netlify: https://nova-s-25029.netlify.app)
- **Backend**: Railway (FastAPI Certificate Verification System)

## 🚀 Integration Steps

### Step 1: Get Your Railway Backend URL

1. Go to Railway Dashboard → Your Service → Settings → Domains
2. Copy your backend URL (example: `https://cert-verify-api-production.railway.app`)

### Step 2: Update Frontend API Configuration

Based on common frontend patterns, look for these files in your project:

#### **Option A: If you have a config.js or constants.js file:**
```javascript
// Before (localhost)
const API_BASE_URL = 'http://localhost:8000';

// After (Railway)
const API_BASE_URL = 'https://your-railway-app.railway.app';
```

#### **Option B: If API calls are in individual files:**
Find and replace all instances of:
```javascript
// Replace this:
fetch('http://localhost:8000/api/...')

// With this:
fetch('https://your-railway-app.railway.app/api/...')
```

#### **Option C: If using environment variables:**
Create or update `.env` file:
```env
REACT_APP_API_URL=https://your-railway-app.railway.app
VITE_API_URL=https://your-railway-app.railway.app
```

### Step 3: Common Files to Update

Look for these files in your frontend project:

1. **Main JavaScript files** (`script.js`, `main.js`, `app.js`)
2. **API service files** (`api.js`, `services.js`)
3. **Configuration files** (`config.js`, `constants.js`)
4. **Environment files** (`.env`, `.env.production`)

### Step 4: Update API Endpoints

Your Railway backend provides these endpoints:

```javascript
// Certificate Upload
const uploadCertificate = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_BASE_URL}/api/v1/upload/certificate`, {
    method: 'POST',
    body: formData
  });
  
  return response.json();
};

// Certificate Verification
const verifyCertificate = async (certId) => {
  const response = await fetch(`${API_BASE_URL}/api/v1/verify/certificate/${certId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  });
  
  return response.json();
};

// OCR Text Extraction
const extractText = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_BASE_URL}/api/v1/ocr/extract-text`, {
    method: 'POST',
    body: formData
  });
  
  return response.json();
};

// Google Authentication
const googleLogin = () => {
  window.location.href = `${API_BASE_URL}/api/v1/auth/google`;
};

// Health Check
const checkBackendHealth = async () => {
  const response = await fetch(`${API_BASE_URL}/health`);
  return response.json();
};
```

### Step 5: Handle CORS (Already Configured)

Your backend is already configured to accept requests from:
- `https://nova-s-25029.netlify.app` ✅
- `http://localhost:3000` (for development) ✅

### Step 6: Test the Integration

Add this test function to your frontend:

```javascript
// Test backend connection
async function testBackendConnection() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    const data = await response.json();
    console.log('Backend Status:', data);
    
    if (data.status === 'healthy') {
      console.log('✅ Backend connected successfully!');
      return true;
    }
  } catch (error) {
    console.error('❌ Backend connection failed:', error);
    return false;
  }
}

// Call this when your page loads
testBackendConnection();
```

## 📋 Specific Integration Based on Your Project

### If Your Project Uses:

#### **Vanilla JavaScript/HTML:**
```html
<script>
const API_BASE_URL = 'https://your-railway-app.railway.app';

// Your existing upload function
async function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/upload/certificate`, {
      method: 'POST',
      body: formData
    });
    
    const result = await response.json();
    console.log('Upload result:', result);
  } catch (error) {
    console.error('Upload failed:', error);
  }
}
</script>
```

#### **React:**
```jsx
// config.js
export const API_BASE_URL = 'https://your-railway-app.railway.app';

// api.js
import { API_BASE_URL } from './config';

export const uploadCertificate = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_BASE_URL}/api/v1/upload/certificate`, {
    method: 'POST',
    body: formData
  });
  
  return response.json();
};
```

#### **Vue.js:**
```javascript
// main.js or config.js
const API_BASE_URL = 'https://your-railway-app.railway.app';

// In your component
methods: {
  async uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/upload/certificate`, {
        method: 'POST',
        body: formData
      });
      
      const result = await response.json();
      this.handleUploadResult(result);
    } catch (error) {
      console.error('Upload failed:', error);
    }
  }
}
```

## 🔧 Quick Integration Checklist

- [ ] Get Railway backend URL
- [ ] Find API configuration in frontend code
- [ ] Replace localhost URLs with Railway URL
- [ ] Test `/health` endpoint
- [ ] Test file upload functionality
- [ ] Test certificate verification
- [ ] Deploy updated frontend to Netlify
- [ ] Test end-to-end flow

## 🚨 Troubleshooting

### Common Issues:

1. **CORS Errors**
   - Your backend already allows `nova-s-25029.netlify.app`
   - If you get CORS errors, check the exact domain

2. **404 Errors**
   - Verify Railway URL is correct
   - Check if backend is running at `/health`

3. **File Upload Issues**
   - Don't set `Content-Type` header for FormData
   - Use `body: formData` not `body: JSON.stringify(formData)`

## 📞 Next Steps

1. **Share your main JavaScript files** (I can help update them specifically)
2. **Get your Railway URL** and replace the API base URL
3. **Test the connection** using browser console
4. **Deploy to Netlify** with updated configuration

Would you like me to help you update specific files from your repository? Just share the content of your main JavaScript/API files and I'll provide the exact updated code! 🚀