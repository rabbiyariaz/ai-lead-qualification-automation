import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lead_scoring import (
    Lead,
    QualificationResult,
    analyze_lead,
    normalize_industry,
    openai_llm_client,
    run_qualification_pipeline,
)


def test_groq_client_factory_returns_none_without_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    assert openai_llm_client(api_key=None) is None


def test_industry_gate_rejects_out_of_niche():
    lead = {
        "industry": "food & beverage",
        "company_size": 50,
        "website": "https://example.com",
        "email": "hello@example.com",
        "description": "Established local restaurant with active marketing",
    }

    result = analyze_lead(lead)

    assert result["stage"] == "industry_gate"
    assert result["decision"] == "disqualified"
    assert result["reason"] == "disqualified: out of niche"


def test_target_industry_with_ideal_signals_is_qualified():
    lead = {
        "industry": "home services",
        "company_size": 12,
        "website": "",
        "email": "",
        "description": "Word of mouth only, growing fast, no online presence",
    }

    result = analyze_lead(lead)

    assert result["decision"] == "qualified"
    assert result["score"] >= 60
    assert result["stage"] == "scoring"


def test_normalize_industry_handles_common_aliases():
    assert normalize_industry("Plumbing Contractor") == "plumbing"
    assert normalize_industry(" HVAC ") == "hvac"
    assert normalize_industry("Emergency Plumbing Services") == "plumbing"
    assert normalize_industry("Residential Electrician") == "electrical"


def test_lead_and_result_models_are_validated():
    lead = Lead(
        company_name="North Valley Plumbing",
        industry="Plumbing Contractor",
        company_size="12",
        website="",
        email="",
        description="Word of mouth only; growing fast.",
    )

    result = QualificationResult(
        lead_id=lead.lead_id,
        decision="qualified",
        score=80,
        stage="scoring",
        reason="Rule-based scoring passed.",
        llm_reasoning="",
        confidence=0.9,
    )

    assert lead.industry == "Plumbing Contractor"
    assert normalize_industry(lead.industry) == "plumbing"
    assert result.decision == "qualified"
    assert 0 <= result.confidence <= 1


def test_review_lead_triggers_llm_reasoning_when_available():
    def fake_llm(prompt: str):
        return {
            "decision": "qualified",
            "reasoning": "The company has a clear need for lead generation and limited digital traction.",
        }

    lead = {
        "industry": "dental",
        "company_size": 65,
        "website": "https://smileworks.com",
        "email": "office@smileworks.com",
        "description": "We are a growing clinic with an in-house marketing manager and some digital ads.",
    }

    result = analyze_lead(lead, llm_client=fake_llm)

    assert result["decision"] == "qualified"
    assert result["stage"] == "llm_review"
    assert "need for lead generation" in result["llm_reasoning"].lower()


def test_csv_pipeline_exports_only_qualified_rows(tmp_path):
    input_csv = tmp_path / "leads.csv"
    output_csv = tmp_path / "qualified.csv"

    input_csv.write_text(
        "industry,company_size,website,email,description\n"
        "home services,12,,,Word of mouth only, no online presence\n"
        "food & beverage,20,,,Large chain with strong marketing\n"
        "dental,60,https://acmedental.com,hello@acmedental.com,We are growing and need help scaling\n",
        encoding="utf-8",
    )

    def fake_llm(prompt: str):
        return {
            "decision": "qualified",
            "reasoning": "This company shows growth and limited digital traction.",
        }

    run_qualification_pipeline(str(input_csv), str(output_csv), llm_client=fake_llm)

    with output_csv.open("r", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))

    assert len(rows) == 2
    assert {row["industry"] for row in rows} == {"home services", "dental"}
    assert all(row["decision"] == "qualified" for row in rows)
