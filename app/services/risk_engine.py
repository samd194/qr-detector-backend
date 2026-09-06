"""
Combines all individual checks into a final risk score and verdict.
This is the orchestrator — mirrors how a C# service method calls multiple
repository/helper methods and assembles a final result.
"""
from app.models.scan import AnalyzeResponse, PayloadType, RiskLevel, RiskFactor
from app.services.qr_parser import classify_payload, extract_domain, is_https
from app.services.safe_browsing import check_url_blacklist
from app.services.whois_check import get_domain_age_days
from app.services.brand_similarity import check_brand_similarity


async def analyze_content(raw_content: str) -> AnalyzeResponse:
    payload_type = classify_payload(raw_content)

    reasons: list[RiskFactor] = []
    score = 0
    domain = None
    domain_age_days = None
    https = None

    if payload_type == PayloadType.URL:
        domain = extract_domain(raw_content)
        https = is_https(raw_content)

        if not https:
            score += 15
        reasons.append(RiskFactor(
            code="NOT_HTTPS",
            label="Connection Security",
            triggered=not https,
            detail="This site does not use a secure HTTPS connection — data sent to it isn't encrypted."
                if not https else
                "This site uses a secure HTTPS connection.",
        ))

        if domain:
            blacklisted = await check_url_blacklist(raw_content)
            if blacklisted:
                score += 100
            reasons.append(RiskFactor(
                code="BLACKLISTED_URL",
                label="Threat Database Check",
                triggered=blacklisted,
                detail="This URL is flagged by Google Safe Browsing as malware or phishing."
                    if blacklisted else
                    "This URL is not listed on any known malware or phishing blacklist.",
            ))

            domain_age_days = get_domain_age_days(domain)
            is_new_domain = domain_age_days is not None and domain_age_days < 30
            if is_new_domain:
                score += 30

            if domain_age_days is not None:
                age_detail = (
                    f"This domain was registered only {domain_age_days} day(s) ago — new domains are commonly used for scams."
                    if is_new_domain else
                    f"This domain has been registered for {domain_age_days} day(s), which is not a red flag."
                )
            else:
                age_detail = "Domain registration date could not be determined."

            reasons.append(RiskFactor(
                code="NEWLY_REGISTERED",
                label="Domain Age",
                triggered=is_new_domain,
                detail=age_detail,
            ))

            is_similar, matched_brand = check_brand_similarity(domain)
            if is_similar:
                score += 40
            reasons.append(RiskFactor(
                code="BRAND_IMPERSONATION",
                label="Brand Impersonation Check",
                triggered=is_similar,
                detail=f"This domain closely resembles '{matched_brand}' but is not the official site — a common phishing tactic."
                    if is_similar else
                    "This domain does not closely resemble any known brand we checked against.",
            ))

    if score >= 70:
        risk_level = RiskLevel.DANGEROUS
    elif score >= 30:
        risk_level = RiskLevel.SUSPICIOUS
    else:
        risk_level = RiskLevel.SAFE

    confidence = min(96, max(50, score + 40))

    return AnalyzeResponse(
        payload_type=payload_type,
        raw_content=raw_content,
        risk_level=risk_level,
        confidence=confidence,
        score=score,
        reasons=reasons,
        domain=domain,
        domain_age_days=domain_age_days,
        is_https=https,
    )