from __future__ import annotations

from app.config.settings import settings
from app.ingestion.csv_loader import load_leads_from_csv
from app.llm.client import create_llm_client as _create_llm_client
from app.llm.groq_client import GroqLLMClient
from app.models.icp import DEFAULT_ICP_CONFIG, INDUSTRY_ALIASES, TARGET_INDUSTRIES
from app.models.lead import Lead, NormalizedLead
from app.models.qualification import Decision, LLMReviewResponse, PipelineStage, QualificationResult
from app.pipeline.features import extract_lead_features
from app.pipeline.industry_gate import industry_gate, normalize_industry, normalize_lead
from app.pipeline.orchestrator import llm_review, qualify_lead, run_qualification_pipeline
from app.pipeline.scoring import company_size_score, description_signal_score, score_lead, website_presence_score


GroqLLMProvider = GroqLLMClient


def analyze_lead(lead, llm_client=None):
    return qualify_lead(lead, llm_client=llm_client)


def create_llm_client(model=None, api_key=None, base_url=None):
    resolved_model = model or settings.groq_model
    resolved_api_key = api_key or settings.groq_api_key
    return _create_llm_client(model=resolved_model, api_key=resolved_api_key, base_url=base_url)


def openai_llm_client(model=None, api_key=None, base_url=None):
    return create_llm_client(model=model, api_key=api_key, base_url=base_url)


__all__ = [
    "TARGET_INDUSTRIES",
    "INDUSTRY_ALIASES",
    "DEFAULT_ICP_CONFIG",
    "Decision",
    "PipelineStage",
    "Lead",
    "NormalizedLead",
    "QualificationResult",
    "LLMReviewResponse",
    "normalize_industry",
    "normalize_lead",
    "company_size_score",
    "website_presence_score",
    "description_signal_score",
    "extract_lead_features",
    "score_lead",
    "industry_gate",
    "llm_review",
    "analyze_lead",
    "GroqLLMProvider",
    "create_llm_client",
    "openai_llm_client",
    "load_leads_from_csv",
    "run_qualification_pipeline",
]
