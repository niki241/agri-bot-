import re


# Intent keywords for classification (Telugu, Hindi, English)
INTENT_KEYWORDS = {
    "crop_problem": {
        "te": ["తెగులు", "పురుగు", "రోగం", "ఆకులు", "పసుపు", "ఎండిపోతున్న", "మచ్చలు", "కుళ్ళిపోతున్న", "పంట సమస్య", "చనిపోతున్న"],
        "hi": ["कीट", "रोग", "बीमारी", "पत्ते", "पीला", "सूखना", "दाग", "सड़ना", "फसल समस्या", "मरना"],
        "en": ["pest", "disease", "leaves", "yellow", "drying", "spots", "rotting", "wilting", "dying", "insect", "worm", "fungus", "blight"],
    },
    "weather": {
        "te": ["వాతావరణం", "వర్షం", "ఎండ", "చలి", "గాలి", "వరద"],
        "hi": ["मौसम", "बारिश", "धूप", "ठंड", "हवा", "बाढ़"],
        "en": ["weather", "rain", "sun", "cold", "wind", "flood", "temperature", "forecast"],
    },
    "price": {
        "te": ["ధర", "మార్కెట్", "మండి", "రేటు", "అమ్మకం"],
        "hi": ["भाव", "मंडी", "दाम", "रेट", "बिक्री", "बाजार"],
        "en": ["price", "market", "mandi", "rate", "sell", "cost"],
    },
    "scheme": {
        "te": ["పథకం", "సబ్సిడీ", "ప్రభుత్వం", "రైతు బంధు", "బీమా", "కిసాన్"],
        "hi": ["योजना", "सब्सिडी", "सरकार", "किसान", "बीमा", "पीएम"],
        "en": ["scheme", "subsidy", "government", "insurance", "pm-kisan", "loan"],
    },
    "greeting": {
        "te": ["నమస్కారం", "నమస్తే", "హలో", "హాయ్"],
        "hi": ["नमस्ते", "नमस्कार", "हैलो", "हाय"],
        "en": ["hello", "hi", "hey", "good morning", "good evening", "start", "help"],
    },
}


def classify_intent(text: str, language: str = "en") -> str:
    """
    Classify farmer's message intent.
    Returns: crop_problem, weather, price, scheme, greeting, or unknown
    """
    text_lower = text.lower().strip()

    # Check all languages (farmer might mix languages)
    scores: dict[str, int] = {}
    for intent, lang_keywords in INTENT_KEYWORDS.items():
        score = 0
        for lang, keywords in lang_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    # Give extra weight to farmer's detected language
                    weight = 2 if lang == language else 1
                    score += weight
        scores[intent] = score

    if not any(scores.values()):
        # Default: if it looks like a crop question, treat as crop_problem
        if len(text_lower) > 10:
            return "crop_problem"
        return "greeting"

    return max(scores, key=scores.get)
