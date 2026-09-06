"""
Domain age lookup via WHOIS — new domains are a strong phishing signal.
"""
from datetime import datetime, timezone
import whois


def get_domain_age_days(domain: str) -> int | None:
    """Returns domain age in days, or None if lookup fails."""
    try:
        w = whois.whois(domain)
        creation_date = w.creation_date

        if isinstance(creation_date, list):
            creation_date = creation_date[0]

        if not creation_date:
            return None

        if creation_date.tzinfo is None:
            creation_date = creation_date.replace(tzinfo=timezone.utc)

        age = datetime.now(timezone.utc) - creation_date
        return age.days
    except Exception:
        return None