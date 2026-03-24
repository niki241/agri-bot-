import logging
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.farmer import Farmer
from app.models.conversation import Conversation
from app.models.query_log import QueryLog

logger = logging.getLogger(__name__)


async def get_or_create_farmer(
    db: AsyncSession, phone: str, language: str = "te"
) -> tuple[Farmer, bool]:
    """
    Get existing farmer or create new one.
    Returns (farmer, is_new).
    """
    stmt = select(Farmer).where(Farmer.phone == phone)
    result = await db.execute(stmt)
    farmer = result.scalar_one_or_none()

    if farmer:
        return farmer, False

    farmer = Farmer(phone=phone, language=language)
    db.add(farmer)
    await db.commit()
    await db.refresh(farmer)
    logger.info("New farmer registered: %s", phone)
    return farmer, True


async def update_farmer_language(
    db: AsyncSession, farmer: Farmer, language: str
) -> Farmer:
    """Update farmer's preferred language based on latest message."""
    if farmer.language != language:
        farmer.language = language
        await db.commit()
        await db.refresh(farmer)
    return farmer


async def get_or_create_conversation(
    db: AsyncSession, farmer_id: int
) -> Conversation:
    """Get the active conversation or create a new one."""
    stmt = (
        select(Conversation)
        .where(Conversation.farmer_id == farmer_id)
        .order_by(Conversation.updated_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    conv = result.scalar_one_or_none()

    if conv:
        return conv

    conv = Conversation(farmer_id=farmer_id, messages_json=[])
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return conv


async def append_message(
    db: AsyncSession,
    conversation: Conversation,
    role: str,
    text: str,
) -> Conversation:
    """Append a message to conversation history."""
    messages = list(conversation.messages_json or [])
    messages.append({
        "role": role,
        "text": text,
        "timestamp": datetime.utcnow().isoformat(),
    })
    # Keep last 20 messages to avoid bloat
    conversation.messages_json = messages[-20:]
    conversation.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(conversation)
    return conversation


async def log_query(
    db: AsyncSession,
    farmer_id: int,
    query_text: str,
    language: str,
    intent: str,
    ai_response: str,
    response_time_ms: float,
) -> QueryLog:
    """Log a farmer query for analytics."""
    log = QueryLog(
        farmer_id=farmer_id,
        query_text=query_text,
        language_detected=language,
        intent=intent,
        ai_response=ai_response,
        response_time_ms=response_time_ms,
    )
    db.add(log)
    await db.commit()
    return log


async def get_all_farmers(db: AsyncSession, limit: int = 100, offset: int = 0) -> list[Farmer]:
    """Get all farmers (admin)."""
    stmt = select(Farmer).order_by(Farmer.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_farmer_by_phone(db: AsyncSession, phone: str) -> Farmer | None:
    """Get farmer by phone number."""
    stmt = select(Farmer).where(Farmer.phone == phone)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_farmer_queries(
    db: AsyncSession, farmer_id: int, limit: int = 50
) -> list[QueryLog]:
    """Get query history for a farmer."""
    stmt = (
        select(QueryLog)
        .where(QueryLog.farmer_id == farmer_id)
        .order_by(QueryLog.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
