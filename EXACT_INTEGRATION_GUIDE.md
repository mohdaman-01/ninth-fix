# 🔗 Exact Integration Guide

## Your URLs:
- **Frontend**: https://nova-s-25029.netlify.app
- **Backend**: https://web-production-935e9.up.railway.app

## ✅ Backend Status: Running (Dependencies missing - we'll fix this)

## 🚀 Step-by-Step Integration

### Step 1: Update Your Frontend Code

In your frontend repository, find and update these files:

#### **Main JavaScript File (likely script.js, main.js, or app.js):**

**Replace any localhost URLs with:**
```javascript
// OLD (remove these):
const API_URL = 'http://localhost:8000';
const BASE_URL = 'localhost:8000';
const BACKEND_URL = 'http://127.0.0.1:8000';

// NEW (use this):
const API_BASE_URL = 'https://web-production-935e9.up.railway.app';
```

#### **Specific API Functions:**

```javascript
// Certificate Upload
async function uploadCertificate(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`https://web-production-935e9.up.railway.app/api/v1/upload/certificate`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        console.log('Upload successful:', result);
        return result;
    } catch (error) {
        console.error('Upload failed:', error);
        throw error;
    }
}

// Certificate Verification
async function verifyCertificate(certificateId) {
    try {
        const response = await fetch(`https://web-production-935e9.up.railway.app/api/v1/verify/certificate/${certificateId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        console.log('Verification result:', result);
        return result;
    } catch (error) {
        console.error('Verification failed:', error);
        throw error;
    }
}

// OCR Text Extraction
async function extractText(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`https://web-production-935e9.up.railway.app/api/v1/ocr/extract-text`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        console.log('OCR result:', result);
        return result;
    } catch (error) {
        console.error('OCR failed:', error);
        throw error;
    }
}

// Google Authentication
function loginWithGoogle() {
    window.location.href = 'https://web-production-935e9.up.railway.app/api/v1/auth/google';
}

// Test Backend Connection
async function testBackendConnection() {
    try {
        const response = await fetch('https://web-production-935e9.up.railway.app/health');
        const data = await response.json();
        console.log('Backend Status:', data);
        
        // Show status to user
        const statusElement = document.getElementById('backend-status');
        if (statusElement) {
            statusElement.textContent = `Backend: ${data.status}`;
            statusElement.className = data.status === 'healthy' ? 'status-good' : 'status-warning';
        }
        
        return data;
    } catch (error) {
        console.error('Backend connection failed:', error);
        
        const statusElement = document.getElementById('backend-status');
        if (statusElement) {
            statusElement.textContent = 'Backend: Offline';
            statusElement.className = 'status-error';
        }
        
        return null;
    }
}

// Call this when page loads
document.addEventListener('DOMContentLoaded', function() {
    testBackendConnection();
});
```

### Step 2: Add Status Indicator to Your HTML

Add this to your HTML to show backend connection status:

```html
<!-- Add this somewhere in your HTML -->
<div id="backend-status" class="status-indicator">Checking backend...</div>

<!-- Add these styles -->
<style>
.status-indicator {
    padding: 5px 10px;
    border-radius: 3px;
    font-size: 12px;
    margin: 10px 0;
}

.status-good {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.status-warning {
    background-color: #fff3cd;
    color: #856404;
    border: 1px solid #ffeaa7;
}

.status-error {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}
</style>
```

### Step 3: Fix Backend Dependencies

Your backend is missing some dependencies. Let's update it:

```javascript
// Test this in your browser console on nova-s-25029.netlify.app:
fetch('https://web-production-935e9.up.railway.app/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error);
```

### Step 4: Update Backend Requirements (I'll do this)

I need to update your backend to include all dependencies. The current error "Dependencies missing" means we need to switch from requirements-core.txt to requirements.txt.

### Step 5: Test the Integration

After updating your frontend code:

1. **Deploy to Netlify** (push your changes)
2. **Test basic connection**:
   ```javascript
   // Run this in browser console on your Netlify site:
   fetch('https://web-production-935e9.up.railway.app/health')
     .then(r => r.json())
     .then(data => console.log('Backend response:', data));
   ```

3. **Test file upload**:
   - Try uploading a certificate image
   - Check browser console for any errors
   - Look for successful API responses

## 🔧 Quick Test Script

Add this to your frontend for testing:

```html
<!-- Add this button to test the connection -->
<button onclick="runConnectionTest()">Test Backend Connection</button>

<script>
async function runConnectionTest() {
    console.log('Testing backend connection...');
    
    // Test 1: Health check
    try {
        const health = await fetch('https://web-production-935e9.up.railway.app/health');
        const healthData = await health.json();
        console.log('✅ Health check:', healthData);
    } catch (error) {
        console.error('❌ Health check failed:', error);
    }
    
    // Test 2: API docs
    try {
        const docs = await fetch('https://web-production-935e9.up.railway.app/docs');
        console.log('✅ API docs accessible:', docs.status === 200);
    } catch (error) {
        console.error('❌ API docs failed:', error);
    }
    
    // Test 3: CORS
    try {
        const cors = await fetch('https://web-production-935e9.up.railway.app/', {
            method: 'GET',
            headers: {
                'Origin': 'https://nova-s-25029.netlify.app'
            }
        });
        console.log('✅ CORS test:', cors.status);
    } catch (error) {
        console.error('❌ CORS test failed:', error);
    }
}
</script>
```

## 📋 Files You Need to Update

Look for these files in your frontend project and update the API URLs:

1. **script.js** or **main.js** - Main JavaScript file
2. **config.js** - Configuration file (if exists)
3. **api.js** - API service file (if exists)
4. **Any HTML files** with inline JavaScript
5. **.env** files (if using environment variables)

## 🚨 Current Backend Issue

Your backend shows "Dependencies missing" - this means it's running the minimal version. Let me fix this by updating the backend to use full requirements.

## 📞 Next Steps

1. **I'll fix your backend dependencies** (switching to full requirements.txt)
2. **You update your frontend** with the API URLs above
3. **Deploy your updated frontend** to Netlify
4. **Test the full integration**

Would you like me to:
1. Fix the backend dependencies first?
2. Or do you want to share your frontend JavaScript files so I can give you the exact updated code?

Your integration is almost ready - just need to connect the dots! 🚀