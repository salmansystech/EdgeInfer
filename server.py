"""Flask backend API for EdgeInfer UI"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from src.config import Config
from src.llm import LLMError
from src.model_analyzer import ModelAnalysisAgent
from src.optimization_agent import OptimizationAgent
from src.code_generator import CodeGenerationAgent
from src.benchmarker import Benchmarker

app = Flask(__name__)
CORS(app)

class BadRequest(ValueError):
    """Invalid request payload"""

@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return jsonify({'error': str(e)}), 400

@app.errorhandler(LLMError)
def handle_llm_error(e):
    return jsonify({'error': str(e)}), 502

def _to_model_info(data: dict) -> dict:
    """Convert the UI's camelCase model info into the agents' snake_case format"""
    info = data.get('modelInfo')
    if not isinstance(info, dict):
        raise BadRequest('modelInfo is required')
    return {
        'name': info.get('name', 'model'),
        'type': info.get('type', 'Neural Network'),
        'framework': info.get('framework', 'Unknown'),
        'total_params': info.get('totalParams', 0),
        'layers': info.get('layers', 0),
        'size_mb': info.get('sizeMb', 0),
        'input_shape': tuple(info.get('inputShape', [])),
        'output_shape': tuple(info.get('outputShape', [])),
    }

def _get_hardware(data: dict) -> str:
    hardware = data.get('hardware')
    if hardware not in Config.HARDWARE_TARGETS:
        raise BadRequest(f'Unknown hardware target: {hardware}')
    return hardware

def _get_level(data: dict) -> str:
    level = data.get('level', 'balanced')
    if level not in Config.OPTIMIZATION_LEVELS:
        raise BadRequest(f'Unknown optimization level: {level}')
    return level

def _techniques_for_level(level: str) -> list:
    """Techniques enabled by an optimization level"""
    level_config = Config.OPTIMIZATION_LEVELS[level]
    return [t for t in ('quantization', 'pruning', 'fusion') if level_config[t]]

def _benchmark(model_info: dict, hardware: str, techniques: list) -> dict:
    result = Benchmarker(model_info, hardware).estimate_performance(techniques)
    return {
        'originalSizeMb': result.original_size_mb,
        'optimizedSizeMb': result.optimized_size_mb,
        'sizeReductionPercent': result.size_reduction_percent,
        'estimatedLatencyMs': result.estimated_latency_ms,
        'estimatedPowerMw': result.estimated_power_mw,
        'accuracyPreservation': result.accuracy_preservation,
        'memoryAvailable': result.memory_available,
        'deploymentReady': result.deployment_ready,
    }

@app.route('/api/hardware-targets', methods=['GET'])
def get_hardware_targets():
    """Get available hardware targets"""
    targets = {}
    for key, specs in Config.HARDWARE_TARGETS.items():
        targets[key] = {
            'key': key,
            'name': specs['name'],
            'ramKb': specs['ram_kb'],
            'flashKb': specs['flash_kb'],
            'cpuMhz': specs['cpu_mhz'],
            'powerMw': specs['power_mw'],
        }
    return jsonify(targets)

@app.route('/api/analyze', methods=['POST'])
def analyze_model():
    """Analyze model for edge deployment"""
    data = request.get_json(silent=True) or {}
    model_info = _to_model_info(data)
    hardware = _get_hardware(data)

    result = ModelAnalysisAgent().analyze_model(model_info, hardware)
    return jsonify({
        'analysis': result['analysis'],
        'metrics': data['modelInfo'],
        'targetHardware': hardware
    })

@app.route('/api/optimize', methods=['POST'])
def optimize_model():
    """Generate optimization strategy"""
    data = request.get_json(silent=True) or {}
    model_info = _to_model_info(data)
    hardware = _get_hardware(data)
    level = _get_level(data)

    result = OptimizationAgent(model_info, hardware).generate_optimization_plan(level)
    techniques = _techniques_for_level(level)
    estimate = Benchmarker(model_info, hardware).estimate_performance(techniques)
    original_latency = Benchmarker(model_info, hardware).estimate_performance([]).estimated_latency_ms
    return jsonify({
        'plan': result['optimization_plan'],
        'level': level,
        'techniques': techniques,
        'estimatedSizeReduction': estimate.size_reduction_percent,
        'estimatedLatencyImprovement': original_latency / estimate.estimated_latency_ms
    })

@app.route('/api/generate-code', methods=['POST'])
def generate_code():
    """Generate inference code"""
    data = request.get_json(silent=True) or {}
    model_info = _to_model_info(data)
    hardware = _get_hardware(data)
    plan = (data.get('optimizationPlan') or {}).get('plan', '')

    result = CodeGenerationAgent(plan, model_info, hardware).generate_inference_code()
    return jsonify({
        'code': result['inference_code'],
        'language': result['language'],
        'hardware': hardware
    })

@app.route('/api/benchmark', methods=['POST'])
def benchmark():
    """Benchmark model performance"""
    data = request.get_json(silent=True) or {}
    model_info = _to_model_info(data)
    hardware = _get_hardware(data)
    if 'techniques' in data:
        techniques = data['techniques']
    else:
        techniques = _techniques_for_level(_get_level(data))

    return jsonify(_benchmark(model_info, hardware, techniques))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
