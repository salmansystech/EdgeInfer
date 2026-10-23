from typing import List, Dict
import anthropic
import requests
from src.config import Config

class LLMError(RuntimeError):
    """Raised when the language model cannot produce a usable answer"""

_client = None

def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client

def chat(system: str, messages: List[Dict], max_tokens: int = 16000) -> str:
    """Send a conversation to the configured provider and return the text of the reply"""
    if Config.LLM_PROVIDER == "ollama":
        return _chat_ollama(system, messages)
    if Config.LLM_PROVIDER == "anthropic":
        return _chat_anthropic(system, messages, max_tokens)
    raise LLMError(f"Unknown LLM_PROVIDER: {Config.LLM_PROVIDER}")

def _chat_anthropic(system: str, messages: List[Dict], max_tokens: int) -> str:
    try:
        response = _get_client().beta.messages.create(
            model=Config.MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
            output_config={"effort": Config.EFFORT},
            # Retry on another model if the request is declined by a safety classifier
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
    except anthropic.AuthenticationError as e:
        raise LLMError("Invalid or missing ANTHROPIC_API_KEY") from e
    except anthropic.APIConnectionError as e:
        raise LLMError("Could not reach the Claude API") from e
    except anthropic.APIStatusError as e:
        raise LLMError(f"Claude API error ({e.status_code}): {e.message}") from e

    if response.stop_reason == "refusal":
        raise LLMError("Claude declined this request")

    # Responses can include thinking blocks, so only collect the text
    text = "".join(block.text for block in response.content if block.type == "text")
    if response.stop_reason == "max_tokens":
        text += "\n\n[Response truncated: max_tokens reached]"
    return text

def _chat_ollama(system: str, messages: List[Dict]) -> str:
    headers = {}
    if Config.OLLAMA_API_KEY:
        headers["Authorization"] = f"Bearer {Config.OLLAMA_API_KEY}"

    try:
        response = requests.post(
            f"{Config.OLLAMA_BASE_URL.rstrip('/')}/api/chat",
            headers=headers,
            json={
                "model": Config.OLLAMA_MODEL,
                "messages": [{"role": "system", "content": system}] + messages,
                "stream": False,
            },
            timeout=Config.TIMEOUT,
        )
    except requests.RequestException as e:
        raise LLMError(f"Could not reach Ollama at {Config.OLLAMA_BASE_URL}") from e

    if response.status_code == 401:
        raise LLMError("Invalid or missing OLLAMA_API_KEY")
    if not response.ok:
        raise LLMError(f"Ollama API error ({response.status_code}): {response.text[:200]}")

    data = response.json()
    text = data.get("message", {}).get("content", "")
    if data.get("done_reason") == "length":
        text += "\n\n[Response truncated: length limit reached]"
    return text
