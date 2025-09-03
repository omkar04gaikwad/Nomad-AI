#!/usr/bin/env python3
"""
Simple test server for NomadAI backend
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="NomadAI Test Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "NomadAI Test Server is running!"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "NomadAI Test Server is running!",
        "cohere_key": "✅ Set" if os.getenv("COHERE_API_KEY") else "❌ Not set"
    }

@app.get("/api/test")
async def test_endpoint():
    return {
        "success": True,
        "message": "Test endpoint working!",
        "env_vars": {
            "COHERE_API_KEY": "✅ Set" if os.getenv("COHERE_API_KEY") else "❌ Not set"
        }
    }

if __name__ == "__main__":
    print("🚀 Starting NomadAI Test Server...")
    print(f"📋 Environment check:")
    print(f"   COHERE_API_KEY: {'✅ Set' if os.getenv('COHERE_API_KEY') else '❌ Not set'}")
    print(f"🌐 Server will be available at: http://localhost:8000")
    print(f"📚 API docs at: http://localhost:8000/docs")
    
    uvicorn.run(
        "simple_test:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

