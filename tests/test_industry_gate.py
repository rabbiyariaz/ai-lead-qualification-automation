from app.models.icp import ICPConfig
from app.pipeline.industry_gate import industry_gate, normalize_industry


def test_normalize_industry_handles_aliases():
    assert normalize_industry("Plumbing Contractor") == "plumbing"
    assert normalize_industry(" HVAC ") == "hvac"
    assert normalize_industry("Emergency Plumbing Services") == "plumbing"
    assert normalize_industry("Residential Electrician") == "electrical"


def test_industry_gate_accepts_default_target_industry():
    lead = {
        "industry": "home services",
        "company_size": 12,
    }

    result = industry_gate(lead)

    assert result is None


def test_industry_gate_rejects_out_of_niche_industry():
    lead = {
        "industry": "food & beverage",
        "company_size": 12,
    }

    result = industry_gate(lead)

    assert result is not None
    assert result["decision"] == "disqualified"
    assert result["stage"] == "industry_gate"


def test_industry_gate_uses_custom_target_industries():
    lead = {
        "industry": "food & beverage",
        "company_size": 12,
    }
    custom_icp = ICPConfig(target_industries={"food & beverage"})

    result = industry_gate(lead, icp_config=custom_icp)

    assert result is None


def test_industry_gate_applies_alias_before_target_check():
    lead = {
        "industry": "Plumbing Contractor",
        "company_size": 12,
    }

    result = industry_gate(lead)

    assert result is None
