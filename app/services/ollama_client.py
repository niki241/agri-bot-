from typing import List, Optional

import httpx
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# System prompts for different languages
SYSTEM_PROMPTS = {
    "te": """నువ్వు కిసాన్ మిత్ర - భారతీయ రైతులకు సహాయం చేసే వ్యవసాయ సలహాదారు బాట్.
నువ్వు తెలుగులో సమాధానం ఇవ్వాలి.
రైతు తన పంట సమస్యను చెప్పినప్పుడు:
1. సమస్యను గుర్తించు (తెగులు/పురుగు/పోషక లోపం)
2. చికిత్స సూచించు (సేంద్రియ + రసాయన రెండూ)
3. మోతాదు స్థానిక యూనిట్లలో చెప్పు
4. అత్యవసరత స్థాయి చెప్పు (తక్కువ/మధ్యస్థం/ఎక్కువ/అత్యవసరం)
సమాధానం చిన్నగా, స్పష్టంగా ఉండాలి. WhatsApp లో చదవడానికి సులభంగా ఉండాలి.
⚠️ ముఖ్యమైన గమనిక: ఇది AI సలహా మాత్రమే. తీవ్రమైన సమస్యలకు మీ స్థానిక వ్యవసాయ అధికారిని సంప్రదించండి.""",

    "hi": """तुम किसान मित्र हो - भारतीय किसानों की मदद करने वाला कृषि सलाहकार बॉट।
तुम्हें हिंदी में जवाब देना है।
जब किसान अपनी फसल की समस्या बताए:
1. समस्या पहचानो (कीट/रोग/पोषक तत्व की कमी)
2. इलाज बताओ (जैविक + रासायनिक दोनों)
3. खुराक स्थानीय इकाइयों में बताओ
4. तत्काल स्तर बताओ (कम/मध्यम/अधिक/अत्यावश्यक)
जवाब छोटा और स्पष्ट हो। WhatsApp पर पढ़ने में आसान हो।
⚠️ महत्वपूर्ण: यह AI सलाह है। गंभीर समस्याओं के लिए अपने स्थानीय कृषि अधिकारी से संपर्क करें।""",

    "en": """You are Kisan Mitra - an agricultural advisory bot helping Indian farmers.
Reply in simple English that a farmer with basic education can understand.
When a farmer describes a crop problem:
1. Identify the issue (pest/disease/nutrient deficiency)
2. Suggest treatment (both organic and chemical options)
3. Give dosage in local units (bigha, acre)
4. State urgency level (low/medium/high/critical)
Keep responses short and clear for WhatsApp reading.
⚠️ Important: This is AI advice only. For severe issues, contact your local agriculture officer.""",
}

# Advisory prompt template with context
ADVISORY_TEMPLATE = """Farmer's location: {district}, {state}
Crops grown: {crops}
Season: {season}
Farmer's query: {query}

{kb_context}

Provide a helpful, practical advisory response."""


async def get_advisory(
    query: str,
    language: str = "en",
    district: str = "Unknown",
    state: str = "Unknown",
    crops: Optional[List[str]] = None,
    season: str = "Kharif",
    kb_context: str = "",
) -> str:
    """
    Get crop advisory from Ollama LLM.
    """
    system_prompt = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["en"])
    user_prompt = ADVISORY_TEMPLATE.format(
        district=district,
        state=state,
        crops=", ".join(crops) if crops else "Not specified",
        season=season,
        query=query,
        kb_context=f"Relevant knowledge base info:\n{kb_context}" if kb_context else "",
    )

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": user_prompt,
                    "system": system_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 300,
                        "top_p": 0.9,
                    },
                },
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()

    except httpx.ConnectError:
        logger.error("Ollama is not reachable at %s", settings.OLLAMA_BASE_URL)
        return _get_fallback_response(language)
    except httpx.TimeoutException:
        logger.error("Ollama request timed out")
        return _get_fallback_response(language)
    except Exception as e:
        logger.error("Ollama error: %s", str(e))
        return _get_fallback_response(language)


def _get_fallback_response(language: str) -> str:
    """Fallback response when Ollama is unavailable."""
    fallbacks = {
        "te": (
            "🙏 క్షమించండి, ప్రస్తుతం AI సేవ అందుబాటులో లేదు.\n\n"
            "దయచేసి కొద్ది సేపట్లో మళ్ళీ ప్రయత్నించండి.\n"
            "అత్యవసర సమస్యలకు మీ స్థానిక వ్యవసాయ అధికారిని సంప్రదించండి.\n"
            "☎️ కిసాన్ కాల్ సెంటర్: 1800-180-1551"
        ),
        "hi": (
            "🙏 क्षमा करें, अभी AI सेवा उपलब्ध नहीं है।\n\n"
            "कृपया कुछ देर बाद फिर से प्रयास करें।\n"
            "गंभीर समस्याओं के लिए अपने स्थानीय कृषि अधिकारी से संपर्क करें।\n"
            "☎️ किसान कॉल सेंटर: 1800-180-1551"
        ),
        "en": (
            "🙏 Sorry, AI service is currently unavailable.\n\n"
            "Please try again shortly.\n"
            "For urgent issues, contact your local agriculture officer.\n"
            "☎️ Kisan Call Centre: 1800-180-1551"
        ),
    }
    return fallbacks.get(language, fallbacks["en"])


async def check_ollama_health() -> bool:
    """Check if Ollama is running and the model is available."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(m["name"].startswith(settings.OLLAMA_MODEL.split(":")[0]) for m in models)
    except Exception:
        pass
    return False
