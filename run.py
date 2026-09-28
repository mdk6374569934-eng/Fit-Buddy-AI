import sys
import os

# Set UTF-8 encoding for standard output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure current folder and backend are in Python search path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
backend_dir = os.path.join(current_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    print("================================================================")
    print("FitBuddy - AI Fitness Plan Generator")
    print(f"Running locally at: http://{host}:{port}")
    print(f"Swagger API Docs:   http://{host}:{port}/docs")
    print(f"Admin Dashboard:    http://{host}:{port}/view-all-users")
    print("================================================================")
    uvicorn.run("app.main:app", host=host, port=port, reload=False)
