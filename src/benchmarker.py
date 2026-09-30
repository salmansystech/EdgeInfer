from dataclasses import dataclass
from typing import Dict, Any
import math

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
        
        for technique in optimization_techniques:
            if "quantization" in technique.lower():
                size_reduction *= 0.25
                latency_improvement *= 0.4
                accuracy_loss += 0.02
            elif "pruning" in technique.lower():
                size_reduction *= 0.75
                latency_improvement *= 0.85
                accuracy_loss += 0.01
            elif "fusion" in technique.lower():
                latency_improvement *= 0.9
        
        original_size = self.model_info.get("size_mb", 0)
        optimized_size = original_size * size_reduction
        
        original_latency = self._estimate_original_latency()
        optimized_latency = original_latency * latency_improvement
        
        power_estimate = self._estimate_power(optimized_latency, hw_specs)
        
        mem_available = optimized_size < (hw_specs.get("flash_kb", 0) / 1024)
        
        return BenchmarkResult(
            model_name=self.model_info.get("name", "Unknown"),
            hardware_target=self.hardware_target,
            original_size_mb=original_size,
            optimized_size_mb=optimized_size,
            size_reduction_percent=(1 - size_reduction) * 100,
            estimated_latency_ms=optimized_latency,
            estimated_power_mw=power_estimate,
            accuracy_preservation=(1 - accuracy_loss) * 100,
            memory_available=mem_available,
            deployment_ready=mem_available and optimized_latency < 5000
        )
    
    def _estimate_original_latency(self) -> float:
        """Estimate original model latency"""
        params = self.model_info.get("total_params", 0)
        # Rough estimate: 1ms per 10M parameters on modern CPU
        return max(10, (params / 10_000_000))
    
    def _estimate_power(self, latency_ms: float, hw_specs: Dict) -> float:
        """Estimate power consumption"""
        base_power = hw_specs.get("power_mw", 50)
        compute_power = (latency_ms / 100) * 50
        return base_power + compute_power
