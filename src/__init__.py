"""EdgeInfer - AI Model Deployment for Edge Devices"""

__version__ = "1.0.0"
__author__ = "Salman Khan"

from src.model_analyzer import ModelAnalysisAgent
from src.optimization_agent import OptimizationAgent
from src.code_generator import CodeGenerationAgent
from src.benchmarker import Benchmarker

__all__ = [
    "ModelAnalysisAgent",
    "OptimizationAgent",
    "CodeGenerationAgent",
    "Benchmarker"
]
