from __future__ import annotations
import json
from typing import Any
from google import genai
from google.genai import types
from utils.config import AppConfig


class LLMUnavailableError(RuntimeError):
    pass


class LLMInvocationError(RuntimeError):
    pass


class LLMClient:
    def __init__(self, config: AppConfig):
        self.config = config
        self.client = genai.Client(api_key=config.gemini_api_key) if config.llm_enabled else None

    @property
    def enabled(self) -> bool:
        return self.client is not None

    def json_completion(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        if not self.client:
            raise LLMUnavailableError("GEMINI_API_KEY is not set")
        try:
            response = self.client.models.generate_content(
                model=self.config.gemini_model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=self.config.gemini_temperature,
                    response_mime_type="application/json",
                ),
            )
            content = response.text.strip()
            content = content.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise LLMInvocationError(f"Invalid JSON from Gemini: {e}")
        except Exception as e:
            raise LLMInvocationError(str(e))
