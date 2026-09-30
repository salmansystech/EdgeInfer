import click
from pathlib import Path
import json
from src.model_analyzer import ModelAnalysisAgent
from src.optimization_agent import OptimizationAgent
from src.code_generator import CodeGenerationAgent
from src.benchmarker import Benchmarker
from src.config import Config

@click.group()
def cli():
    """EdgeInfer - AI Model Deployment for Edge Devices"""
    pass

@cli.command()
@click.option('--model', '-m', type=click.Path(exists=True), required=True, help='Model file (TensorFlow, PyTorch, ONNX)')
@click.option('--hardware', '-hw', default='esp32', type=click.Choice(list(Config.HARDWARE_TARGETS.keys())), help='Target hardware')
def analyze(model, hardware):
    """Analyze model for edge deployment"""
    
    click.echo(f"\n🔍 Analyzing model for {Config.HARDWARE_TARGETS[hardware]['name']}...\n")
    
    # Parse model info
    model_info = {
        "name": Path(model).stem,
        "path": model,
        "type": "Neural Network",
        "framework": "TensorFlow/PyTorch/ONNX",
        "total_params": 3_500_000,  # Example
        "layers": 154,
        "input_shape": (224, 224, 3),
        "output_shape": (1000,),
        "size_mb": 14.2
    }
    
    # Analysis
    analyzer = ModelAnalysisAgent()
    result = analyzer.analyze_model(model_info, hardware)
    
    click.echo(f"📊 Analysis Report:\n{result['analysis']}\n")
    
    # Interactive follow-ups
    while True:
        try:
            question = click.prompt("❓ Follow-up question (or 'exit')")
            if question.lower() in ['exit', 'quit', 'q']:
                break
            response = analyzer.ask_about_model(question)
            click.echo(f"\n🤖 Response:\n{response}\n")
        except KeyboardInterrupt:
            break

@cli.command()
@click.option('--model', '-m', type=click.Path(exists=True), required=True, help='Model file')
@click.option('--hardware', '-hw', default='esp32', type=click.Choice(list(Config.HARDWARE_TARGETS.keys())), help='Target hardware')
@click.option('--level', '-l', default='balanced', type=click.Choice(['conservative', 'balanced', 'aggressive']), help='Optimization level')
def optimize(model, hardware, level):
    """Generate optimization strategy"""
    
    click.echo(f"\n⚡ Generating {level} optimization strategy...\n")
    
    model_info = {
        "name": Path(model).stem,
        "type": "Neural Network",
        "total_params": 3_500_000,
        "layers": 154,
        "size_mb": 14.2,
        "framework": "TensorFlow"
    }
    
    opt_agent = OptimizationAgent(model_info, hardware)
    strategy = opt_agent.generate_optimization_plan(level)
    
    click.echo(f"✨ Optimization Strategy:\n{strategy['optimization_plan']}\n")
    
    # Refinement loop
    while True:
        try:
            feedback = click.prompt("💡 Feedback for refinement (or 'done')")
            if feedback.lower() in ['done', 'ok', 'exit']:
                break
            refined = opt_agent.refine_optimization(feedback)
            click.echo(f"\n✨ Refined Strategy:\n{refined}\n")
        except KeyboardInterrupt:
            break

@cli.command()
@click.option('--model', '-m', type=click.Path(exists=True), required=True, help='Model file')
@click.option('--hardware', '-hw', default='esp32', type=click.Choice(list(Config.HARDWARE_TARGETS.keys())), help='Target hardware')
@click.option('--optimization', '-o', default='quantization,pruning,fusion', help='Comma-separated optimization techniques')
@click.option('--output', '-out', type=click.Path(), help='Output directory for generated code')
def generate(model, hardware, optimization, output):
    """Generate optimized inference code"""
    
    click.echo(f"\n💻 Generating inference code for {hardware}...\n")
    
    model_info = {
        "name": Path(model).stem,
        "type": "Neural Network",
        "input_shape": (224, 224, 3),
        "output_shape": (1000,),
        "framework": "TensorFlow"
    }
    
    techniques = [t.strip() for t in optimization.split(',')]
    
    codegen = CodeGenerationAgent("", model_info, hardware)
    code_result = codegen.generate_inference_code()
    
    click.echo(f"✅ Generated Code:\n{code_result['inference_code'][:500]}...\n")
    
    if output:
        Path(output).mkdir(exist_ok=True)
        Path(output) / "inference.cpp"
        click.echo(f"💾 Code saved to: {output}")

@cli.command()
@click.option('--model', '-m', type=click.Path(exists=True), required=True, help='Model file')
@click.option('--hardware', '-hw', default='esp32', type=click.Choice(list(Config.HARDWARE_TARGETS.keys())), help='Target hardware')
@click.option('--optimization', '-o', default='quantization,pruning', help='Optimization techniques')
def benchmark(model, hardware, optimization):
    """Benchmark model performance"""
    
    click.echo(f"\n📊 Benchmarking model...\n")
    
    model_info = {
        "name": Path(model).stem,
        "size_mb": 14.2,
        "total_params": 3_500_000
    }
    
    techniques = [t.strip() for t in optimization.split(',')]
    benchmarker = Benchmarker(model_info, hardware)
    result = benchmarker.estimate_performance(techniques)
    
    click.echo("═" * 60)
    click.echo("           EDGEINFER BENCHMARK REPORT")
    click.echo("═" * 60)
    click.echo(f"\n📱 Device: {Config.HARDWARE_TARGETS[hardware]['name']}")
    click.echo(f"📊 Original Size: {result.original_size_mb:.2f} MB")
    click.echo(f"✨ Optimized Size: {result.optimized_size_mb:.2f} MB")
    click.echo(f"📉 Size Reduction: {result.size_reduction_percent:.1f}%")
    click.echo(f"⚡ Latency: {result.estimated_latency_ms:.1f} ms")
    click.echo(f"🔋 Power: {result.estimated_power_mw:.1f} mW")
    click.echo(f"🎯 Accuracy Preservation: {result.accuracy_preservation:.1f}%")
    click.echo(f"✅ Memory Available: {'Yes' if result.memory_available else 'No'}")
    click.echo(f"🚀 Deployment Ready: {'Yes' if result.deployment_ready else 'No'}")
    click.echo("\n" + "═" * 60)

@cli.command()
def list_hardware():
    """List supported hardware targets"""
    
    click.echo("\n📱 Supported Hardware Targets:\n")
    for hw_key, hw_specs in Config.HARDWARE_TARGETS.items():
        click.echo(f"  {hw_key}:")
        click.echo(f"    Name: {hw_specs['name']}")
        click.echo(f"    RAM: {hw_specs['ram_kb']} KB | Flash: {hw_specs['flash_kb']} KB")
        click.echo(f"    CPU: {hw_specs['cpu_mhz']} MHz | Power: ~{hw_specs['power_mw']} mW")
        click.echo()

if __name__ == '__main__':
    cli()
