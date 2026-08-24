from app.models.icp import ICPConfig
from app.models.lead import LeadFeatures
from app.pipeline import scoring
from app.pipeline.scoring import score_lead


def test_score_lead_qualifies_ideal_signal_profile():
    features = LeadFeatures(
        company_size=12,
        company_size_fit=True,
        website_present=False,
        email_present=False,
        website_missing=True,
        email_missing=True,
        growth_signal=True,
        marketing_team_signal=False,
        positive_signals=["word of mouth", "growing fast", "no online presence"],
        negative_signals=[],
    )

    result = score_lead(features)

    assert result["decision"] == "qualified"
    assert result["score"] == 100
    assert result["score_breakdown"]["company_size"] == 30
    assert result["score_breakdown"]["website_presence"] == 25
    assert result["score_breakdown"]["description_signals"] == 45


def test_score_lead_threshold_boundaries(monkeypatch):
    features = LeadFeatures(
        company_size=12,
        company_size_fit=True,
        website_present=False,
        email_present=False,
        website_missing=True,
        email_missing=True,
        growth_signal=False,
        marketing_team_signal=False,
        positive_signals=[],
        negative_signals=[],
    )

    for total, expected in [
        (9, "disqualified"),
        (10, "disqualified"),
        (11, "review"),
        (12, "review"),
        (49, "review"),
        (50, "qualified"),
        (51, "qualified"),
    ]:
        monkeypatch.setattr(scoring, "company_size_score", lambda *_args, **_kwargs: total)
        monkeypatch.setattr(scoring, "website_presence_score", lambda *_args, **_kwargs: 0)
        monkeypatch.setattr(scoring, "description_signal_score", lambda *_args, **_kwargs: 0)

        result = score_lead(features)
        assert result["score"] == total
        assert result["decision"] == expected


def test_score_lead_uses_custom_icp_thresholds(monkeypatch):
    features = LeadFeatures(
        company_size=12,
        company_size_fit=True,
        website_present=False,
        email_present=False,
        website_missing=True,
        email_missing=True,
        growth_signal=False,
        marketing_team_signal=False,
        positive_signals=[],
        negative_signals=[],
    )

    monkeypatch.setattr(scoring, "company_size_score", lambda *_args, **_kwargs: 50)
    monkeypatch.setattr(scoring, "website_presence_score", lambda *_args, **_kwargs: 0)
    monkeypatch.setattr(scoring, "description_signal_score", lambda *_args, **_kwargs: 0)

    default_result = score_lead(features)
    custom_icp = ICPConfig(qualification_threshold=70, disqualification_threshold=20, review_threshold=20)
    custom_result = score_lead(features, icp_config=custom_icp)

    assert default_result["score"] == 50
    assert default_result["decision"] == "qualified"
    assert custom_result["score"] == 50
    assert custom_result["decision"] == "review"


def test_score_lead_uses_custom_scoring_weights_and_breakdown():
    features = LeadFeatures(
        company_size=12,
        company_size_fit=True,
        website_present=False,
        email_present=False,
        website_missing=True,
        email_missing=True,
        growth_signal=True,
        marketing_team_signal=False,
        positive_signals=["word of mouth", "growing fast", "no online presence"],
        negative_signals=[],
    )

    custom_icp = ICPConfig(
        company_size_ideal_score=40,
        website_missing_score=20,
        positive_signal_score=10,
        negative_signal_score=-20,
        qualification_threshold=50,
        disqualification_threshold=10,
        review_threshold=10,
    )

    result = score_lead(features, icp_config=custom_icp)

    assert result["score_breakdown"]["company_size"] == 40
    assert result["score_breakdown"]["website_presence"] == 20
    assert result["score_breakdown"]["description_signals"] == 30
    assert result["score"] == 90
    assert result["decision"] == "qualified"


def test_default_vs_custom_weights_change_score():
    features = LeadFeatures(
        company_size=12,
        company_size_fit=True,
        website_present=False,
        email_present=False,
        website_missing=True,
        email_missing=True,
        growth_signal=True,
        marketing_team_signal=False,
        positive_signals=["word of mouth", "growing fast", "no online presence"],
        negative_signals=[],
    )

    default_result = score_lead(features)
    custom_icp = ICPConfig(
        company_size_ideal_score=35,
        website_missing_score=15,
        positive_signal_score=5,
        negative_signal_score=-20,
    )
    custom_result = score_lead(features, icp_config=custom_icp)

    assert default_result["score"] == 100
    assert custom_result["score"] == 65
    assert custom_result["score"] != default_result["score"]
