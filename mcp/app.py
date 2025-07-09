from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import sys
import logging

# Add the project root to the Python path to allow importing from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# We can import our own tools for "dogfooding" security.
# For example, using SemanticFirewall to validate certain inputs to the MCP.
from src.semantic_firewall import SemanticFirewall 

logger = logging.getLogger(__name__)

app = FastAPI(
    title="MCP (Master Control Program) API",
    description="A centralized command and control server for managing and monitoring the RADAR system.",
    version="0.1.0"
)

# --- Security: API Key ---
API_KEY = os.getenv("MCP_API_KEY")
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key_from_header: str = Depends(api_key_header)):
    if not API_KEY:
        logger.critical("MCP_API_KEY environment variable not set. The server is misconfigured and insecure.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is not configured for security. Cannot process request."
        )
    if api_key_from_header != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )
    return api_key_from_header
# --- End Security ---


@app.get("/")
async def read_root():
    return {"message": "Welcome to the MCP API. Secure endpoints require authentication."}

@app.get("/status", dependencies=[Depends(get_api_key)])
async def get_system_status():
    """
    Get the health and status of all managed components.
    (Placeholder implementation)
    """
    # In a real implementation, this would query various services.
    return {
        "status": "ok",
        "components": {
            "semantic_firewall_api": "healthy",
            "demo_ui": "healthy",
            "llm_service": "not_monitored"
        }
    }

# To run this app from the project root:
# MCP_API_KEY=your-secret-key uvicorn mcp.app:app --reload --port 8001
