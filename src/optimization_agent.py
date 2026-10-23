from typing import Dict, List, Any
from dataclasses import dataclass
from src.llm import chat
from src.model_parser import format_operators

@dataclass
class OptimizationStrategy:
    """Optimization strategy"""
    name: str
    technique: str
    size_reduction: float
    latency_improvement: float
    accuracy_loss: float
    complexity: str

class OptimizationAgent:
    """Agent for model optimization strategies"""
    
    def __init__(self, model_info: Dict, hardware_target: str):
        self.model_info = model_info
        self.hardware_target = hardware_target
        self.conversation_history = []
    
    def generate_optimization_plan(self, optimization_level: str) -> Dict:
        """Generate optimization strategy"""
        
        prompt = self._build_optimization_prompt(optimization_level)
        
        self.conversation_history.append({
            "role": "user",
            "content": prompt
        })
        
        strategy = chat(self._get_system_prompt(), self.conversation_history)
        self.conversation_history.append({
            "role": "assistant",
            "content": strategy
        })
        
        return {
            "optimization_plan": strategy,
            "level": optimization_level,
            "model_info": self.model_info,
            "conversation_active": True
        }
    
    def refine_optimization(self, feedback: str) -> str:
        """Refine optimization strategy based on feedback"""
        
        self.conversation_history.append({
            "role": "user",
            "content": f"Please refine the optimization strategy based on this feedback:\n{feedback}"
        })
        
        refined = chat(self._get_system_prompt(), self.conversation_history)
        self.conversation_history.append({
            "role": "assistant",
            "content": refined
        })
        
        return refined
    
    def _get_system_prompt(self) -> str:
        """System prompt for optimization"""
        return """You are an expert in neural network optimization for edge devices.

Expertise areas:
- Quantization (FP32→INT8, INT8, mixed-precision)
- Pruning (magnitude-based, structured)
- Knowledge distillation
- Layer fusion and graph optimization
- Hardware-specific optimization
- Accuracy-efficiency trade-offs

For each optimization strategy, provide:
1. Technique name and description
2. Expected size reduction percentage
3. Expected latency improvement
4. Estimated accuracy loss
5. Implementation complexity (Low/Medium/High)
6. When to use (which models/hardware)
7. Specific parameters and thresholds
8. Potential risks and mitigations"""
    
    def _build_optimization_prompt(self, level: str) -> str:
        """Build optimization prompt"""
        from src.config import Config
        
        hw_specs = Config.HARDWARE_TARGETS.get(self.hardware_target, {})
        level_config = Config.OPTIMIZATION_LEVELS.get(level, {})
        
        return f"""Generate optimization strategy for edge deployment:

MODEL:
- Type: {self.model_info.get('type', 'Unknown')}
- Size: {self.model_info.get('size_mb', 0):.2f} MB
- Parameters: {self.model_info.get('total_params', 0):,}
- Layers: {self.model_info.get('layers', 0)}
- Weight Precision: {self.model_info.get('precision', 'Unknown')}
- Operators: {format_operators(self.model_info.get('operators', {}))}

TARGET DEVICE: {hw_specs.get('name', 'Unknown')}
- RAM: {hw_specs.get('ram_kb', 0)} KB available
- Flash: {hw_specs.get('flash_kb', 0)} KB available
- CPU: {hw_specs.get('cpu_mhz', 0)} MHz

OPTIMIZATION LEVEL: {level}
- {level_config.get('description', 'Unknown')}
- Quantization: {level_config.get('quantization', False)}
- Pruning: {level_config.get('pruning', False)}
- Fusion: {level_config.get('fusion', False)}

Please provide:
1. Recommended optimization techniques in priority order
2. Estimated improvements for each technique
3. Combined optimization plan
4. Implementation steps
5. Trade-offs and risks
6. Expected final model size
7. Projected inference latency
8. Accuracy preservation estimate"""
