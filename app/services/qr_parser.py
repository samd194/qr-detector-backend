"""
Classifies the raw decoded QR string into a payload type,
and extracts the domain if it's a URL.
"""
import re
from urllib.parse import urlparse

from app.models.scan import PayloadType


def classify_payload(raw_content: str) -> PayloadType:
    content = raw_content.strip()

    if content.lower().startswith(("http://", "https://")):
        return PayloadType.URL
    if content.lower().startswith("upi://"):
        return PayloadType.UPI
    if content.upper().startswith("WIFI:"):
        return PayloadType.WIFI
    if re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$", content):
        # Looks like a bare domain without scheme, e.g. "paytm-verify.xyz/pay"
        return PayloadType.URL

    return PayloadType.TEXT if content else PayloadType.UNKNOWN


def extract_domain(raw_content: str) -> str | None:
    content = raw_content.strip()
    if not content.lower().startswith(("http://", "https://")):
        content = "http://" + content  # allow parsing bare domains

    try:
        parsed = urlparse(content)
        return parsed.netloc.lower()
    except Exception:
        return None


def is_https(raw_content: str) -> bool:
    return raw_content.strip().lower().startswith("https://")