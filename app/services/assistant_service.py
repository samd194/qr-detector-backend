"""
AI assistant powered by Google Gemini — explains scan results and
answers general QR/scam safety questions.
"""
import httpx

from app.config import settings

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-3.5-flash:generateContent"
)

SYSTEM_CONTEXT = (
    "You are a helpful, concise safety assistant inside a QR code fraud detection app. "
    "You help users understand scan results and answer questions about QR code scams, "
    "phishing, and digital payment safety, especially in the Indian context (UPI, RBI guidelines). "
    "Keep answers short, practical, and non-technical unless asked for detail. "
    "Never provide information that could help someone create scams."
)


async def ask_assistant(user_message: str, scan_context: str | None = None) -> str:
    prompt = SYSTEM_CONTEXT
    if scan_context:
        prompt += f"\n\nContext about the user's current scan result:\n{scan_context}"
    prompt += f"\n\nUser question: {user_message}"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            GEMINI_URL,
            headers={
                "x-goog-api-key": settings.gemini_api_key,
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return "Sorry, I couldn't generate a response. Please try again."