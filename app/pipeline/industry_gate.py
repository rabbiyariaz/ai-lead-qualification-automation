import re

from app.models.icp import DEFAULT_ICP_CONFIG, INDUSTRY_ALIASES
from app.models.lead import Lead, NormalizedLead


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def is_valid_email(email: str | None) -> bool:
    if not email:
        return False
    return bool(EMAIL_PATTERN.match(email.strip()))

def normalize_industry(industry):
    if industry is None:
        return ""

    text = str(industry).strip().lower()
    if not text:
        return ""

    text = re.sub(r"[^a-z0-9&\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    for canonical, aliases in INDUSTRY_ALIASES.items():
        if text in aliases:
            return canonical

    for canonical in INDUSTRY_ALIASES:
        if text.startswith(canonical) or text.endswith(canonical):
            return canonical

    return text


def normalize_lead(lead):
    if isinstance(lead, NormalizedLead):
        return lead

    raw_lead = lead if isinstance(lead, Lead) else Lead.model_validate(lead)
    normalized_industry = normalize_industry(raw_lead.industry)

    try:
        company_size = int(raw_lead.company_size)
    except (TypeError, ValueError):
        company_size = None

    website = raw_lead.website.strip() if raw_lead.website else None
    email = raw_lead.email.strip() if raw_lead.email else None
    description = raw_lead.description.strip() if raw_lead.description else None

    return NormalizedLead(
        lead_id=raw_lead.lead_id,
        company_name=raw_lead.company_name,
        industry=raw_lead.industry,
        normalized_industry=normalized_industry,
        company_size=company_size,
        website=website,
        email=email,
        location=raw_lead.location,
        description=description,
        website_present=bool(website),
        email_present=is_valid_email(email),
    )


def industry_gate(lead, icp_config=DEFAULT_ICP_CONFIG):
    normalized = normalize_lead(lead)
    if normalized.normalized_industry not in icp_config.target_industries:
        return {
            "stage": "industry_gate",
            "decision": "disqualified",
            "reason": "disqualified: out of niche",
            "normalized_industry": normalized.normalized_industry,
        }
    return None
