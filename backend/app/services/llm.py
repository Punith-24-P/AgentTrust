import json
import re
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import httpx
from app.config import settings


class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.0) -> str:
        pass

    @abstractmethod
    async def structured_generate(
        self, prompt: str, system_prompt: Optional[str] = None, schema_desc: Optional[str] = None
    ) -> Dict[str, Any]:
        pass

    @property
    @abstractmethod
    def is_mock(self) -> bool:
        pass


class OpenAICompatibleProvider(BaseLLMProvider):
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    @property
    def is_mock(self) -> bool:
        return False

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.0) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def structured_generate(
        self, prompt: str, system_prompt: Optional[str] = None, schema_desc: Optional[str] = None
    ) -> Dict[str, Any]:
        full_system = system_prompt or "You are an evaluation assistant. Return ONLY valid JSON."
        if schema_desc:
            full_system += f"\nRequired JSON schema:\n{schema_desc}"

        raw = await self.generate(prompt=prompt, system_prompt=full_system, temperature=0.0)

        # Clean markdown code blocks if present
        clean_text = raw.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()

        try:
            return json.loads(clean_text)
        except Exception:
            # Fallback regex extraction of outermost JSON object
            match = re.search(r"\{.*\}", clean_text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise ValueError(f"Failed to parse LLM response as JSON: {raw}")


class MockLLMProvider(BaseLLMProvider):
    """
    Deterministic evaluation judge and claim extractor for standalone/zero-dependency demo runs.
    Provides rigorous, predictable, explainable evaluation without external API keys.
    """

    @property
    def is_mock(self) -> bool:
        return True

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.0) -> str:
        return "Deterministic Mock Evaluation Output"

    async def structured_generate(
        self, prompt: str, system_prompt: Optional[str] = None, schema_desc: Optional[str] = None
    ) -> Dict[str, Any]:
        # Semantic correctness judge simulation
        if "semantic evaluation" in prompt.lower() or "judge" in prompt.lower():
            # Check for simulated error flags in prompt
            if "simulated_error" in prompt.lower() or "wrong" in prompt.lower():
                return {
                    "decision": "FAIL",
                    "semantic_score": 0.25,
                    "reason": "Agent answer contradicts expected legal conditions or deadlines."
                }
            return {
                "decision": "PASS",
                "semantic_score": 0.95,
                "reason": "Agent answer accurately preserves required statutory meaning and entities."
            }

        # Claim extraction simulation
        if "claim extraction" in prompt.lower() or "extract claims" in prompt.lower():
            return {
                "claims": [
                    {"claim": "Application must be submitted within 30 calendar days", "type": "deadline"},
                    {"claim": "Governing statutory rule is Section 4", "type": "section"}
                ]
            }

        return {"status": "SUCCESS", "message": "Parsed via deterministic fallback evaluator"}


def get_llm_provider() -> BaseLLMProvider:
    if settings.LLM_PROVIDER in ["openai", "openai_compatible"] and settings.LLM_API_KEY:
        return OpenAICompatibleProvider(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            model=settings.LLM_MODEL
        )
    return MockLLMProvider()
