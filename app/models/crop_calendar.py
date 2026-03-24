from typing import Optional
from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class CropCalendar(Base):
    __tablename__ = "crop_calendar"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    crop: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    region: Mapped[str] = mapped_column(String(100), nullable=False)
    activity: Mapped[str] = mapped_column(String(200), nullable=False)
    month_start: Mapped[int] = mapped_column(Integer, nullable=False)
    month_end: Mapped[int] = mapped_column(Integer, nullable=False)
    description_te: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_hi: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
