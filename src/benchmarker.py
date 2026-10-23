from dataclasses import dataclass
from typing import Dict, Any

# Interpreter overhead per layer (dispatch, tensor bookkeeping), in CPU cycles
CYCLES_PER_LAYER = 2000

@dataclass
class BenchmarkResult:
    """Benchmark results"""
    model_name: str
    hardware_target: str
    original_size_mb: float
    optimized_size_mb: float
    size_reduction_percent: float
    estimated_latency_ms: float
    estimated_power_mw: float
    energy_per_inference_mj: float
    accuracy_preservation: float
    memory_available: bool
    deployment_ready: bool

class Benchmarker:
    """Benchmark model performance on target hardware"""

    def __init__(self, model_info: Dict, hardware_target: str):
        self.model_info = model_info
        self.hardware_target = hardware_target

    def estimate_performance(self, optimization_techniques: list) -> BenchmarkResult:
        """Estimate performance after optimization"""

        from src.config import Config

        hw_specs = Config.HARDWARE_TARGETS.get(self.hardware_target, {})

        # Calculate optimizations
        size_reduction = 1.0
        latency_improvement = 1.0
        accuracy_loss = 0.0

        # Models stored as 8-bit integers are already quantized
        already_quantized = self.model_info.get("precision") in ("INT8", "UINT8")
        quantized = already_quantized

        for technique in optimization_techniques:
            if "quantization" in technique.lower():
                if already_quantized:
                    continue
                # Quantized models run on the faster INT8 kernels (see _estimate_latency)
                quantized = True
                size_reduction *= 0.25
                accuracy_loss += 0.02
            elif "pruning" in technique.lower():
                size_reduction *= 0.75
                latency_improvement *= 0.85
                accuracy_loss += 0.01
            elif "fusion" in technique.lower():
                latency_improvement *= 0.9

        original_size = self.model_info.get("size_mb", 0)
        optimized_size = original_size * size_reduction

        optimized_latency = self._estimate_latency(hw_specs, quantized) * latency_improvement

        # The CPU draws roughly its active power for the whole inference
        power = hw_specs.get("power_mw", 50)
        energy = power * optimized_latency / 1000

        mem_available = optimized_size < (hw_specs.get("flash_kb", 0) / 1024)

        return BenchmarkResult(
            model_name=self.model_info.get("name", "Unknown"),
            hardware_target=self.hardware_target,
            original_size_mb=original_size,
            optimized_size_mb=optimized_size,
            size_reduction_percent=(1 - size_reduction) * 100,
            estimated_latency_ms=optimized_latency,
            estimated_power_mw=power,
            energy_per_inference_mj=energy,
            accuracy_preservation=(1 - accuracy_loss) * 100,
            memory_available=mem_available,
            deployment_ready=mem_available and optimized_latency < 5000
        )

    def _estimate_latency(self, hw_specs: Dict, quantized: bool) -> float:
        """Estimate inference latency in milliseconds from the model's compute and the CPU's throughput"""
        # Without a MAC count, assume each parameter is used once (true for dense layers)
        macs = self.model_info.get("macs") or self.model_info.get("total_params", 0)
        layers = self.model_info.get("layers", 0)

        macs_per_cycle = hw_specs.get("int8_macs_per_cycle" if quantized else "float_macs_per_cycle", 0.1)
        cycles = macs / macs_per_cycle + layers * CYCLES_PER_LAYER
        return cycles / (hw_specs.get("cpu_mhz", 100) * 1000)
