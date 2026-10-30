import os
from typing import Any

import httpx
from dotenv import load_dotenv


class OpenRouterClient:
    """Client for interacting with OpenRouter chat completions."""

    API_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 60.0,
    ):
        load_dotenv(override=False)

        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model or os.getenv("OPENROUTER_MODEL")
        self.timeout = timeout

        if not self.api_key or not self.api_key.strip():
            raise ValueError("OPENROUTER_API_KEY is not configured")

        if not self.model or not self.model.strip():
            raise ValueError("OPENROUTER_MODEL is not configured")

        if timeout <= 0:
            raise ValueError("Timeout must be positive")

    def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Send a request and return the decoded OpenRouter response."""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self.API_URL,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()

        except httpx.HTTPStatusError as error:
            raise RuntimeError(
                f"OpenRouter returned HTTP {error.response.status_code}"
            ) from error

        except httpx.RequestError as error:
            raise RuntimeError(f"OpenRouter connection failed: {error}") from error

        try:
            data = response.json()
        except ValueError as error:
            raise RuntimeError("OpenRouter returned invalid JSON") from error

        if not isinstance(data, dict):
            raise TypeError("OpenRouter returned an invalid response")

        return data

    @staticmethod
    def _validate_generation_options(
        messages: list[dict],
        temperature: float,
        max_tokens: int,
    ) -> None:
        if not messages:
            raise ValueError("Messages cannot be empty")

        if not 0 <= temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2")

        if max_tokens < 1:
            raise ValueError("max_tokens must be positive")

    def generate(
        self,
        messages: list[dict],
        temperature: float = 0.2,
        max_tokens: int = 2000,
    ) -> str:
        """Generate a normal text response."""

        self._validate_generation_options(messages, temperature, max_tokens)

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        data = self._post(payload)

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise RuntimeError("OpenRouter returned an invalid response") from error

        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("OpenRouter returned an empty answer")

        return content.strip()

    def generate_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        temperature: float = 0.2,
        max_tokens: int = 2000,
    ) -> dict:
        """Generate a response that may contain a tool call."""

        self._validate_generation_options(messages, temperature, max_tokens)

        if not tools:
            raise ValueError("Tools cannot be empty")

        payload = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        data = self._post(payload)

        try:
            message = data["choices"][0]["message"]
        except (KeyError, IndexError, TypeError) as error:
            raise RuntimeError(
                "OpenRouter returned an invalid tool response"
            ) from error

        if not isinstance(message, dict):
            raise TypeError("OpenRouter returned an invalid message")

        return message
