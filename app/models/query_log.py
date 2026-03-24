from datetime import datetime
from sqlalchemy import String, Text, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class QueryLog(Base):
    __tablename__ = "query_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    farmer_id: Mapped[int] = mapped_column(Integer, ForeignKey("farmers.id"), nullable=False, index=True)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    language_detected: Mapped[str] = mapped_column(String(10), nullable=False)
    intent: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ai_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    feedback: Mapped[str | None] = mapped_column(String(20), nullable=True)  # helpful, not_helpful, null
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
