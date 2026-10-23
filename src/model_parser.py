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

def _summary(total_params: int, operators: Counter, input_shape: List[int],
             output_shape: List[int], precision: str, framework: str) -> Dict:
    return {
        "framework": framework,
        "total_params": total_params,
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
        for s in range(model.SubgraphsLength()):
            subgraph = model.Subgraphs(s)
            for i in range(subgraph.OperatorsLength()):
                operators[_tflite_op_name(model, subgraph.Operators(i), op_names)] += 1
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

    return _summary(total_params, operators, input_shape, output_shape,
                    _main_precision(weight_counts), "TensorFlow Lite")

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
    return [int(d) for d in tensor.ShapeAsNumpy()] if tensor.ShapeLength() else []

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

    return _summary(sum(weight_counts.values()), operators, input_shape, output_shape,
                    _main_precision(weight_counts), "ONNX")

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
