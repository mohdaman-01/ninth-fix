"""
Simple Railway entry point - moves to backend and starts the app
"""
import os
import sys

# Add backend to path and change directory
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)
os.chdir(backend_path)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    
    # Import app after setting up paths
    try:
        from app.main import app
        print("✅ App imported successfully")
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        print(f"❌ Failed to import app: {e}")
        # Create a minimal FastAPI app as fallback
        from fastapi import FastAPI
        fallback_app = FastAPI()
        
        @fallback_app.get("/")
        def root():
            return {"status": "error", "message": f"App failed to start: {e}"}
            
        @fallback_app.get("/health")
        def health():
            return {"status": "error", "message": "Dependencies missing"}
            
        uvicorn.run(fallback_app, host="0.0.0.0", port=port)