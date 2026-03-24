from typing import Dict, List, Optional

import httpx
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def send_text_message(to: str, text: str) -> bool:
    """
    Send a text message via WhatsApp Cloud API.
    `to` should be the full phone number with country code (e.g., '919876543210').
    """
    url = settings.whatsapp_api_url
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"preview_url": False, "body": text},
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            logger.info("WhatsApp message sent to %s", to)
            return True
    except httpx.HTTPStatusError as e:
        logger.error("WhatsApp API error %s: %s", e.response.status_code, e.response.text)
        return False
    except Exception as e:
        logger.error("WhatsApp send error: %s", str(e))
        return False


async def send_interactive_buttons(to: str, body_text: str, buttons: List[Dict]) -> bool:
    """
    Send an interactive button message.
    buttons: [{"id": "btn_1", "title": "Option 1"}, ...]
    Max 3 buttons.
    """
    url = settings.whatsapp_api_url
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    button_rows = [
        {"type": "reply", "reply": {"id": btn["id"], "title": btn["title"][:20]}}
        for btn in buttons[:3]
    ]
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text},
            "action": {"buttons": button_rows},
        },
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return True
    except Exception as e:
        logger.error("WhatsApp interactive send error: %s", str(e))
        return False


def extract_message_data(payload: dict) -> Optional[dict]:
    """
    Extract message data from WhatsApp webhook payload.
    Returns dict with keys: from_number, message_type, text, message_id
    """
    try:
        entry = payload.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            return None

        msg = messages[0]
        from_number = msg.get("from", "")
        message_id = msg.get("id", "")
        message_type = msg.get("type", "")

        text = ""
        if message_type == "text":
            text = msg.get("text", {}).get("body", "")
        elif message_type == "interactive":
            interactive = msg.get("interactive", {})
            if interactive.get("type") == "button_reply":
                text = interactive.get("button_reply", {}).get("title", "")
            elif interactive.get("type") == "list_reply":
                text = interactive.get("list_reply", {}).get("title", "")
        elif message_type == "audio":
            # Phase 2: voice note handling
            text = "[voice_note]"

        return {
            "from_number": from_number,
            "message_type": message_type,
            "text": text,
            "message_id": message_id,
        }
    except (IndexError, KeyError) as e:
        logger.error("Error extracting WhatsApp message: %s", str(e))
        return None


# Welcome messages for first-time farmers
WELCOME_MESSAGES = {
    "te": (
        "🌾 *కిసాన్ మిత్రకు స్వాగతం!* 🙏\n\n"
        "నేను మీ వ్యవసాయ సహాయకుడిని. మీకు ఈ విషయాల్లో సహాయం చేయగలను:\n\n"
        "🌱 *పంట సమస్యలు* — తెగులు, పురుగులు, పోషక లోపాలు\n"
        "🌤️ *వాతావరణం* — వర్షం, ఎండ సమాచారం\n"
        "💰 *మార్కెట్ ధరలు* — మండి రేట్లు\n"
        "📋 *ప్రభుత్వ పథకాలు* — సబ్సిడీలు, బీమా\n\n"
        "మీ సమస్యను తెలుగులో టైప్ చేయండి! 👇\n\n"
        "⚠️ _ఇది AI సలహా. తీవ్ర సమస్యలకు వ్యవసాయ అధికారిని సంప్రదించండి._"
    ),
    "hi": (
        "🌾 *किसान मित्र में आपका स्वागत है!* 🙏\n\n"
        "मैं आपका कृषि सहायक हूँ। मैं इन विषयों में मदद कर सकता हूँ:\n\n"
        "🌱 *फसल समस्या* — कीट, रोग, पोषक तत्व की कमी\n"
        "🌤️ *मौसम* — बारिश, धूप की जानकारी\n"
        "💰 *बाजार भाव* — मंडी रेट\n"
        "📋 *सरकारी योजनाएं* — सब्सिडी, बीमा\n\n"
        "अपनी समस्या हिंदी में टाइप करें! 👇\n\n"
        "⚠️ _यह AI सलाह है। गंभीर समस्याओं के लिए कृषि अधिकारी से संपर्क करें।_"
    ),
    "en": (
        "🌾 *Welcome to Kisan Mitra!* 🙏\n\n"
        "I am your agriculture assistant. I can help with:\n\n"
        "🌱 *Crop Problems* — pests, diseases, nutrient deficiency\n"
        "🌤️ *Weather* — rain, sun forecast\n"
        "💰 *Market Prices* — mandi rates\n"
        "📋 *Government Schemes* — subsidies, insurance\n\n"
        "Type your problem in Telugu, Hindi, or English! 👇\n\n"
        "⚠️ _This is AI advice. For severe issues, contact your agriculture officer._"
    ),
}
