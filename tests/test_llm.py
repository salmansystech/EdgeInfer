from types import SimpleNamespace
from unittest.mock import MagicMock
import pytest
import requests
from src import llm
from src.config import Config

def _ollama_response(status_code=200, json_data=None, text=""):
    response = MagicMock()
    response.status_code = status_code
    response.ok = status_code < 400
    response.json.return_value = json_data or {}
    response.text = text
    return response

@pytest.fixture
def use_ollama(monkeypatch):
    monkeypatch.setattr(Config, "LLM_PROVIDER", "ollama")
    post = MagicMock(return_value=_ollama_response(json_data={"message": {"content": "Hello"}, "done_reason": "stop"}))
    monkeypatch.setattr(llm.requests, "post", post)
    return post

def test_unknown_provider_raises(monkeypatch):
    monkeypatch.setattr(Config, "LLM_PROVIDER", "nope")

    with pytest.raises(llm.LLMError, match="Unknown LLM_PROVIDER"):
        llm.chat("system", [{"role": "user", "content": "hi"}])

def test_ollama_returns_message_content(use_ollama):
    assert llm.chat("system", [{"role": "user", "content": "hi"}]) == "Hello"

def test_ollama_sends_system_prompt_first(use_ollama):
    llm.chat("Be brief.", [{"role": "user", "content": "hi"}])

    assert use_ollama.call_args.args[0] == "http://ollama.test/api/chat"
    body = use_ollama.call_args.kwargs["json"]
    assert body["model"] == "test-model"
    assert body["stream"] is False
    assert body["messages"] == [
        {"role": "system", "content": "Be brief."},
        {"role": "user", "content": "hi"},
    ]

def test_ollama_sends_api_key_only_when_set(use_ollama, monkeypatch):
    llm.chat("system", [{"role": "user", "content": "hi"}])
    assert "Authorization" not in use_ollama.call_args.kwargs["headers"]

    monkeypatch.setattr(Config, "OLLAMA_API_KEY", "secret")
    llm.chat("system", [{"role": "user", "content": "hi"}])
    assert use_ollama.call_args.kwargs["headers"]["Authorization"] == "Bearer secret"

def test_ollama_marks_truncated_responses(use_ollama):
    use_ollama.return_value = _ollama_response(json_data={"message": {"content": "Partial"}, "done_reason": "length"})

    assert "[Response truncated" in llm.chat("system", [{"role": "user", "content": "hi"}])

def test_ollama_invalid_key(use_ollama):
    use_ollama.return_value = _ollama_response(status_code=401)

    with pytest.raises(llm.LLMError, match="OLLAMA_API_KEY"):
        llm.chat("system", [{"role": "user", "content": "hi"}])

def test_ollama_server_error(use_ollama):
    use_ollama.return_value = _ollama_response(status_code=500, text="boom")

    with pytest.raises(llm.LLMError, match="500"):
        llm.chat("system", [{"role": "user", "content": "hi"}])

def test_ollama_unreachable(use_ollama):
    use_ollama.side_effect = requests.ConnectionError()

    with pytest.raises(llm.LLMError, match="Could not reach Ollama"):
        llm.chat("system", [{"role": "user", "content": "hi"}])

def _claude_response(content, stop_reason="end_turn"):
    return SimpleNamespace(content=content, stop_reason=stop_reason)

@pytest.fixture
def claude_client(monkeypatch):
    client = MagicMock()
    monkeypatch.setattr(llm, "_get_client", lambda: client)
    return client

def test_claude_skips_thinking_blocks(claude_client):
    claude_client.beta.messages.create.return_value = _claude_response([
        SimpleNamespace(type="thinking", thinking=""),
        SimpleNamespace(type="text", text="Answer"),
    ])

    assert llm.chat("system", [{"role": "user", "content": "hi"}]) == "Answer"

def test_claude_uses_configured_model(claude_client, monkeypatch):
    monkeypatch.setattr(Config, "MODEL", "claude-test")
    claude_client.beta.messages.create.return_value = _claude_response([SimpleNamespace(type="text", text="ok")])

    llm.chat("system", [{"role": "user", "content": "hi"}])

    assert claude_client.beta.messages.create.call_args.kwargs["model"] == "claude-test"

def test_claude_refusal_raises(claude_client):
    claude_client.beta.messages.create.return_value = _claude_response([], stop_reason="refusal")

    with pytest.raises(llm.LLMError, match="declined"):
        llm.chat("system", [{"role": "user", "content": "hi"}])

def test_claude_marks_truncated_responses(claude_client):
    claude_client.beta.messages.create.return_value = _claude_response(
        [SimpleNamespace(type="text", text="Partial")], stop_reason="max_tokens")

    assert "[Response truncated" in llm.chat("system", [{"role": "user", "content": "hi"}])
