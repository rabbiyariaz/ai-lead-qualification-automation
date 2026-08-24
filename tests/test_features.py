from app.models.icp import ICPConfig
from app.pipeline.features import extract_lead_features


def test_extract_features_returns_structured_data():
    lead = {
        "industry": "home services",
        "company_size": 12,
        "website": "",
        "email": "",
        "description": "Word of mouth only, growing fast, no online presence",
    }

    features = extract_lead_features(lead)

    assert features.company_size == 12
    assert features.company_size_fit is True
    assert features.website_present is False
    assert features.email_present is False
    assert features.website_missing is True
    assert features.email_missing is True
    assert features.growth_signal is True
    assert features.marketing_team_signal is False
    assert features.positive_signals


def test_extract_features_company_size_fit_uses_icp_boundaries():
    lead = {
        "industry": "home services",
        "company_size": 12,
        "website": "",
        "email": "",
        "description": "",
    }

    default_features = extract_lead_features(lead)
    custom_icp = ICPConfig(company_size_ideal_min=13, company_size_ideal_max=30)
    custom_features = extract_lead_features(lead, icp_config=custom_icp)

    assert default_features.company_size_fit is True
    assert custom_features.company_size_fit is False
