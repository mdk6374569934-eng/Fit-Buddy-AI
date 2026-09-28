import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routes import router

# Initialize FastAPI application
app = FastAPI(
    title="FitBuddy - AI Fitness Plan Generator",
    description="AI-driven personalized 7-day workout and nutrition plan generator using Google Gemini models.",
    version="1.0.0"
)

# Enable CORS for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve static directory location flexibly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_PARENT = os.path.dirname(CURRENT_DIR)
WORKSPACE_ROOT = os.path.dirname(APP_PARENT) if os.path.basename(APP_PARENT) == "backend" else APP_PARENT

candidate_static_dirs = [
    os.path.join(WORKSPACE_ROOT, "frontend", "static"),
    os.path.join(WORKSPACE_ROOT, "static"),
    os.path.join(APP_PARENT, "static"),
]

STATIC_DIR = None
for candidate in candidate_static_dirs:
    if os.path.isdir(candidate):
        STATIC_DIR = candidate
        break

if not STATIC_DIR:
    STATIC_DIR = candidate_static_dirs[0]
    os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Include application routes
app.include_router(router)

@app.on_event("startup")
def startup_event():
    # Ensure database tables exist
    Base.metadata.create_all(bind=engine)
