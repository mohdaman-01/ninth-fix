"""
Simple Railway entry point - moves to backend and starts the app
"""
import os
import sys

# Add backend to path and change directory
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)
os.chdir(backend_path)

# Import and run the FastAPI app
from app.main import app
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)