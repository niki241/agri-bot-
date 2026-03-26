from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://localhost/kisan_mitra"
    DATABASE_URL_SYNC: str = "postgresql://localhost/kisan_mitra"

    # WhatsApp Cloud API
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_VERIFY_TOKEN: str = "kisan_mitra_verify"
    WHATSAPP_API_VERSION: str = "v21.0"

    # LLM Provider: "groq" (cloud, free) or "ollama" (local)
    LLM_PROVIDER: str = "groq"

    # Groq API (free, fast — used on Railway)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    # Ollama (local dev fallback)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"

    # OpenWeatherMap
    OPENWEATHER_API_KEY: str = ""

    # Razorpay (future premium)
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""

    # App
    APP_ENV: str = "development"
    APP_SECRET_KEY: str = "change-this-to-a-random-secret"
    ADMIN_PASSWORD: str = "admin123"

    @property
    def whatsapp_api_url(self) -> str:
        return f"https://graph.facebook.com/{self.WHATSAPP_API_VERSION}/{self.WHATSAPP_PHONE_NUMBER_ID}/messages"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
