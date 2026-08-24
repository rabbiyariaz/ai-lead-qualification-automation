import app.llm.prompts as prompts_module
from app.llm.prompts import build_qualification_prompt
from app.models.lead import LeadFeatures
from app.pipeline.orchestrator import llm_review
from app.llm.schemas import safe_llm_result


def test_llm_schema_handles_malformed_response():
    payload = {"decision": "qualified", "confidence": 2.0, "reasoning": "ok"}

    result = safe_llm_result(payload)

    assert result["decision"] == "review"
    assert result["confidence"] == 0.0
    assert "manual review" in result["reasoning"].lower()


def test_prompt_builder_uses_supplied_evidence():
    lead = {
        "industry": "dental",
        "company_size": 65,
        "website": "https://example.com",
        "email": "owner@example.com",
        "description": "Growing clinic with in-house marketing team.",
    }
    features = LeadFeatures(
        company_size=65,
        company_size_fit=False,
        website_present=True,
        email_present=True,
        website_missing=False,
        email_missing=False,
        growth_signal=True,
        marketing_team_signal=True,
        positive_signals=["growing"],
        negative_signals=["in-house marketing team"],
    )
    scored = {
        "score": 20,
        "decision": "review",
        "score_breakdown": {
            "company_size": 15,
            "website_presence": -5,
            "description_signals": 10,
        },
    }

    prompt = build_qualification_prompt(lead, features=features, scored=scored)

    assert "Rule-based pre-LLM decision: review" in prompt
    assert "Rule score: 20" in prompt
    assert "'company_size': 15" in prompt
    assert "Positive signals: ['growing']" in prompt
    assert "Negative signals: ['in-house marketing team']" in prompt


def test_prompts_module_has_no_feature_or_scoring_imports():
    assert not hasattr(prompts_module, "extract_lead_features")
    assert not hasattr(prompts_module, "score_lead")


def test_llm_review_behavior_unchanged_for_valid_llm_response():
    lead = {
        "industry": "dental",
        "company_size": 65,
        "website": "https://example.com",
        "email": "owner@example.com",
        "description": "Growing clinic with in-house marketing team.",
    }

    def fake_llm(_prompt: str):
        return {
            "decision": "qualified",
            "confidence": 0.83,
            "reasoning": "Strong growth indicators and lead-generation need.",
            "positive_signals": ["growing"],
            "negative_signals": ["in-house marketing team"],
        }

    result = llm_review(lead, llm_client=fake_llm)

    assert result["stage"] == "llm_review"
    assert result["decision"] == "qualified"
    assert result["llm_reasoning"] == "Strong growth indicators and lead-generation need."
    assert "score_breakdown" in result
    assert "score" in result
