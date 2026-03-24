import time
import logging
from fastapi import APIRouter, Request, Query, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.services.whatsapp import extract_message_data, send_text_message, send_interactive_buttons, WELCOME_MESSAGES
from app.services.language import detect_language
from app.services.intent import classify_intent
from app.services.ollama_client import get_advisory
from app.services.knowledge_base import search_advisories, format_kb_context
from app.services.farmer_service import (
    get_or_create_farmer,
    update_farmer_language,
    get_or_create_conversation,
    append_message,
    log_query,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhook", tags=["webhook"])
settings = get_settings()


@router.get("/whatsapp")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    """WhatsApp webhook verification (Meta challenge-response)."""
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("WhatsApp webhook verified successfully")
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/whatsapp")
async def receive_whatsapp(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Receive incoming WhatsApp messages and process them."""
    payload = await request.json()

    msg_data = extract_message_data(payload)
    if not msg_data or not msg_data["text"]:
        return {"status": "no_message"}

    # Process in background to return 200 quickly (WhatsApp requires fast response)
    background_tasks.add_task(
        process_message,
        from_number=msg_data["from_number"],
        text=msg_data["text"],
        message_type=msg_data["message_type"],
    )

    return {"status": "received"}


async def process_message(from_number: str, text: str, message_type: str):
    """Process a farmer's message end-to-end."""
    start_time = time.time()

    async with get_db_session() as db:
        try:
            # 1. Detect language
            language = detect_language(text)

            # 2. Get or create farmer
            farmer, is_new = await get_or_create_farmer(db, from_number, language)

            # 3. Send welcome message for new farmers
            if is_new:
                welcome = WELCOME_MESSAGES.get(language, WELCOME_MESSAGES["en"])
                await send_text_message(from_number, welcome)
                # Also send quick-reply buttons
                await send_interactive_buttons(
                    from_number,
                    _get_menu_text(language),
                    _get_menu_buttons(language),
                )
                return

            # 4. Update language preference
            await update_farmer_language(db, farmer, language)

            # 5. Get/create conversation and log incoming message
            conversation = await get_or_create_conversation(db, farmer.id)
            await append_message(db, conversation, "farmer", text)

            # 6. Classify intent
            intent = classify_intent(text, language)

            # 7. Generate response based on intent
            if intent == "greeting":
                response_text = _get_greeting_response(language)
                await send_interactive_buttons(
                    from_number,
                    response_text,
                    _get_menu_buttons(language),
                )
            elif intent == "crop_problem":
                response_text = await _handle_crop_problem(
                    db, text, language, farmer
                )
                await send_text_message(from_number, response_text)
            elif intent == "weather":
                response_text = _get_weather_placeholder(language, farmer.district)
                await send_text_message(from_number, response_text)
            elif intent == "price":
                response_text = _get_price_placeholder(language)
                await send_text_message(from_number, response_text)
            elif intent == "scheme":
                response_text = _get_scheme_placeholder(language)
                await send_text_message(from_number, response_text)
            else:
                response_text = await _handle_crop_problem(
                    db, text, language, farmer
                )
                await send_text_message(from_number, response_text)

            # 8. Log outgoing message
            await append_message(db, conversation, "bot", response_text)

            # 9. Log query for analytics
            elapsed_ms = (time.time() - start_time) * 1000
            await log_query(
                db, farmer.id, text, language, intent, response_text, elapsed_ms
            )

        except Exception as e:
            logger.error("Error processing message from %s: %s", from_number, str(e))
            error_msg = _get_error_response(detect_language(text))
            await send_text_message(from_number, error_msg)


async def _handle_crop_problem(
    db: AsyncSession, query: str, language: str, farmer
) -> str:
    """Handle a crop problem query with KB + Ollama."""
    # Search knowledge base for grounding context
    advisories = await search_advisories(db, query, language)
    kb_context = format_kb_context(advisories)

    # Get AI advisory
    response = await get_advisory(
        query=query,
        language=language,
        district=farmer.district or "Unknown",
        state=farmer.state or "Unknown",
        crops=farmer.crops,
        kb_context=kb_context,
    )

    return response


# --- Helper functions for localized responses ---

def _get_greeting_response(language: str) -> str:
    responses = {
        "te": "🙏 నమస్కారం! మీకు ఏ విషయంలో సహాయం కావాలి?",
        "hi": "🙏 नमस्ते! आपको किस विषय में मदद चाहिए?",
        "en": "🙏 Hello! How can I help you today?",
    }
    return responses.get(language, responses["en"])


def _get_menu_text(language: str) -> str:
    texts = {
        "te": "ఏ విషయంలో సహాయం కావాలి?",
        "hi": "किस विषय में मदद चाहिए?",
        "en": "What do you need help with?",
    }
    return texts.get(language, texts["en"])


def _get_menu_buttons(language: str) -> list[dict]:
    buttons = {
        "te": [
            {"id": "crop_problem", "title": "🌱 పంట సమస్య"},
            {"id": "weather", "title": "🌤️ వాతావరణం"},
            {"id": "price", "title": "💰 మార్కెట్ ధర"},
        ],
        "hi": [
            {"id": "crop_problem", "title": "🌱 फसल समस्या"},
            {"id": "weather", "title": "🌤️ मौसम"},
            {"id": "price", "title": "💰 बाजार भाव"},
        ],
        "en": [
            {"id": "crop_problem", "title": "🌱 Crop Problem"},
            {"id": "weather", "title": "🌤️ Weather"},
            {"id": "price", "title": "💰 Market Price"},
        ],
    }
    return buttons.get(language, buttons["en"])


def _get_weather_placeholder(language: str, district: str | None) -> str:
    responses = {
        "te": f"🌤️ వాతావరణ సమాచారం త్వరలో అందుబాటులో ఉంటుంది.\n📍 జిల్లా: {district or 'తెలియదు'}\n\nమీ జిల్లా పేరు చెప్పండి.",
        "hi": f"🌤️ मौसम की जानकारी जल्द उपलब्ध होगी।\n📍 जिला: {district or 'अज्ञात'}\n\nअपने जिले का नाम बताएं।",
        "en": f"🌤️ Weather info coming soon.\n📍 District: {district or 'Unknown'}\n\nPlease tell me your district name.",
    }
    return responses.get(language, responses["en"])


def _get_price_placeholder(language: str) -> str:
    responses = {
        "te": "💰 మార్కెట్ ధరల సేవ త్వరలో అందుబాటులో ఉంటుంది.\n\nమీ పంట పేరు చెప్పండి — ధర తెలుసుకుందాం!",
        "hi": "💰 बाजार भाव सेवा जल्द उपलब्ध होगी।\n\nअपनी फसल का नाम बताएं — भाव जानें!",
        "en": "💰 Market price service coming soon.\n\nTell me your crop name to check prices!",
    }
    return responses.get(language, responses["en"])


def _get_scheme_placeholder(language: str) -> str:
    responses = {
        "te": (
            "📋 ముఖ్యమైన ప్రభుత్వ పథకాలు:\n\n"
            "1️⃣ *PM-KISAN* — ₹6,000/సంవత్సరం\n"
            "2️⃣ *రైతు బంధు* — ₹10,000/ఎకరం (తెలంగాణ)\n"
            "3️⃣ *PM ఫసల్ బీమా* — పంట బీమా\n\n"
            "☎️ హెల్ప్‌లైన్: 1800-180-1551"
        ),
        "hi": (
            "📋 महत्वपूर्ण सरकारी योजनाएं:\n\n"
            "1️⃣ *PM-KISAN* — ₹6,000/वर्ष\n"
            "2️⃣ *PM फसल बीमा* — फसल बीमा\n"
            "3️⃣ *किसान क्रेडिट कार्ड* — कम ब्याज ऋण\n\n"
            "☎️ हेल्पलाइन: 1800-180-1551"
        ),
        "en": (
            "📋 Key Government Schemes:\n\n"
            "1️⃣ *PM-KISAN* — ₹6,000/year\n"
            "2️⃣ *PM Fasal Bima* — crop insurance\n"
            "3️⃣ *Kisan Credit Card* — low interest loans\n\n"
            "☎️ Helpline: 1800-180-1551"
        ),
    }
    return responses.get(language, responses["en"])


def _get_error_response(language: str) -> str:
    responses = {
        "te": "😔 క్షమించండి, లోపం జరిగింది. దయచేసి మళ్ళీ ప్రయత్నించండి.",
        "hi": "😔 क्षमा करें, कोई त्रुटि हुई। कृपया फिर से प्रयास करें।",
        "en": "😔 Sorry, an error occurred. Please try again.",
    }
    return responses.get(language, responses["en"])


# DB session context manager for background tasks
from contextlib import asynccontextmanager
from app.database import async_session


@asynccontextmanager
async def get_db_session():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
