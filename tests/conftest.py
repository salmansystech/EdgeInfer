import pytest
from src.config import Config

@pytest.fixture(autouse=True)
def isolated_config(monkeypatch):
    """Ignore the developer's .env so tests never call a real LLM"""
    monkeypatch.setattr(Config, "LLM_PROVIDER", "anthropic")
    monkeypatch.setattr(Config, "OLLAMA_BASE_URL", "http://ollama.test")
    monkeypatch.setattr(Config, "OLLAMA_MODEL", "test-model")
    monkeypatch.setattr(Config, "OLLAMA_API_KEY", None)

@pytest.fixture
def model_info():
    """Model info in the snake_case format the agents and benchmarker use"""
    return {
        "name": "mobilenet",
        "type": "Neural Network",
        "framework": "TensorFlow",
        "total_params": 3_500_000,
        "layers": 154,
        "size_mb": 14.2,
        "input_shape": (224, 224, 3),
        "output_shape": (1000,),
    }
