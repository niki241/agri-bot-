import re
from langdetect import detect, LangDetectException


# Telugu Unicode range: \u0C00-\u0C7F
# Hindi/Devanagari Unicode range: \u0900-\u097F
TELUGU_PATTERN = re.compile(r"[\u0C00-\u0C7F]")
HINDI_PATTERN = re.compile(r"[\u0900-\u097F]")


def detect_language(text: str) -> str:
    """
    Detect language from text. Returns 'te', 'hi', or 'en'.
    Priority: script-based detection first, then langdetect fallback.
    """
    if not text or not text.strip():
        return "en"

    telugu_chars = len(TELUGU_PATTERN.findall(text))
    hindi_chars = len(HINDI_PATTERN.findall(text))
    total_alpha = sum(1 for c in text if c.isalpha())

    if total_alpha == 0:
        return "en"

    # If >30% of alphabetic chars are Telugu script
    if telugu_chars / total_alpha > 0.3:
        return "te"

    # If >30% of alphabetic chars are Devanagari script
    if hindi_chars / total_alpha > 0.3:
        return "hi"

    # Fallback to langdetect for transliterated text
    try:
        lang = detect(text)
        if lang == "te":
            return "te"
        elif lang in ("hi", "mr"):  # Marathi is close to Hindi
            return "hi"
    except LangDetectException:
        pass

    return "en"


# Common greetings in each language for quick detection
GREETINGS = {
    "te": ["నమస్కారం", "నమస్తే", "హలో", "బాగున్నారా"],
    "hi": ["नमस्ते", "नमस्कार", "हैलो", "कैसे हो"],
    "en": ["hello", "hi", "hey", "good morning", "good evening"],
}
