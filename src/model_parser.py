from collections import Counter
from pathlib import Path
from typing import Dict, List
import math

class ModelParseError(ValueError):
    """Raised when a model file cannot be read"""

SUPPORTED_EXTENSIONS = (".tflite", ".onnx")

def parse_model_file(path: str) -> Dict:
    """Read model details from a .tflite or .onnx file on disk"""
    file_path = Path(path)
    return parse_model(file_path.read_bytes(), file_path.name)

def parse_model(data: bytes, filename: str) -> Dict:
    """Read model details from the contents of a .tflite or .onnx file"""
    extension = Path(filename).suffix.lower()
    if extension == ".tflite":
        info = _parse_tflite(data)
    elif extension == ".onnx":
        info = _parse_onnx(data)
    else:
        raise ModelParseError(
            f"Unsupported model format '{extension or filename}'. Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    info.update({
        "name": Path(filename).stem,
        "type": "Neural Network",
        "size_mb": len(data) / (1024 * 1024),
    })
    return info

def format_operators(operators: Dict) -> str:
    """Human-readable operator summary, e.g. "CONV_2D x12, RELU x12" """
    if not operators:
        return "Unknown"
    return ", ".join(f"{name} x{count}" for name, count in operators.items())

def _summary(total_params: int, macs: int, operators: Counter, input_shape: List[int],
             output_shape: List[int], precision: str, framework: str) -> Dict:
    return {
        "framework": framework,
        "total_params": total_params,
        "macs": macs,
        "layers": sum(operators.values()),
        "operators": dict(operators.most_common()),
        "input_shape": tuple(input_shape),
        "output_shape": tuple(output_shape),
        "precision": precision,
    }

def _parse_tflite(data: bytes) -> Dict:
    import tflite

    # TFLite flatbuffers carry the "TFL3" file identifier at bytes 4-8
    if len(data) < 8 or data[4:8] != b"TFL3":
        raise ModelParseError("Not a valid TensorFlow Lite file")

    try:
        model = tflite.Model.GetRootAsModel(data, 0)
        if model.SubgraphsLength() == 0:
            raise ModelParseError("TensorFlow Lite file contains no subgraphs")

        type_names = _enum_names(tflite.TensorType)
        op_names = _enum_names(tflite.BuiltinOperator)

        operators = Counter()
        weight_counts = Counter()
        total_params = 0
        macs = 0
        for s in range(model.SubgraphsLength()):
            subgraph = model.Subgraphs(s)
            for i in range(subgraph.OperatorsLength()):
                operator = subgraph.Operators(i)
                name = _tflite_op_name(model, operator, op_names)
                operators[name] += 1
                macs += _tflite_op_macs(subgraph, operator, name)
            for i in range(subgraph.TensorsLength()):
                tensor = subgraph.Tensors(i)
                if _tflite_has_data(model, tensor.Buffer()):
                    count = _element_count(_tflite_shape(tensor))
                    total_params += count
                    weight_counts[type_names.get(tensor.Type(), "UNKNOWN")] += count

        main = model.Subgraphs(0)
        input_shape = _tflite_shape(main.Tensors(int(main.Inputs(0)))) if main.InputsLength() else []
        output_shape = _tflite_shape(main.Tensors(int(main.Outputs(0)))) if main.OutputsLength() else []
    except ModelParseError:
        raise
    except Exception as e:
        raise ModelParseError("Could not read TensorFlow Lite file: it may be corrupted") from e

    return _summary(total_params, macs, operators, input_shape, output_shape,
                    _main_precision(weight_counts), "TensorFlow Lite")

def _tflite_op_macs(subgraph, operator, name: str) -> int:
    """Multiply-accumulates for one dense or convolution layer (0 for other layers)"""
    if name not in ("FULLY_CONNECTED", "CONV_2D", "DEPTHWISE_CONV_2D") or operator.InputsLength() < 2 or operator.OutputsLength() < 1:
        return 0
    weights = _tflite_shape(subgraph.Tensors(int(operator.Inputs(1))))
    outputs = _element_count(_tflite_shape(subgraph.Tensors(int(operator.Outputs(0)))))
    
    if name == "FULLY_CONNECTED" and len(weights) == 2:
        # Weights are [units, inputs]: each output value needs one MAC per input
        return outputs * weights[1]
    if name == "CONV_2D" and len(weights) == 4:
        # Filters are [out_channels, height, width, in_channels]
        return outputs * weights[1] * weights[2] * weights[3]
    if name == "DEPTHWISE_CONV_2D" and len(weights) == 4:
        # Filters are [1, height, width, channels]: one input channel per output
        return outputs * weights[1] * weights[2]
    return 0

