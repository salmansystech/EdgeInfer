from anthropic import Anthropic
from typing import Dict, Any
from dataclasses import dataclass
import json

@dataclass
class ModelMetrics:
    """Model metrics extracted"""
    model_type: str
    total_params: int
    layers: int
    input_shape: tuple
    output_shape: tuple
    model_size_mb: float
    estimated_flops: int
    estimated_inference_ms: float

class ModelAnalysisAgent:
    """Agent for analyzing ML models"""
    
    def __init__(self):
        self.client = Anthropic()
        self.model = "claude-opus-4-1-20250805"
        self.conversation_history = []
    
    def analyze_model(self, model_info: Dict[str, Any], target_hardware: str) -> Dict:
        """Analyze model for edge deployment"""
        
        prompt = self._build_analysis_prompt(model_info, target_hardware)
        
        self.conversation_history.append({
            "role": "user",
            "content": prompt
        })
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=self._get_system_prompt(),
            messages=self.conversation_history
        )
        
        analysis = response.content[0].text
        self.conversation_history.append({
            "role": "assistant",
            "content": analysis
        })
        
        return {
            "analysis": analysis,
            "metrics": model_info,
            "target_hardware": target_hardware,
            "conversation_active": True
        }
    
    def ask_about_model(self, question: str) -> str:
        """Ask follow-up questions about model"""
        
        self.conversation_history.append({
            "role": "user",
            "content": question
        })
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=self._get_system_prompt(),
            messages=self.conversation_history
        )
        
        answer = response.content[0].text
        self.conversation_history.append({
            "role": "assistant",
            "content": answer
        })
        
        return answer
    
    def _get_system_prompt(self) -> str:
        """System prompt for model analysis"""
        return """You are an expert in deploying ML models to edge devices and microcontrollers.
        
Your expertise includes:
- Model architecture analysis
- Memory footprint calculations
- Latency estimation
- Hardware compatibility assessment
- Optimization strategy recommendations
- Power consumption analysis
- Trade-off analysis between accuracy and efficiency

For each model, provide:
1. Detailed architecture breakdown
2. Memory requirements (RAM, Flash)
3. Estimated inference latency
4. Computational complexity (FLOPs)
5. Power consumption estimates
6. Hardware compatibility assessment
7. Optimization recommendations prioritized by impact
8. Deployment feasibility score"""
    
    def _build_analysis_prompt(self, model_info: Dict, hardware: str) -> str:
        """Build analysis prompt"""
        from src.config import Config
        
        hw_specs = Config.HARDWARE_TARGETS.get(hardware, {})
        
        return f"""Analyze this ML model for deployment on embedded hardware:

MODEL INFORMATION:
- Type: {model_info.get('type', 'Unknown')}
- Total Parameters: {model_info.get('total_params', 0):,}
- Layers: {model_info.get('layers', 0)}
- Input Shape: {model_info.get('input_shape', 'Unknown')}
- Output Shape: {model_info.get('output_shape', 'Unknown')}
- Model Size: {model_info.get('size_mb', 0):.2f} MB
- Framework: {model_info.get('framework', 'Unknown')}

TARGET HARDWARE: {hw_specs.get('name', 'Unknown')}
- RAM: {hw_specs.get('ram_kb', 0)} KB
- Flash: {hw_specs.get('flash_kb', 0)} KB
- CPU: {hw_specs.get('cpu_mhz', 0)} MHz
- Platform: {hw_specs.get('platform', 'Unknown')}

Please provide:
1. Detailed feasibility assessment
2. Memory requirement breakdown
3. Estimated inference time
4. Identified optimization opportunities
5. Recommended optimization strategies
6. Deployment feasibility (Yes/No/With modifications)
7. Expected improvements after optimization"""
