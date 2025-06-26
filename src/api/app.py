from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sys
import os

# Add the project root to the Python path to allow importing from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.detectors.rule_based import EchoChamberDetector

app = FastAPI(
    title="RADAR API",
    description="API for detecting advanced AI deception, focusing on in-context scheming and multi-turn manipulative attacks.",
    version="0.1.0"
)

# Initialize the detector
detector = EchoChamberDetector()

class AnalysisRequest(BaseModel):
    text_input: str
    conversation_history: Optional[List[str]] = None

class AnalysisResponse(BaseModel):
    classification: str
    echo_chamber_score: int
    echo_chamber_probability: float
    detected_indicators: List[str]
    llm_analysis: Optional[str] = None # Analysis from the local LLM
    llm_status: Optional[str] = None # Status of the LLM analysis (e.g., success, model_not_loaded, analysis_error)
    # For any other potential fields in the future
    additional_info: Optional[Dict[str, Any]] = None


@app.post("/analyze/", response_model=AnalysisResponse)
async def analyze_text_endpoint(request: AnalysisRequest):
    """
    Analyzes a given text input for signs of deceptive reasoning or echo chamber characteristics.
    Optionally, a conversation history can be provided for more context.
    """
    analysis_result = detector.analyze_text(
        text_input=request.text_input,
        conversation_history=request.conversation_history
    )
    return AnalysisResponse(**analysis_result)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the RADAR API. Use the /analyze endpoint to submit text for analysis."}

# To run the app (from the project root directory):
# uvicorn src.api.app:app --reload