def _tflite_op_name(model, operator, op_names: Dict) -> str:
    code = model.OperatorCodes(operator.OpcodeIndex())
    # Newer files store the operator in BuiltinCode; older ones in DeprecatedBuiltinCode
    builtin = max(code.BuiltinCode(), code.DeprecatedBuiltinCode())
    name = op_names.get(builtin, f"OP_{builtin}")
    if name == "CUSTOM" and code.CustomCode():
        name = f"CUSTOM:{code.CustomCode().decode()}"
    return name

def _tflite_has_data(model, buffer_index: int) -> bool:
    """Whether a tensor holds constant data (weights) rather than activations"""
    if buffer_index <= 0 or buffer_index >= model.BuffersLength():
        return False
    buffer = model.Buffers(buffer_index)
    # Files over 2 GB store weights outside the flatbuffer and reference them by offset
    return buffer.DataLength() > 0 or buffer.Size() > 0

def _tflite_shape(tensor) -> List[int]:
    # Dynamic dimensions (e.g. batch size) are stored as -1
    return [max(int(d), 1) for d in tensor.ShapeAsNumpy()] if tensor.ShapeLength() else []

def _parse_onnx(data: bytes) -> Dict:
    import onnx
    from google.protobuf.message import DecodeError

    try:
        model = onnx.load_model_from_string(data)
    except (DecodeError, ValueError) as e:
        raise ModelParseError("Could not read ONNX file: it may be corrupted") from e

    graph = model.graph
    if len(graph.node) == 0:
        raise ModelParseError("Not a valid ONNX model: no layers found")

    operators = Counter(node.op_type for node in graph.node)

    weight_counts = Counter()
    for initializer in graph.initializer:
        type_name = onnx.TensorProto.DataType.Name(initializer.data_type)
        weight_counts[type_name] += _element_count(initializer.dims)

    # Graph inputs can include initializers in older exports; real inputs are the rest
    initializer_names = {initializer.name for initializer in graph.initializer}
    inputs = [value for value in graph.input if value.name not in initializer_names]
    input_shape = _onnx_shape(inputs[0]) if inputs else []
    output_shape = _onnx_shape(graph.output[0]) if graph.output else []

    return _summary(sum(weight_counts.values()), _onnx_macs(model), operators, input_shape, output_shape,
                    _main_precision(weight_counts), "ONNX")

def _onnx_macs(model) -> int:
    """Multiply-accumulates for the model's dense, matrix multiply and convolution layers"""
    import onnx
    
    try:
        graph = onnx.shape_inference.infer_shapes(model).graph
    except Exception:
        # Shape inference can fail on unusual models; fall back to declared shapes
        graph = model.graph
    
    shapes = {initializer.name: list(initializer.dims) for initializer in graph.initializer}
    for value in list(graph.input) + list(graph.value_info) + list(graph.output):
        if value.type.tensor_type.HasField("shape"):
            # Treat dynamic dimensions (e.g. batch size) as 1
            shapes[value.name] = [max(d, 1) for d in _onnx_shape(value)]
    
    total = 0
    for node in graph.node:
        if node.op_type not in ("Conv", "Gemm", "MatMul") or len(node.input) < 2:
            continue
        a = shapes.get(node.input[0])
        b = shapes.get(node.input[1])
        output = shapes.get(node.output[0])
        if not a or not b or not output:
            continue
        
        if node.op_type == "Conv" and len(b) >= 3:
            # Weights are [out_channels, in_channels / groups, kernel...]
            total += _element_count(output) * _element_count(b[1:])
        elif node.op_type == "Gemm":
            trans_a = any(attr.name == "transA" and attr.i for attr in node.attribute)
            total += _element_count(output) * (a[0] if trans_a else a[-1])
        elif node.op_type == "MatMul":
            total += _element_count(output) * a[-1]
    return total

def _onnx_shape(value) -> List[int]:
    """Tensor shape, with -1 for dimensions that are dynamic (e.g. batch size)"""
    dims = value.type.tensor_type.shape.dim
    return [d.dim_value if d.HasField("dim_value") else -1 for d in dims]

def _element_count(shape) -> int:
    return math.prod(int(d) for d in shape) if len(shape) else 1

def _main_precision(weight_counts: Counter) -> str:
    """Data type holding the most weights, e.g. FLOAT32 or INT8"""
    if not weight_counts:
        return "UNKNOWN"
    name = weight_counts.most_common(1)[0][0]
    # ONNX names FLOAT32 as FLOAT
    return "FLOAT32" if name == "FLOAT" else name

def _enum_names(enum_class) -> Dict[int, str]:
    return {value: name for name, value in vars(enum_class).items() if not name.startswith("_")}
