import click
from pathlib import Path
import json
from src.model_analyzer import ModelAnalysisAgent
from src.optimization_agent import OptimizationAgent
from src.code_generator import CodeGenerationAgent
from src.benchmarker import Benchmarker
from src.config import Config
from src.model_parser import parse_model_file, format_operators, ModelParseError

def _load_model(path: str) -> dict:
    """Read the model file and print a short summary"""
    try:
        model_info = parse_model_file(path)
    except ModelParseError as e:
        raise click.ClickException(str(e))
    
    size_mb = model_info['size_mb']
    size = f"{size_mb:.2f} MB" if size_mb >= 1 else f"{size_mb * 1024:.1f} KB"
    click.echo(f"📦 {model_info['name']} ({model_info['framework']}, {size})")
    click.echo(f"   Parameters: {model_info['total_params']:,} | MACs: {model_info['macs']:,} | Layers: {model_info['layers']} | Precision: {model_info['precision']}")
    click.echo(f"   Input: {model_info['input_shape']} | Output: {model_info['output_shape']}")
    click.echo(f"   Operators: {format_operators(model_info['operators'])}\n")
    return model_info

@click.group()
def cli():
    """EdgeInfer - AI Model Deployment for Edge Devices"""
    pass

@cli.command()
@click.option('--model', '-m', type=click.Path(exists=True), required=True, help='Model file (.tflite or .onnx)')
@click.option('--hardware', '-hw', default='esp32', type=click.Choice(list(Config.HARDWARE_TARGETS.keys())), help='Target hardware')
def analyze(model, hardware):
    """Analyze model for edge deployment"""
    
    click.echo(f"\n🔍 Analyzing model for {Config.HARDWARE_TARGETS[hardware]['name']}...\n")
    
    model_info = _load_model(model)
    
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
@click.option('--model', '-m', type=click.Path(exists=True), required=True, help='Model file (.tflite or .onnx)')
@click.option('--hardware', '-hw', default='esp32', type=click.Choice(list(Config.HARDWARE_TARGETS.keys())), help='Target hardware')
@click.option('--level', '-l', default='balanced', type=click.Choice(['conservative', 'balanced', 'aggressive']), help='Optimization level')
def optimize(model, hardware, level):
    """Generate optimization strategy"""
    
    click.echo(f"\n⚡ Generating {level} optimization strategy...\n")
    
    model_info = _load_model(model)
    
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
@click.option('--model', '-m', type=click.Path(exists=True), required=True, help='Model file (.tflite or .onnx)')
@click.option('--hardware', '-hw', default='esp32', type=click.Choice(list(Config.HARDWARE_TARGETS.keys())), help='Target hardware')
@click.option('--optimization', '-o', default='quantization,pruning,fusion', help='Comma-separated optimization techniques')
@click.option('--output', '-out', type=click.Path(), help='Output directory for generated code')
def generate(model, hardware, optimization, output):
    """Generate optimized inference code"""
    
    click.echo(f"\n💻 Generating inference code for {hardware}...\n")
    
    model_info = _load_model(model)
    
    techniques = [t.strip() for t in optimization.split(',')]
    
    codegen = CodeGenerationAgent("", model_info, hardware)
    code_result = codegen.generate_inference_code()
    
    click.echo(f"✅ Generated Code:\n{code_result['inference_code'][:500]}...\n")
    
    if output:
        Path(output).mkdir(parents=True, exist_ok=True)
        output_file = Path(output) / "inference.md"
        output_file.write_text(code_result['inference_code'], encoding="utf-8")
        click.echo(f"💾 Code saved to: {output_file}")

@cli.command()
@click.option('--model', '-m', type=click.Path(exists=True), required=True, help='Model file (.tflite or .onnx)')
@click.option('--hardware', '-hw', default='esp32', type=click.Choice(list(Config.HARDWARE_TARGETS.keys())), help='Target hardware')
@click.option('--optimization', '-o', default='quantization,pruning', help='Optimization techniques')
def benchmark(model, hardware, optimization):
    """Benchmark model performance"""
    
    click.echo(f"\n📊 Benchmarking model...\n")
    
    model_info = _load_model(model)
    
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
    click.echo(f"⚡ Latency: {result.estimated_latency_ms:.2f} ms")
    click.echo(f"🔋 Power: {result.estimated_power_mw:.1f} mW ({result.energy_per_inference_mj:.3f} mJ per inference)")
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
