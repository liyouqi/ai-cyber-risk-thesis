"""Minimal OpenAI-compatible JSON client."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import requests
from dotenv import dotenv_values


class JsonLlm(Protocol):
    model: str

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]: ...


@dataclass(frozen=True)
class LlmConfig:
    api_key: str
    base_url: str
    model: str
    thinking_mode: str | None = None
    timeout_seconds: int = 120

    @classmethod
    def from_env_file(cls, path: str | Path = ".env") -> "LlmConfig":
        values = dotenv_values(path)
        required = ("PRIVATE_AI_API_KEY", "PRIVATE_AI_BASE_URL", "PRIVATE_AI_MODEL")
        missing = [name for name in required if not values.get(name)]
        if missing:
            raise RuntimeError("Missing LLM configuration: " + ", ".join(missing))
        return cls(
            api_key=str(values["PRIVATE_AI_API_KEY"]),
            base_url=str(values["PRIVATE_AI_BASE_URL"]).rstrip("/"),
            model=str(values["PRIVATE_AI_MODEL"]),
            thinking_mode=str(values["PRIVATE_AI_THINKING_MODE"])
            if values.get("PRIVATE_AI_THINKING_MODE")
            else None,
        )

    @property
    def endpoint(self) -> str:
        if self.base_url.endswith("/chat/completions"):
            return self.base_url
        return f"{self.base_url}/chat/completions"


class OpenAiCompatibleLlm:
    def __init__(self, config: LlmConfig) -> None:
        self._config = config
        self.model = config.model

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        if self._config.thinking_mode:
            payload["thinking"] = {"type": self._config.thinking_mode}
        response = requests.post(
            self._config.endpoint,
            headers={
                "Authorization": f"Bearer {self._config.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=self._config.timeout_seconds,
        )
        response.raise_for_status()
        body = response.json()
        content = body["choices"][0]["message"]["content"]
        if not isinstance(content, str):
            raise RuntimeError("LLM response did not contain text content")
        content = content.strip()
        if content.startswith("```"):
            lines = content.splitlines()
            content = "\n".join(lines[1:-1])
            if content.lstrip().startswith("json"):
                content = content.lstrip()[4:].lstrip()
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise RuntimeError("LLM response must be a JSON object")
        return parsed
