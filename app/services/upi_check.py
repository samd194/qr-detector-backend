"""
Heuristic checks for UPI payment QR codes.
Note: unlike URLs, there's no public blacklist/registry for UPI VPAs,
so this is necessarily heuristic-based rather than authoritative.
"""
import re
from urllib.parse import urlparse, parse_qs

# Legitimate UPI handles issued by banks/PSPs. Not exhaustive, but covers
# the vast majority of real Indian UPI traffic.
KNOWN_UPI_HANDLES = {
    "okaxis", "okhdfcbank", "oksbi", "okicici", "ybl", "ibl", "axl",
    "paytm", "upi", "apl", "sbi", "hdfcbank", "icici", "axisbank",
    "kotak", "yesbank", "idfcbank", "federal", "pnb", "unionbank",
    "boi", "cnrb", "indus", "rbl", "jio", "airtel", "fbl",
}

SUSPICIOUS_NAME_KEYWORDS = [
    "refund", "cashback", "reward", "prize", "winner", "lottery",
    "verify", "kyc", "support team", "customer care",
]


def parse_upi_params(raw_content: str) -> dict:
    parsed = urlparse(raw_content)
    return {k: v[0] for k, v in parse_qs(parsed.query).items()}


def is_valid_vpa_format(vpa: str) -> bool:
    return bool(re.match(r"^[\w.\-]{2,256}@[a-zA-Z]{2,64}$", vpa))


def check_upi_risk(raw_content: str) -> dict:
    """Returns a dict of {factor_code: (triggered, detail)}."""
    params = parse_upi_params(raw_content)
    vpa = params.get("pa", "")
    payee_name = params.get("pn", "")
    amount = params.get("am")

    results = {}

    # 1. VPA format check
    valid_format = is_valid_vpa_format(vpa) if vpa else False
    results["INVALID_VPA_FORMAT"] = (
        not valid_format,
        "This UPI ID is missing or badly formatted — legitimate payment QR codes always have a valid ID."
        if not valid_format else
        "The UPI ID is correctly formatted.",
    )

    # 2. Known handle check
    handle = vpa.split("@")[-1].lower() if "@" in vpa else ""
    known_handle = handle in KNOWN_UPI_HANDLES
    results["UNKNOWN_UPI_HANDLE"] = (
        valid_format and not known_handle,
        f"'@{handle}' is not a widely recognized bank/PSP handle — proceed with caution."
        if (valid_format and not known_handle) else
        "This UPI ID uses a recognized bank/PSP handle.",
    )

    # 3. Missing payee name
    missing_name = not payee_name.strip()
    results["MISSING_PAYEE_NAME"] = (
        missing_name,
        "No payee name is provided — legitimate merchant QR codes almost always identify who you're paying."
        if missing_name else
        "A payee name is provided.",
    )

    # 4. Suspicious payee name wording
    name_lower = payee_name.lower()
    suspicious_name = any(word in name_lower for word in SUSPICIOUS_NAME_KEYWORDS)
    results["SUSPICIOUS_PAYEE_NAME"] = (
        suspicious_name,
        f"The payee name '{payee_name}' contains wording commonly used in refund/cashback scams — remember, receiving money never requires scanning a QR or entering your PIN."
        if suspicious_name else
        "The payee name doesn't contain common scam wording.",
    )

    # 5. Large pre-filled amount
    large_amount = False
    if amount:
        try:
            large_amount = float(amount) >= 5000
        except ValueError:
            pass
    results["LARGE_PREFILLED_AMOUNT"] = (
        large_amount,
        f"This QR locks in a payment of ₹{amount} — double-check this is the amount you expect before proceeding."
        if large_amount else
        "No unusually large pre-filled amount detected.",
    )

    return results