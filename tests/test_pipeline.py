from app.pipeline.orchestrator import qualify_lead


def test_pipeline_routes_qualified_lead_without_llm():
    lead = {
        "industry": "home services",
        "company_size": 12,
        "website": "",
        "email": "",
        "description": "Word of mouth only, growing fast, no online presence",
    }

    result = qualify_lead(lead)

    assert result["decision"] == "qualified"
    assert result["stage"] == "scoring"
    assert result["score"] >= 50


def test_pipeline_rejects_out_of_niche_industry():
    lead = {
        "industry": "food & beverage",
        "company_size": 50,
        "website": "https://example.com",
        "email": "hello@example.com",
        "description": "Strong existing marketing",
    }

    result = qualify_lead(lead)

    assert result["decision"] == "disqualified"
    assert result["stage"] == "industry_gate"
