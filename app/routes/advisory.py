from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.language import detect_language
from app.services.intent import classify_intent
from app.services.ollama_client import get_advisory
from app.services.knowledge_base import search_advisories, format_kb_context

router = APIRouter(prefix="/api/advisory", tags=["advisory"])


class AdvisoryRequest(BaseModel):
    query: str
    language: Optional[str] = None
    district: str = "Unknown"
    state: str = "Unknown"
    crops: Optional[List[str]] = None


class AdvisoryResponse(BaseModel):
    query: str
    language_detected: str
    intent: str
    response: str
    kb_matches: int


@router.post("/query", response_model=AdvisoryResponse)
async def query_advisory(
    request: AdvisoryRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Process a crop advisory query (internal/testing endpoint).
    Can be used directly without WhatsApp for testing the advisory pipeline.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Detect language if not provided
    language = request.language or detect_language(request.query)

    # Classify intent
    intent = classify_intent(request.query, language)

    # Search KB
    advisories = await search_advisories(db, request.query, language)
    kb_context = format_kb_context(advisories)

    # Get AI response
    response = await get_advisory(
        query=request.query,
        language=language,
        district=request.district,
        state=request.state,
        crops=request.crops,
        kb_context=kb_context,
    )

    return AdvisoryResponse(
        query=request.query,
        language_detected=language,
        intent=intent,
        response=response,
        kb_matches=len(advisories),
    )
