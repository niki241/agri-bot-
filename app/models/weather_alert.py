from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class WeatherAlert(Base):
    __tablename__ = "weather_alerts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    district: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)
    message_te: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    message_hi: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    valid_from: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    valid_to: Mapped[datetime] = mapped_column(DateTime, nullable=False)
