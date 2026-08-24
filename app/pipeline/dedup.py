import re


def normalize_name(name: str | None) -> str:
    if not name:
        return ""
    text = name.lower().strip()
    text = re.sub(r"\b(llc|inc|co|company|ltd|corp)\b\.?", "", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_domain(website: str | None) -> str:
    if not website:
        return ""
    domain = website.lower().strip()
    domain = re.sub(r"^https?://", "", domain)
    domain = re.sub(r"^www\.", "", domain)
    domain = domain.split("/")[0]
    return domain


def dedupe_leads(leads: list) -> list:
    seen_names = {}
    seen_domains = {}
    deduped = []

    for lead in leads:
        name_key = normalize_name(lead.company_name)
        domain_key = normalize_domain(lead.website)

        is_duplicate = (name_key and name_key in seen_names) or (domain_key and domain_key in seen_domains)

        if is_duplicate:
            continue

        if name_key:
            seen_names[name_key] = lead
        if domain_key:
            seen_domains[domain_key] = lead
        deduped.append(lead)

    return deduped