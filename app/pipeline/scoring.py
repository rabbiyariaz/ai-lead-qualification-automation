from app.models.icp import DEFAULT_ICP_CONFIG
from app.models.lead import LeadFeatures


def company_size_score(size, icp_config=DEFAULT_ICP_CONFIG):
    try:
        size_num = int(size)
    except (TypeError, ValueError):
        return 0

    if icp_config.company_size_ideal_min <= size_num <= icp_config.company_size_ideal_max:
        return icp_config.company_size_ideal_score
    if icp_config.company_size_good_min <= size_num <= icp_config.company_size_good_max:
        return icp_config.company_size_good_score
    return icp_config.company_size_out_of_range_score


def website_presence_score(website_present, email_present, icp_config=DEFAULT_ICP_CONFIG):
    score = 0

    if not website_present:
        score += icp_config.website_missing_score
    elif not email_present:
        score += icp_config.email_missing_score

    if website_present and email_present:
        score += icp_config.complete_contact_score

    return score


def description_signal_score(positive_signals, negative_signals, icp_config=DEFAULT_ICP_CONFIG):
    positive_score = len(positive_signals) * icp_config.positive_signal_score
    negative_score = len(negative_signals) * icp_config.negative_signal_score
    return positive_score + negative_score


def score_lead(features: LeadFeatures, icp_config=DEFAULT_ICP_CONFIG):
    size_score = company_size_score(features.company_size, icp_config=icp_config)
    website_score = website_presence_score(features.website_present, features.email_present, icp_config=icp_config)
    description_score = description_signal_score(features.positive_signals, features.negative_signals, icp_config=icp_config)
    total = size_score + website_score + description_score

    if features.insufficient_data:
        status = "review"
    elif features.ambiguity_signals:
        status = "review"
    elif total >= icp_config.qualification_threshold:
        status = "qualified"
    elif total <= icp_config.disqualification_threshold:
        status = "disqualified"
    else:
        status = "review"

    breakdown = {
        "company_size": size_score,
        "website_presence": website_score,
        "description_signals": description_score,
    }
    explanation_parts = []
    if size_score:
        explanation_parts.append(f"Company size: {size_score:+d}")
    if website_score:
        explanation_parts.append(f"Website/email fit: {website_score:+d}")
    if description_score:
        explanation_parts.append(f"Description signals: {description_score:+d}")
    if features.insufficient_data:
        explanation_parts.append("Insufficient data (no website, email, or description) — routed to review")
    if features.ambiguity_signals:
        explanation_parts.append(f"Ambiguity detected: {', '.join(features.ambiguity_signals)} — routed to LLM review")

    return {
        "score": total,
        "decision": status,
        "score_breakdown": breakdown,
        "positive_signals": list(features.positive_signals),
        "negative_signals": list(features.negative_signals),
        "ambiguity_signals": list(features.ambiguity_signals),
        "insufficient_data": features.insufficient_data,
        "explanation": " | ".join(explanation_parts) if explanation_parts else "No scoring signals detected.",
        "features": features.model_dump(),
    }

def compute_rule_confidence(features, base_confidence, icp_config=DEFAULT_ICP_CONFIG):
    missing_count = sum([
        not features.email_present,
        not features.website_present,
        features.description_missing,
    ])
    confidence = base_confidence - (0.15 * missing_count)
    return max(0.1, round(confidence, 2))