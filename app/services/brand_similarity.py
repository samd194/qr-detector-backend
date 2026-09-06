"""
Typosquatting / brand impersonation detection using fuzzy string matching.
"""
from Levenshtein import distance as levenshtein_distance

KNOWN_BRANDS = [
    "paytm.com",
    "phonepe.com",
    "googlepay.com",
    "amazon.in",
    "flipkart.com",
    "sbi.co.in",
    "hdfcbank.com",
    "icicibank.com",
    "axisbank.com",
]


def _core_name(domain: str) -> str:
    """Strip TLD to get the registrable core name, e.g. 'paytm.com' -> 'paytm'."""
    return domain.split(".")[0]


def check_brand_similarity(domain: str) -> tuple[bool, str | None]:
    """
    Returns (is_suspicious, matched_brand).
    Flags domains that embed or closely resemble a known brand name
    without being the brand's actual official domain.
    """
    domain = domain.lower().replace("www.", "")
    domain_core = _core_name(domain)

    for brand in KNOWN_BRANDS:
        if domain == brand:
            return False, None  # exact match to legit brand — not suspicious

        brand_core = _core_name(brand)

        # Case 1: brand name is embedded in the domain (e.g. "paytm-verification.xyz")
        if brand_core in domain_core and domain_core != brand_core:
            return True, brand

        # Case 2: core name is a close typo of the brand (e.g. "paytnn.com")
        dist = levenshtein_distance(domain_core, brand_core)
        if dist <= max(1, len(brand_core) // 5) and domain_core != brand_core:
            return True, brand

    return False, None