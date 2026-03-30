"""
ABUSE DETECTION API - BACKEND
==============================
Lightweight backend using Hugging Face Inference API
Image size: ~200MB (no torch, no transformers)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
import requests
import re
from datetime import datetime
import os

# ============================================================================
# HUGGING FACE CONFIG
# ============================================================================

HF_TOKEN    = os.environ.get("HF_TOKEN", "")
MODEL_REPO  = "Vihnn-e/emotional-abuse-detector"
HF_API_URL  = f"https://api-inference.huggingface.co/models/{MODEL_REPO}"

HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

# ============================================================================
# CREATE API
# ============================================================================

app = FastAPI(
    title="Abuse Detection API",
    description="AI-powered abuse detection via Hugging Face Inference API",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# REQUEST / RESPONSE MODELS
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
# CONTEXT DETECTION (runs locally — no model needed)
# ============================================================================

def detect_context(text: str) -> dict:
    text_lower = text.lower()

    positive_words   = r'\b(love|like|cute|amazing|beautiful|awesome|great|wonderful|fantastic|adore|cherish|thank|thanks|appreciate|happy|joy|friend|buddy|bro|sis)\b'
    emphasis_pattern = r'\b(fucking|damn|shit)\s+(good|great|cool|nice|amazing|awesome|cute|beautiful|fantastic)\b'
    attack_patterns  = [
        r'\bfuck\s+you\b',
        r'\byou\s+(are|re)\s+(stupid|dumb|idiot|moron|worthless|pathetic|ugly|disgusting)',
        r'\bgo\s+(and\s+)?die\b',
        r'\bkill\s+yourself\b',
        r'\byou\s+suck\b',
        r'\bshut\s+(up|the\s+fuck\s+up)\b',
        r'\bi\s+hate\s+you\b'
    ]

    return {
        "has_positive_context":   bool(re.search(positive_words, text_lower)),
        "has_attack_pattern":     any(re.search(p, text_lower) for p in attack_patterns),
        "has_emotional_emphasis": bool(re.search(emphasis_pattern, text_lower)),
        "has_profanity":          bool(re.search(r'\b(fuck|shit|bitch|damn|ass)\b', text_lower)),
    }

# ============================================================================
# PREDICTION LOGIC
# ============================================================================

def predict_abuse(text: str, threshold: float = 0.70) -> dict:

    # Call Hugging Face Inference API
    hf_response = requests.post(
        HF_API_URL,
        headers=HEADERS,
        json={"inputs": text},
        timeout=30
    )

    if hf_response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Hugging Face API error: {hf_response.status_code} — {hf_response.text}"
        )

    # Parse response
    # HF returns: [[{"label": "LABEL_0", "score": 0.x}, {"label": "LABEL_1", "score": 0.x}]]
    raw = hf_response.json()
    scores = raw[0] if isinstance(raw[0], list) else raw

    prob_non_abusive = 0.0
    prob_abusive     = 0.0

    for item in scores:
        lbl = item["label"].upper()
        if lbl in ("LABEL_0", "NON-ABUSIVE", "NOT_ABUSIVE", "0"):
            prob_non_abusive = item["score"]
        elif lbl in ("LABEL_1", "ABUSIVE", "1"):
            prob_abusive = item["score"]

    # Context-aware threshold adjustment
    context = detect_context(text)
    adjusted_threshold = threshold

    if context["has_positive_context"] and not context["has_attack_pattern"]:
        adjusted_threshold += 0.15
    if context["has_emotional_emphasis"]:
        adjusted_threshold += 0.20
    if context["has_attack_pattern"]:
        adjusted_threshold -= 0.05

    is_abusive = prob_abusive >= adjusted_threshold

    return {
        "text":                  text,
        "label":                 "ABUSIVE" if is_abusive else "NON-ABUSIVE",
        "confidence":            round(prob_abusive if is_abusive else prob_non_abusive, 4),
        "is_abusive":            is_abusive,
        "probability_abusive":   round(prob_abusive, 4),
        "probability_non_abusive": round(prob_non_abusive, 4),
        "threshold_used":        round(adjusted_threshold, 4),
        "context_flags":         context,
        "timestamp":             datetime.now().isoformat()
    }

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
def home():
    return {
        "name":    "Abuse Detection API",
        "status":  "running",
        "model":   MODEL_REPO,
        "version": "2.0 — Hugging Face Inference API",
        "endpoints": {
            "predict": "POST /api/predict",
            "batch":   "POST /api/batch",
            "health":  "GET  /api/health"
        }
    }

@app.get("/api/health")
def health():
    return {
        "status":      "healthy",
        "model":       MODEL_REPO,
        "backend":     "Hugging Face Inference API",
        "hf_token_set": bool(HF_TOKEN)
    }

@app.post("/api/predict", response_model=PredictionResponse)
def predict_endpoint(request: TextRequest):
    try:
        return predict_abuse(request.text, request.threshold)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/batch", response_model=BatchResponse)
def batch_predict(request: BatchRequest):
    try:
        results = [predict_abuse(t, request.threshold) for t in request.texts]
        abusive_count = sum(1 for r in results if r["is_abusive"])
        return {
            "results":          results,
            "total":            len(results),
            "abusive_count":    abusive_count,
            "non_abusive_count": len(results) - abusive_count
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")