from typing import List, Dict
import anthropic
from src.config import Config

class LLMError(RuntimeError):
    """Raised when Claude cannot produce a usable answer"""

_client = None

def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client

def chat(system: str, messages: List[Dict], max_tokens: int = 16000) -> str:
    """Send a conversation to Claude and return the text of the reply"""

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
