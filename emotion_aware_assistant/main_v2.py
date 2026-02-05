"""Emotion-Aware Productivity Assistant - Version 2.0
Pure Python implementation (no LangGraph)

This is the new main application file using the refactored architecture.
For the old LangGraph version, see main.py"""


import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import API routes
from emotion_aware_assistant.api.chat import router as chat_router
from emotion_aware_assistant.services.google_auth import router as auth_router

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Emotion-Aware Productivity Assistant",
    description="An AI assistant that understands your emotions and helps with productivity",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "https://emotion-aware-prod-assistant.onrender.com",
        # Add your frontend URLs here
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/api/v2", tags=["Chat"])
app.include_router(auth_router, prefix="/api/v2/auth", tags=["Authentication"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Emotion-Aware Productivity Assistant API v2.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "chat": "/api/v2/chat",
            "history": "/api/v2/history",
            "health": "/api/v2/health",
            "authorize": "/api/v2/auth/authorize"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "architecture": "pure-python"
    }

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    
    print(f"""

     Server starting on http://localhost:{port}
     API Docs: http://localhost:{port}/docs
    Health: http://localhost:{port}/health
    
    Endpoints:
    - POST /api/v2/chat - Main chat endpoint
    - POST /api/v2/history - Get conversation history
    - GET  /api/v2/health - Health check
    - GET  /api/v2/auth/authorize - Google Calendar OAuth
    """)
    
    uvicorn.run(
        "emotion_aware_assistant.main_v2:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
