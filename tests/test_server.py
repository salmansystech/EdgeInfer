import pytest
import server
from src.llm import LLMError

MODEL_INFO = {
    "name": "mobilenet",
    "type": "Neural Network",
    "framework": "TensorFlow",
    "totalParams": 3500000,
    "layers": 154,
    "sizeMb": 14.2,
    "inputShape": [224, 224, 3],
    "outputShape": [1000],
}

ENDPOINTS = ["/api/analyze", "/api/optimize", "/api/generate-code", "/api/benchmark"]

@pytest.fixture
def client():
    return server.app.test_client()

@pytest.fixture
def fake_llm(monkeypatch):
    """Replace the LLM call in every agent and record the prompts it receives"""
    prompts = []

    def fake_chat(system, messages, max_tokens=16000):
        prompts.append(messages[-1]["content"])
        return "LLM reply"

    for module in ("src.model_analyzer", "src.optimization_agent", "src.code_generator"):
        monkeypatch.setattr(f"{module}.chat", fake_chat)
    return prompts

def test_hardware_targets_lists_every_device(client):
    data = client.get("/api/hardware-targets").get_json()

    assert set(data) == set(server.Config.HARDWARE_TARGETS)
    assert data["esp32"] == {
        "key": "esp32", "name": "ESP32", "ramKb": 520, "flashKb": 4096, "cpuMhz": 240, "powerMw": 80,
    }

@pytest.mark.parametrize("path", ENDPOINTS)
def test_missing_model_info_is_rejected(client, path):
    response = client.post(path, json={"hardware": "esp32"})

    assert response.status_code == 400
    assert response.get_json()["error"] == "modelInfo is required"

@pytest.mark.parametrize("path", ENDPOINTS)
def test_unknown_hardware_is_rejected(client, path):
    response = client.post(path, json={"modelInfo": MODEL_INFO, "hardware": "toaster"})

    assert response.status_code == 400
    assert "Unknown hardware target" in response.get_json()["error"]

def test_unknown_level_is_rejected(client):
    response = client.post("/api/optimize", json={"modelInfo": MODEL_INFO, "hardware": "esp32", "level": "extreme"})

    assert response.status_code == 400
    assert "Unknown optimization level" in response.get_json()["error"]

def test_non_json_body_is_rejected(client):
    response = client.post("/api/benchmark", data="not json", content_type="text/plain")

    assert response.status_code == 400

def test_benchmark_by_level(client):
    conservative = client.post("/api/benchmark", json={"modelInfo": MODEL_INFO, "hardware": "esp32", "level": "conservative"}).get_json()
    balanced = client.post("/api/benchmark", json={"modelInfo": MODEL_INFO, "hardware": "esp32", "level": "balanced"}).get_json()

    assert conservative["sizeReductionPercent"] == pytest.approx(0)
    assert not conservative["deploymentReady"]
    assert balanced["optimizedSizeMb"] == pytest.approx(14.2 * 0.25 * 0.75)
    assert balanced["deploymentReady"]

def test_benchmark_with_explicit_techniques(client):
    data = client.post("/api/benchmark", json={
        "modelInfo": MODEL_INFO, "hardware": "esp32", "techniques": ["quantization"],
    }).get_json()

    assert data["sizeReductionPercent"] == pytest.approx(75)

def test_analyze_sends_model_details_to_llm(client, fake_llm):
    response = client.post("/api/analyze", json={"modelInfo": MODEL_INFO, "hardware": "esp32"})

    assert response.status_code == 200
    assert response.get_json() == {"analysis": "LLM reply", "metrics": MODEL_INFO, "targetHardware": "esp32"}
    assert "3,500,000" in fake_llm[0]
    assert "ESP32" in fake_llm[0]

def test_optimize_returns_plan_and_estimates(client, fake_llm):
    data = client.post("/api/optimize", json={"modelInfo": MODEL_INFO, "hardware": "esp32", "level": "balanced"}).get_json()

    assert data["plan"] == "LLM reply"
    assert data["techniques"] == ["quantization", "pruning", "fusion"]
    assert data["estimatedSizeReduction"] == pytest.approx(81.25)
    assert data["estimatedLatencyImprovement"] == pytest.approx(1 / (0.4 * 0.85 * 0.9))

def test_generate_code_includes_optimization_plan(client, fake_llm):
    response = client.post("/api/generate-code", json={
        "modelInfo": MODEL_INFO, "hardware": "esp32", "optimizationPlan": {"plan": "Quantize to INT8"},
    })

    assert response.get_json() == {"code": "LLM reply", "language": "C++", "hardware": "esp32"}
    assert "Quantize to INT8" in fake_llm[0]

def test_llm_failure_returns_502(client, monkeypatch):
    def failing_chat(system, messages, max_tokens=16000):
        raise LLMError("Invalid or missing OLLAMA_API_KEY")
    monkeypatch.setattr("src.model_analyzer.chat", failing_chat)

    response = client.post("/api/analyze", json={"modelInfo": MODEL_INFO, "hardware": "esp32"})

    assert response.status_code == 502
    assert response.get_json() == {"error": "Invalid or missing OLLAMA_API_KEY"}
