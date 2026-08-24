from __future__ import annotations

import json

from groq import Groq

from app.llm.client import LLMClient


class GroqLLMClient(LLMClient):
    def __init__(self, model: str, api_key: str, base_url=None):
        self.model = model
        self.api_key = api_key
        self.client = Groq(api_key=api_key, base_url=base_url)

    def __call__(self, prompt: str):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a lead qualification assistant. Return only valid JSON with "
                            "keys: decision, confidence, reasoning, positive_signals, negative_signals."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
                response_format={"type": "json_object"},
            )
        except Exception as exc:
            return {"error": "llm_failure", "message": str(exc)}

        content = response.choices[0].message.content
        if not content:
            return {"decision": "review", "confidence": 0.0, "reasoning": "No reason supplied by the model."}

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            return {"decision": "review", "confidence": 0.0, "reasoning": content}

        if not isinstance(parsed, dict):
            return {"decision": "review", "confidence": 0.0, "reasoning": str(parsed)}

        return parsed


def create_llm_client(model: str, api_key: str, base_url=None):
    if not api_key:
        return None
    return GroqLLMClient(model=model, api_key=api_key, base_url=base_url)
