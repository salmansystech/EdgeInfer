import pytest
from src.benchmarker import Benchmarker

def test_no_optimization_keeps_original_size(model_info):
    result = Benchmarker(model_info, "esp32").estimate_performance([])

    assert result.optimized_size_mb == pytest.approx(14.2)
    assert result.size_reduction_percent == pytest.approx(0)
    assert result.accuracy_preservation == pytest.approx(100)

def test_quantization_shrinks_model_to_a_quarter(model_info):
    result = Benchmarker(model_info, "esp32").estimate_performance(["quantization"])

    assert result.optimized_size_mb == pytest.approx(14.2 * 0.25)
    assert result.size_reduction_percent == pytest.approx(75)
    assert result.accuracy_preservation == pytest.approx(98)

def test_techniques_combine(model_info):
    result = Benchmarker(model_info, "esp32").estimate_performance(["quantization", "pruning", "fusion"])

    assert result.optimized_size_mb == pytest.approx(14.2 * 0.25 * 0.75)
    assert result.estimated_latency_ms == pytest.approx(10 * 0.4 * 0.85 * 0.9)
    assert result.accuracy_preservation == pytest.approx(97)

def test_technique_names_are_case_insensitive(model_info):
    lower = Benchmarker(model_info, "esp32").estimate_performance(["quantization"])
    upper = Benchmarker(model_info, "esp32").estimate_performance(["Quantization"])

    assert lower == upper

def test_model_larger_than_flash_is_not_deployment_ready(model_info):
    # 14.2 MB does not fit in the ESP32's 4 MB of Flash
    result = Benchmarker(model_info, "esp32").estimate_performance([])

    assert not result.memory_available
    assert not result.deployment_ready

def test_optimized_model_that_fits_is_deployment_ready(model_info):
    result = Benchmarker(model_info, "esp32").estimate_performance(["quantization", "pruning"])

    assert result.memory_available
    assert result.deployment_ready

def test_fit_depends_on_device_flash(model_info):
    # 3.55 MB fits in the ESP32's 4 MB but not the Cortex-M4's 1 MB
    techniques = ["quantization"]

    assert Benchmarker(model_info, "esp32").estimate_performance(techniques).memory_available
    assert not Benchmarker(model_info, "arm_cortex_m4").estimate_performance(techniques).memory_available

def test_power_includes_device_base_power(model_info):
    result = Benchmarker(model_info, "esp32").estimate_performance([])

    # ESP32 base power is 80 mW, plus 50 mW per 100 ms of latency
    assert result.estimated_power_mw == pytest.approx(80 + (10 / 100) * 50)

def test_int8_model_is_not_quantized_again(model_info):
    model_info["precision"] = "INT8"
    result = Benchmarker(model_info, "esp32").estimate_performance(["quantization"])
    
    assert result.size_reduction_percent == pytest.approx(0)
    assert result.accuracy_preservation == pytest.approx(100)
