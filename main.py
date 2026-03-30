"""
ABUSE DETECTION API - BACKEND
==============================
Fast, context-aware abuse detection API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List
import torch
from transformers import RobertaTokenizerFast, RobertaForSequenceClassification
import re
from datetime import datetime
import os

# ============================================================================
# LOAD MODEL
# ============================================================================

print("Loading model from Hugging Face...")

MODEL_REPO = "Vihnn-e/emotional-abuse-detector"

tokenizer = RobertaTokenizerFast.from_pretrained(MODEL_REPO)
model = RobertaForSequenceClassification.from_pretrained(MODEL_REPO)
model.eval()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

print(f"Model loaded successfully on {device}")

# ============================================================================
# CREATE API
# ============================================================================

app = FastAPI(
    title="Abuse Detection API",
    description="AI-powered abuse detection with context awareness",
    version="1.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class TextRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)
    threshold: float = Field(0.70, ge=0.0, le=1.0)

class BatchRequest(BaseModel):
    texts: List[str] = Field(..., max_items=100)
    threshold: float = Field(0.70, ge=0.0, le=1.0)

class PredictionResponse(BaseModel):
    text: str
    label: str
    confidence: float
    is_abusive: bool
    probability_abusive: float
    probability_non_abusive: float
    threshold_used: float
    context_flags: dict
    timestamp: str

class BatchResponse(BaseModel):
    results: List[PredictionResponse]
    total: int
    abusive_count: int
    non_abusive_count: int

# ============================================================================
# PREDICTION LOGIC
# ============================================================================

def detect_context(text: str) -> dict:
    """Detect context patterns to avoid false positives"""
    text_lower = text.lower()

    # Positive context words
    positive_words = r'\b(love|like|cute|amazing|beautiful|awesome|great|wonderful|fantastic|adore|cherish|thank|thanks|appreciate|happy|joy|friend|buddy|bro|sis)\b'

    # Direct attack patterns
    attack_patterns = [
        r'\bfuck\s+you\b',
        r'\byou\s+(are|re)\s+(stupid|dumb|idiot|moron|worthless|pathetic|ugly|disgusting)',
        r'\bgo\s+(and\s+)?die\b',
        r'\bkill\s+yourself\b',
        r'\byou\s+suck\b',
        r'\bshut\s+(up|the\s+fuck\s+up)\b',
        r'\bi\s+hate\s+you\b'
    ]

    # Emotional emphasis (profanity as intensifier, not attack)
    emphasis_patterns = r'\b(fucking|damn|shit)\s+(good|great|cool|nice|amazing|awesome|cute|beautiful|fantastic)\b'

    has_positive = bool(re.search(positive_words, text_lower))
    has_attack = any(re.search(pattern, text_lower) for pattern in attack_patterns)
    has_emphasis = bool(re.search(emphasis_patterns, text_lower))
    has_profanity = bool(re.search(r'\b(fuck|shit|bitch|damn|ass)\b', text_lower))

    return {
        "has_positive_context": has_positive,
        "has_attack_pattern": has_attack,
        "has_emotional_emphasis": has_emphasis,
        "has_profanity": has_profanity
    }


def predict_abuse(text: str, threshold: float = 0.70) -> dict:
    """
    Predict if text is abusive with context awareness.
    Context rules adjust the threshold to reduce false positives.
    """

    # Tokenize and move inputs to same device as model
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)

    prob_non_abusive = probs[0][0].item()
    prob_abusive = probs[0][1].item()

    # Detect context
    context = detect_context(text)

    # Adjust threshold based on context
    adjusted_threshold = threshold

    # Rule 1: Positive context raises threshold (harder to flag as abusive)
    if context["has_positive_context"] and not context["has_attack_pattern"]:
        adjusted_threshold += 0.15

    # Rule 2: Emotional emphasis (not attack) raises threshold
    if context["has_emotional_emphasis"]:
        adjusted_threshold += 0.20

    # Rule 3: Direct attack lowers threshold (easier to flag)
    if context["has_attack_pattern"]:
        adjusted_threshold -= 0.05

    # Make final decision
    is_abusive = prob_abusive >= adjusted_threshold

    return {
        "text": text,
        "label": "ABUSIVE" if is_abusive else "NON-ABUSIVE",
        "confidence": round(prob_abusive if is_abusive else prob_non_abusive, 4),
        "is_abusive": is_abusive,
        "probability_abusive": round(prob_abusive, 4),
        "probability_non_abusive": round(prob_non_abusive, 4),
        "threshold_used": round(adjusted_threshold, 4),
        "context_flags": context,
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
def home():
    """API info"""
    return {
        "name": "Abuse Detection API",
        "status": "running",
        "model": MODEL_REPO,
        "device": str(device),
        "endpoints": {
            "predict": "POST /api/predict",
            "batch": "POST /api/batch",
            "health": "GET /api/health"
        }
    }


@app.get("/api/health")
def health():
    """Health check"""
    return {
        "status": "healthy",
        "model_loaded": True,
        "model_repo": MODEL_REPO,
        "device": str(device)
    }


@app.post("/api/predict", response_model=PredictionResponse)
def predict_endpoint(request: TextRequest):
    """
    Analyze single text for abuse.

    Example:
    {
        "text": "you are fucking cute",
        "threshold": 0.70
    }
    """
    try:
        result = predict_abuse(request.text, request.threshold)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/batch", response_model=BatchResponse)
def batch_predict(request: BatchRequest):
    """
    Analyze multiple texts at once.

    Example:
    {
        "texts": ["fuck you", "you are cute", "I love you"],
        "threshold": 0.70
    }
    """
    try:
        results = []
        for text in request.texts:
            result = predict_abuse(text, request.threshold)
            results.append(result)

        abusive_count = sum(1 for r in results if r["is_abusive"])

        return {
            "results": results,
            "total": len(results),
            "abusive_count": abusive_count,
            "non_abusive_count": len(results) - abusive_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SERVE FRONTEND
# ============================================================================

@app.get("/app")
def serve_frontend():
    """Serve the frontend HTML"""
    if os.path.exists("frontend.html"):
        return FileResponse("frontend.html")
    else:
        return {"message": "Frontend not found. Make sure frontend.html is in the same folder."}


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 70)
    print("ABUSE DETECTION API - STARTING")
    print("=" * 70)
    print(f"API:      http://localhost:8000")
    print(f"Docs:     http://localhost:8000/docs")
    print(f"Frontend: http://localhost:8000/app")
    print(f"Model:    {MODEL_REPO}")
    print(f"Device:   {device}")
    print("=" * 70 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")