import pytest
from src.benchmarker import Benchmarker, CYCLES_PER_LAYER
from src.config import Config

def expected_latency_ms(macs, layers, hardware, rate_key):
    hw = Config.HARDWARE_TARGETS[hardware]
    return (macs / hw[rate_key] + layers * CYCLES_PER_LAYER) / (hw["cpu_mhz"] * 1000)

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
    assert result.estimated_latency_ms == pytest.approx(
        expected_latency_ms(300_000_000, 154, "esp32", "int8_macs_per_cycle") * 0.85 * 0.9)
    assert result.accuracy_preservation == pytest.approx(97)

def test_technique_names_are_case_insensitive(model_info):
    lower = Benchmarker(model_info, "esp32").estimate_performance(["quantization"])
    upper = Benchmarker(model_info, "esp32").estimate_performance(["Quantization"])

    assert lower == upper

def test_float_latency_uses_device_float_throughput(model_info):
    result = Benchmarker(model_info, "arm_cortex_m7").estimate_performance([])

    assert result.estimated_latency_ms == pytest.approx(
        expected_latency_ms(300_000_000, 154, "arm_cortex_m7", "float_macs_per_cycle"))

def test_quantization_switches_to_int8_throughput(model_info):
    result = Benchmarker(model_info, "arm_cortex_m7").estimate_performance(["quantization"])

    assert result.estimated_latency_ms == pytest.approx(
        expected_latency_ms(300_000_000, 154, "arm_cortex_m7", "int8_macs_per_cycle"))

def test_int8_model_runs_at_int8_speed_without_quantization(model_info):
    model_info["precision"] = "INT8"
    result = Benchmarker(model_info, "esp32").estimate_performance([])

    assert result.estimated_latency_ms == pytest.approx(
        expected_latency_ms(300_000_000, 154, "esp32", "int8_macs_per_cycle"))

def test_latency_depends_on_device(model_info):
    latencies = {
        hardware: Benchmarker(model_info, hardware).estimate_performance(["quantization"]).estimated_latency_ms
        for hardware in Config.HARDWARE_TARGETS
    }

    # The ESP32-S3's vector unit beats the plain ESP32 at the same clock speed,
    # and the 125 MHz Cortex-M0+ in the RP2040 is the slowest
    assert latencies["esp32_s3"] < latencies["esp32"]
    assert max(latencies, key=latencies.get) == "raspberry_pi_pico"

def test_latency_scales_with_compute(model_info):
    small = dict(model_info, macs=1_000_000, layers=0)
    large = dict(model_info, macs=10_000_000, layers=0)

    small_latency = Benchmarker(small, "esp32").estimate_performance([]).estimated_latency_ms
    large_latency = Benchmarker(large, "esp32").estimate_performance([]).estimated_latency_ms

    assert large_latency == pytest.approx(small_latency * 10)

def test_latency_falls_back_to_parameter_count(model_info):
    del model_info["macs"]
    result = Benchmarker(model_info, "esp32").estimate_performance([])

    assert result.estimated_latency_ms == pytest.approx(
        expected_latency_ms(3_500_000, 154, "esp32", "float_macs_per_cycle"))

def test_model_larger_than_flash_is_not_deployment_ready(model_info):
    # 14.2 MB does not fit in the ESP32's 4 MB of Flash
    result = Benchmarker(model_info, "esp32").estimate_performance([])

    assert not result.memory_available
    assert not result.deployment_ready

def test_slow_model_is_not_deployment_ready(model_info):
    # Fits in Flash after optimization but takes over 5 seconds per inference on the ESP32
    result = Benchmarker(model_info, "esp32").estimate_performance(["quantization", "pruning"])

    assert result.memory_available
    assert result.estimated_latency_ms > 5000
    assert not result.deployment_ready

def test_small_fast_model_is_deployment_ready(model_info):
    small = dict(model_info, macs=7_000_000, layers=31, size_mb=0.3, precision="INT8")
    result = Benchmarker(small, "esp32_s3").estimate_performance([])

    assert result.memory_available
    assert result.deployment_ready

def test_fit_depends_on_device_flash(model_info):
    # 3.55 MB fits in the ESP32's 4 MB but not the Cortex-M4's 1 MB
    techniques = ["quantization"]

    assert Benchmarker(model_info, "esp32").estimate_performance(techniques).memory_available
    assert not Benchmarker(model_info, "arm_cortex_m4").estimate_performance(techniques).memory_available

def test_power_and_energy(model_info):
    result = Benchmarker(model_info, "esp32").estimate_performance([])

    # The ESP32 draws about 80 mW while running; energy is power x time
    assert result.estimated_power_mw == pytest.approx(80)
    assert result.energy_per_inference_mj == pytest.approx(80 * result.estimated_latency_ms / 1000)

def test_int8_model_is_not_quantized_again(model_info):
    model_info["precision"] = "INT8"
    result = Benchmarker(model_info, "esp32").estimate_performance(["quantization"])

    assert result.size_reduction_percent == pytest.approx(0)
    assert result.accuracy_preservation == pytest.approx(100)
