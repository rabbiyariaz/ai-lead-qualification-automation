import re

from matplotlib import markers

from app.models.icp import DEFAULT_ICP_CONFIG
from app.models.lead import LeadFeatures
from app.pipeline.industry_gate import normalize_lead


def extract_lead_features(lead, icp_config=DEFAULT_ICP_CONFIG):
    normalized = normalize_lead(lead)
    description_text = (normalized.description or "").lower()


    def matched(markers):
        return [label for pattern, label in markers if re.search(pattern, description_text)]

    positive_signals = matched(icp_config.positive_markers)
    negative_signals = matched(icp_config.negative_markers)
    ambiguity_signals = matched(icp_config.ambiguity_markers)


    company_size_fit = bool(
        normalized.company_size is not None
        and icp_config.company_size_ideal_min <= normalized.company_size <= icp_config.company_size_ideal_max
    )
    website_missing = not normalized.website_present
    email_missing = not normalized.email_present
    description_missing = not bool(normalized.description)

    insufficient_data = website_missing and email_missing and description_missing

    return LeadFeatures(
        company_size=normalized.company_size,
        company_size_fit=company_size_fit,
        website_present=normalized.website_present,
        email_present=normalized.email_present,
        website_missing=website_missing,
        email_missing=email_missing,
        description_missing=description_missing,
        insufficient_data=insufficient_data,
        growth_signal=bool(positive_signals),
        marketing_team_signal=bool(negative_signals),
        positive_signals=positive_signals,
        negative_signals=negative_signals,
        ambiguity_signals=ambiguity_signals,
    )