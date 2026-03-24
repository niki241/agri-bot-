from datetime import date
from typing import Optional
from sqlalchemy import String, Float, Date
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class MarketPrice(Base):
    __tablename__ = "market_prices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    commodity: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    market: Mapped[str] = mapped_column(String(200), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    price_date: Mapped[date] = mapped_column(Date, nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
