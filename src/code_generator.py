from anthropic import Anthropic
from typing import Dict, Any
from pathlib import Path

class CodeGenerationAgent:
    """Agent for generating optimized embedded code"""
    
    def __init__(self, optimization_plan: str, model_info: Dict, hardware: str):
        self.client = Anthropic()
        self.model = "claude-opus-4-1-20250805"
        self.optimization_plan = optimization_plan
        self.model_info = model_info
        self.hardware = hardware
        self.conversation_history = []
    
    def generate_inference_code(self) -> Dict:
        """Generate inference code for target platform"""
        
        prompt = self._build_code_generation_prompt()
        
        self.conversation_history.append({
            "role": "user",
            "content": prompt
        })
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=self._get_system_prompt(),
            messages=self.conversation_history
        )
        
        code = response.content[0].text
        self.conversation_history.append({
            "role": "assistant",
            "content": code
        })
        
        return {
            "inference_code": code,
            "language": "C++",
            "hardware": self.hardware
        }
    
    def generate_integration_example(self, use_case: str) -> str:
        """Generate integration example for specific use case"""
        
        prompt = f"""Based on the inference code generated, provide a complete integration example for this use case: {use_case}

Include:
1. Setup code
2. Input preprocessing
3. Inference execution
4. Output postprocessing
5. Full working example"""
        
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
        
        example = response.content[0].text
        self.conversation_history.append({
            "role": "assistant",
            "content": example
        })
        
        return example
    
    def _get_system_prompt(self) -> str:
        """System prompt for code generation"""
        return """You are an expert embedded systems programmer specializing in ML inference.

Your expertise:
- TensorFlow Lite Micro
- ONNX Runtime Lite
- ARM CMSIS-NN
- Hardware-specific optimizations
- Memory-efficient C/C++
- Real-time constraints
- Power-aware programming

Generate production-ready code with:
1. Clear documentation and comments
2. Memory-safe implementations
3. Error handling
4. Performance optimizations
5. Hardware-specific features
6. Integration examples
7. Deployment checklist"""
    
    def _build_code_generation_prompt(self) -> str:
        """Build code generation prompt"""
        from src.config import Config
        
        hw_specs = Config.HARDWARE_TARGETS.get(self.hardware, {})
        
        return f"""Generate optimized C++ inference code for edge deployment:

MODEL INFORMATION:
- Type: {self.model_info.get('type', 'Unknown')}
- Input: {self.model_info.get('input_shape', 'Unknown')}
- Output: {self.model_info.get('output_shape', 'Unknown')}
- Framework: {self.model_info.get('framework', 'Unknown')}

TARGET HARDWARE: {hw_specs.get('name', 'Unknown')}
- Platform: {hw_specs.get('platform', 'Unknown')}
- RAM: {hw_specs.get('ram_kb', 0)} KB
- Flash: {hw_specs.get('flash_kb', 0)} KB

OPTIMIZATION PLAN:
{self.optimization_plan}

Generate:
1. Complete inference engine code
2. Input/output handling
3. Memory management
4. Optimized tensor operations
5. Hardware-specific optimizations
6. Error handling
7. Performance profiling hooks
8. Deployment guide

Code should be:
- Production-ready
- Well-commented
- Memory-efficient
- Hardware-optimized"""
