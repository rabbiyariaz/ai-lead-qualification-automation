from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Decision(str, Enum):
    QUALIFIED = "qualified"
    DISQUALIFIED = "disqualified"
    REVIEW = "review"


class Capacity(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    UNKNOWN = "unknown"


class GrowthIntent(str, Enum):
    SEEKING_GROWTH = "seeking_growth"
    SATURATED = "saturated"
    STABLE = "stable"
    UNKNOWN = "unknown"


class AcquisitionNeed(str, Enum):
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    UNKNOWN = "unknown"


class FailureType(str, Enum):
    LLM_TIMEOUT = "llm_timeout"
    LLM_API_ERROR = "llm_api_error"
    LLM_INVALID_RESPONSE = "llm_invalid_response"
    LLM_EMPTY_RESPONSE = "llm_empty_response"


class PipelineStage(str, Enum):
    INDUSTRY_GATE = "industry_gate"
    SCORING = "scoring"
    LLM_REVIEW = "llm_review"


class QualificationResult(BaseModel):
    lead_id: str | None = None
    decision: Decision = Decision.REVIEW
    score: int = 0
    stage: PipelineStage | str = PipelineStage.SCORING
    reason: str = ""
    llm_reasoning: str = ""
    failure_type: FailureType | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    score_breakdown: dict[str, int] | None = None
    positive_signals: list[str] = Field(default_factory=list)
    negative_signals: list[str] = Field(default_factory=list)
    ambiguity_signals: list[str] = Field(default_factory=list)


class LLMReviewResponse(BaseModel):
    capacity: Capacity
    growth_intent: GrowthIntent
    customer_acquisition_need: AcquisitionNeed
    ambiguity: bool
    reasoning: str
    positive_signals: list[str] = Field(default_factory=list)
    negative_signals: list[str] = Field(default_factory=list)
    ambiguity_signals: list[str] = Field(default_factory=list)