from __future__ import annotations

from app.models.qualification import LLMReviewResponse


def validate_llm_response(payload):
    if not isinstance(payload, dict):
        raise ValueError("LLM response must be a dictionary.")

    try:
        return LLMReviewResponse.model_validate(payload)
    except Exception as exc:
        raise ValueError(f"Malformed LLM response: {exc}") from exc


def safe_llm_result(payload):
    try:
        validated = validate_llm_response(payload)
        return {
            "capacity": validated.capacity.value,
            "growth_intent": validated.growth_intent.value,
            "customer_acquisition_need": validated.customer_acquisition_need.value,
            "ambiguity": validated.ambiguity,
            "reasoning": validated.reasoning,
            "positive_signals": validated.positive_signals,
            "negative_signals": validated.negative_signals,
        }
    except ValueError:
        return {
            "capacity": "unknown",
            "growth_intent": "unknown",
            "customer_acquisition_need": "unknown",
            "ambiguity": True,
            "reasoning": "Malformed model response; manual review required.",
            "positive_signals": [],
            "negative_signals": [],
        }