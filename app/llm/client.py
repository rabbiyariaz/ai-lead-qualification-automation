from __future__ import annotations

from abc import ABC, abstractmethod


def create_llm_client(model: str, api_key: str, base_url=None):
    from app.llm.groq_client import GroqLLMClient

    if not api_key:
        return None
    return GroqLLMClient(model=model, api_key=api_key, base_url=base_url)


class LLMClient(ABC):
    @abstractmethod
    def __call__(self, prompt: str):
        raise NotImplementedError
