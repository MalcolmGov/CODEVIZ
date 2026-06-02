"""
Ollama LLM service.

Real integration with a local Ollama server (https://ollama.com), used to power
CodeViz's natural-language code Q&A. Designed to degrade gracefully: if Ollama
is not running or the model is missing, callers can fall back to the deterministic
keyword answer path.

Configuration (environment variables):
    OLLAMA_BASE_URL   Base URL of the Ollama server (default http://localhost:11434)
    OLLAMA_MODEL      Model name to use (default 'mistral')
    OLLAMA_TIMEOUT    Per-request timeout in seconds (default 60)
    ENABLE_LLM_CHAT   Set to '0'/'false' to disable LLM answers entirely
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional

import requests

DEFAULT_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "mistral"
DEFAULT_TIMEOUT = 60.0


class OllamaError(Exception):
    """Raised when an Ollama request fails."""


def _base_url() -> str:
    return os.getenv("OLLAMA_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def _model() -> str:
    return os.getenv("OLLAMA_MODEL", DEFAULT_MODEL)


def _timeout() -> float:
    try:
        return float(os.getenv("OLLAMA_TIMEOUT", str(DEFAULT_TIMEOUT)))
    except (TypeError, ValueError):
        return DEFAULT_TIMEOUT


def llm_chat_enabled() -> bool:
    """Whether LLM-backed chat is enabled via configuration."""
    return os.getenv("ENABLE_LLM_CHAT", "1").strip().lower() not in ("0", "false", "no")


class OllamaClient:
    """Thin synchronous client for the Ollama HTTP API."""

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None,
                 timeout: Optional[float] = None):
        self.base_url = (base_url or _base_url()).rstrip("/")
        self.model = model or _model()
        self.timeout = timeout if timeout is not None else _timeout()

    # -- introspection ---------------------------------------------------- #

    def list_models(self) -> List[str]:
        """Return installed model names. Raises OllamaError if unreachable."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=min(self.timeout, 5))
            resp.raise_for_status()
            return [m.get("name", "") for m in resp.json().get("models", [])]
        except requests.RequestException as e:
            raise OllamaError(f"Ollama unreachable at {self.base_url}: {e}") from e

    def is_available(self) -> bool:
        """True if the Ollama server responds (model may still need pulling)."""
        try:
            self.list_models()
            return True
        except OllamaError:
            return False

    def has_model(self) -> bool:
        """True if the configured model is installed on the server."""
        try:
            names = self.list_models()
        except OllamaError:
            return False
        # Ollama lists models as 'name:tag'; match on the base name too.
        return any(n == self.model or n.split(":")[0] == self.model.split(":")[0]
                   for n in names)

    # -- generation ------------------------------------------------------- #

    def generate(self, prompt: str, system: Optional[str] = None,
                 temperature: float = 0.2) -> str:
        """Single-prompt completion via /api/generate (non-streaming)."""
        payload: Dict = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if system:
            payload["system"] = system
        return self._post("/api/generate", payload, key="response")

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
        """Multi-turn completion via /api/chat (non-streaming).

        Args:
            messages: list of {'role': 'system'|'user'|'assistant', 'content': str}.
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        try:
            resp = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            raise OllamaError(f"Ollama chat request failed: {e}") from e
        content = (data.get("message") or {}).get("content", "").strip()
        if not content:
            raise OllamaError("Ollama returned an empty response")
        return content

    def _post(self, path: str, payload: Dict, key: str) -> str:
        try:
            resp = requests.post(f"{self.base_url}{path}", json=payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            raise OllamaError(f"Ollama request to {path} failed: {e}") from e
        content = str(data.get(key, "")).strip()
        if not content:
            raise OllamaError("Ollama returned an empty response")
        return content


# --------------------------------------------------------------------------- #
# High-level helper used by the chat layer
# --------------------------------------------------------------------------- #

SYSTEM_PROMPT = """You are CodeViz, an expert code-analysis assistant. \
Answer the user's question about THEIR repository using only the context provided \
below. The context is the result of a static scan: file structure, detected APIs, \
classes, functions, models, dependencies, and tech stack.

Guidelines:
- Be concise and use Markdown (short headers, bullet lists, code spans).
- Ground every claim in the provided context; cite file paths when relevant.
- For security questions (e.g. SQL injection, auth gaps, secrets), reason about \
LIKELY risks from the detected frameworks, endpoints, and patterns. Be explicit \
that this is a heuristic assessment and that confirming requires source review.
- If the context lacks the information to answer, say so plainly and suggest what \
to scan or which CodeViz tool to use (security scan, scoring, compliance).
- Never invent files, endpoints, or findings that are not in the context."""


def build_messages(question: str, grounding: str,
                   history: Optional[List[Dict[str, str]]] = None
                   ) -> List[Dict[str, str]]:
    """Assemble the chat message list: system + optional history + grounded question."""
    messages: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        # Only carry prior user/assistant turns (not system), capped to recent context.
        for turn in history[-6:]:
            role = turn.get("role")
            content = turn.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})
    user_content = (
        f"Repository context:\n\n{grounding}\n\n"
        f"---\n\nQuestion: {question}"
    )
    messages.append({"role": "user", "content": user_content})
    return messages


def answer_question(question: str, grounding: str,
                    history: Optional[List[Dict[str, str]]] = None,
                    client: Optional[OllamaClient] = None) -> str:
    """Answer a code question with the LLM, grounded in scan context.

    Raises OllamaError if LLM chat is disabled or Ollama is unavailable, so the
    caller can fall back to the deterministic answer path.
    """
    if not llm_chat_enabled():
        raise OllamaError("LLM chat is disabled (ENABLE_LLM_CHAT=0)")
    client = client or OllamaClient()
    if not client.is_available():
        raise OllamaError(f"Ollama server not reachable at {client.base_url}")
    return client.chat(build_messages(question, grounding, history))
