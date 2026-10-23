import io
from pathlib import Path
import pytest
import server
from src.llm import LLMError

MODEL_INFO = {
    "name": "mobilenet",
    "type": "Neural Network",
    "framework": "TensorFlow",
    "totalParams": 3500000,
    "macs": 300000000,
    "precision": "FLOAT32",
    "layers": 154,
    "sizeMb": 14.2,
    "inputShape": [224, 224, 3],
    "outputShape": [1000],
}

SAMPLE_MODEL = Path(__file__).parent.parent / "examples" / "sample-models" / "hello_world_int8.tflite"

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
    # A MobileNetV2-sized model fits in the ESP32's Flash after optimization but is too slow
    assert balanced["memoryAvailable"]
    assert balanced["estimatedLatencyMs"] > 5000
    assert not balanced["deploymentReady"]

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
    # Quantization moves to INT8 kernels; pruning and fusion cut a further 15% and 10%
    esp32 = server.Config.HARDWARE_TARGETS["esp32"]
    float_cycles = 300_000_000 / esp32["float_macs_per_cycle"] + 154 * 2000
    int8_cycles = 300_000_000 / esp32["int8_macs_per_cycle"] + 154 * 2000
    assert data["estimatedLatencyImprovement"] == pytest.approx(float_cycles / (int8_cycles * 0.85 * 0.9))

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

def _upload(client, data, filename):
    return client.post("/api/parse-model", data={"file": (io.BytesIO(data), filename)},
                       content_type="multipart/form-data")

def test_parse_model_returns_ui_format(client):
    response = _upload(client, SAMPLE_MODEL.read_bytes(), "hello_world_int8.tflite")
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "hello_world_int8"
    assert data["totalParams"] == 321
    assert data["macs"] == 288
    assert data["layers"] == 3
    assert data["precision"] == "INT8"
    assert data["inputShape"] == [1, 1]
    assert data["operators"] == {"FULLY_CONNECTED": 3}

def test_parse_model_requires_a_file(client):
    response = client.post("/api/parse-model", data={}, content_type="multipart/form-data")
    
    assert response.status_code == 400
    assert response.get_json()["error"] == "A model file is required"

def test_parse_model_rejects_unsupported_format(client):
    response = _upload(client, b"weights", "model.pt")
    
    assert response.status_code == 400
    assert "Unsupported model format" in response.get_json()["error"]

def test_parse_model_rejects_corrupted_file(client):
    response = _upload(client, b"not a model", "model.tflite")
    
    assert response.status_code == 400
    assert "Not a valid TensorFlow Lite file" in response.get_json()["error"]

def test_parsed_model_details_reach_the_llm(client, fake_llm):
    model_info = _upload(client, SAMPLE_MODEL.read_bytes(), "hello_world_int8.tflite").get_json()
    
    client.post("/api/analyze", json={"modelInfo": model_info, "hardware": "esp32"})
    
    assert "Weight Precision: INT8" in fake_llm[0]
    assert "Operators: FULLY_CONNECTED x3" in fake_llm[0]
    assert "Compute: 288 multiply-accumulates" in fake_llm[0]
