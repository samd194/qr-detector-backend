"""
Google Safe Browsing API check — blacklist lookup for known-malicious URLs.
"""
import httpx

from app.config import settings

SAFE_BROWSING_URL = "https://safebrowsing.googleapis.com/v4/threatMatches:find"


async def check_url_blacklist(url: str) -> bool:
    """Returns True if the URL is flagged as malicious/phishing by Google."""
    payload = {
        "client": {"clientId": "qr-detector", "clientVersion": "1.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}],
        },
    }

    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.post(
                SAFE_BROWSING_URL,
                params={"key": settings.google_safe_browsing_key},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return "matches" in data and len(data["matches"]) > 0
        except httpx.HTTPError:
            # Fail safe: if the check itself fails, don't block the whole pipeline —
            # just report "not blacklisted" and let other signals carry the score.
            return False