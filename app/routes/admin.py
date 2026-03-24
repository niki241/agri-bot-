from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Farmer, QueryLog, Conversation
from app.services.farmer_service import get_all_farmers, get_farmer_by_phone, get_farmer_queries
from app.services.whatsapp import send_text_message

router = APIRouter(prefix="/api", tags=["admin"])


# --- Farmer endpoints ---

class FarmerOut(BaseModel):
    id: int
    phone: str
    name: str | None
    language: str
    district: str | None
    state: str | None
    crops: list[str] | None
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/farmers", response_model=list[FarmerOut])
async def list_farmers(
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List all registered farmers."""
    farmers = await get_all_farmers(db, limit, offset)
    return farmers


@router.get("/farmers/{phone}", response_model=FarmerOut)
async def get_farmer(phone: str, db: AsyncSession = Depends(get_db)):
    """Get a farmer's profile by phone number."""
    farmer = await get_farmer_by_phone(db, phone)
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    return farmer


class QueryLogOut(BaseModel):
    id: int
    query_text: str
    language_detected: str
    intent: str | None
    ai_response: str | None
    response_time_ms: float | None
    feedback: str | None
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/farmers/{phone}/queries", response_model=list[QueryLogOut])
async def get_farmer_query_history(
    phone: str,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Get a farmer's query history."""
    farmer = await get_farmer_by_phone(db, phone)
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    queries = await get_farmer_queries(db, farmer.id, limit)
    return queries


# --- Analytics ---

class DashboardStats(BaseModel):
    total_farmers: int
    total_queries: int
    queries_today: int
    avg_response_time_ms: float
    language_split: dict[str, int]
    intent_split: dict[str, int]
    top_crops: list[dict]
    recent_queries: list[dict]


@router.get("/analytics/dashboard", response_model=DashboardStats)
async def dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Aggregated stats for the admin dashboard."""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # Total farmers
    result = await db.execute(select(func.count(Farmer.id)))
    total_farmers = result.scalar() or 0

    # Total queries
    result = await db.execute(select(func.count(QueryLog.id)))
    total_queries = result.scalar() or 0

    # Queries today
    result = await db.execute(
        select(func.count(QueryLog.id)).where(QueryLog.created_at >= today)
    )
    queries_today = result.scalar() or 0

    # Avg response time
    result = await db.execute(select(func.avg(QueryLog.response_time_ms)))
    avg_response_time = result.scalar() or 0.0

    # Language split
    result = await db.execute(
        select(QueryLog.language_detected, func.count(QueryLog.id))
        .group_by(QueryLog.language_detected)
    )
    language_split = {row[0]: row[1] for row in result.all()}

    # Intent split
    result = await db.execute(
        select(QueryLog.intent, func.count(QueryLog.id))
        .where(QueryLog.intent.isnot(None))
        .group_by(QueryLog.intent)
    )
    intent_split = {row[0]: row[1] for row in result.all()}

    # Top crops from farmers
    result = await db.execute(
        select(func.unnest(Farmer.crops).label("crop"), func.count().label("cnt"))
        .where(Farmer.crops.isnot(None))
        .group_by(text("crop"))
        .order_by(text("cnt DESC"))
        .limit(10)
    )
    top_crops = [{"crop": row[0], "count": row[1]} for row in result.all()]

    # Recent queries
    result = await db.execute(
        select(QueryLog)
        .order_by(QueryLog.created_at.desc())
        .limit(20)
    )
    recent = result.scalars().all()
    recent_queries = [
        {
            "id": q.id,
            "farmer_id": q.farmer_id,
            "query": q.query_text[:100],
            "language": q.language_detected,
            "intent": q.intent,
            "response_time_ms": q.response_time_ms,
            "created_at": q.created_at.isoformat() if q.created_at else None,
        }
        for q in recent
    ]

    return DashboardStats(
        total_farmers=total_farmers,
        total_queries=total_queries,
        queries_today=queries_today,
        avg_response_time_ms=round(avg_response_time, 2),
        language_split=language_split,
        intent_split=intent_split,
        top_crops=top_crops,
        recent_queries=recent_queries,
    )


# --- Broadcast ---

class BroadcastRequest(BaseModel):
    message: str
    language: str | None = None  # None = send to all
    state: str | None = None
    crop: str | None = None


class BroadcastResponse(BaseModel):
    sent: int
    failed: int


@router.post("/broadcast", response_model=BroadcastResponse)
async def broadcast_message(
    request: BroadcastRequest,
    db: AsyncSession = Depends(get_db),
):
    """Send a broadcast message to a segment of farmers."""
    stmt = select(Farmer)

    if request.language:
        stmt = stmt.where(Farmer.language == request.language)
    if request.state:
        stmt = stmt.where(Farmer.state == request.state)
    if request.crop:
        stmt = stmt.where(Farmer.crops.contains([request.crop]))

    result = await db.execute(stmt)
    farmers = result.scalars().all()

    sent = 0
    failed = 0
    for farmer in farmers:
        success = await send_text_message(farmer.phone, request.message)
        if success:
            sent += 1
        else:
            failed += 1

    return BroadcastResponse(sent=sent, failed=failed)
