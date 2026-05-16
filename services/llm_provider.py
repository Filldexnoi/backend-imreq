"""
LLM Provider abstraction.

Switch providers via environment variables:
  LLM_PROVIDER=openai   (default)  → needs OPENAI_API_KEY,  optional OPENAI_MODEL
  LLM_PROVIDER=gemini               → needs GEMINI_API_KEY,  optional GEMINI_MODEL
"""
import os
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def generate_json(self, prompt: str) -> str:
        """Send prompt, return raw response text (expected JSON)."""


class OpenAIProvider(LLMProvider):
    DEFAULT_MODEL = "gpt-5.4"

    def __init__(self):
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self._client = OpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", self.DEFAULT_MODEL)

    def generate_json(self, prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content.strip()


class GeminiProvider(LLMProvider):
    DEFAULT_MODEL = "gemini-3.1-pro-preview"

    def __init__(self):
        from google import genai
        from google.genai import types as genai_types
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        self._client = genai.Client(api_key=api_key)
        self._types = genai_types
        self.model = os.getenv("GEMINI_MODEL", self.DEFAULT_MODEL)

    def generate_json(self, prompt: str) -> str:
        response = self._client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=self._types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
            ),
        )
        return response.text.strip()


def get_llm_provider() -> LLMProvider:
    """Factory: read LLM_PROVIDER env var and return the matching provider."""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider == "gemini":
        return GeminiProvider()
    return OpenAIProvider()
