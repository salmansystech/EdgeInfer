from pathlib import Path
import numpy as np
import pytest
from onnx import TensorProto, helper, numpy_helper
from src.model_parser import parse_model, parse_model_file, format_operators, ModelParseError

SAMPLES = Path(__file__).parent.parent / "examples" / "sample-models"

def make_onnx_cnn(weight_type=np.float32) -> bytes:
    """A small Conv + ReLU model with a dynamic batch dimension"""
    weights = numpy_helper.from_array(np.zeros((8, 3, 3, 3), weight_type), "W")
    bias = numpy_helper.from_array(np.zeros((8,), weight_type), "B")
    graph = helper.make_graph(
        [helper.make_node("Conv", ["x", "W", "B"], ["c"]), helper.make_node("Relu", ["c"], ["y"])],
        "cnn",
        [helper.make_tensor_value_info("x", TensorProto.FLOAT, ["batch", 3, 32, 32])],
        [helper.make_tensor_value_info("y", TensorProto.FLOAT, ["batch", 8, 30, 30])],
        [weights, bias],
    )
    return helper.make_model(graph).SerializeToString()

def test_tflite_float_model():
    info = parse_model_file(SAMPLES / "hello_world_float.tflite")

    # Three dense layers: 1->16, 16->16, 16->1 (weights + biases)
    assert info["total_params"] == (16 + 16) + (256 + 16) + (16 + 1)
    assert info["macs"] == 16 + 256 + 16
    assert info["layers"] == 3
    assert info["operators"] == {"FULLY_CONNECTED": 3}
    assert info["input_shape"] == (1, 1)
    assert info["output_shape"] == (1, 1)
    assert info["precision"] == "FLOAT32"
    assert info["framework"] == "TensorFlow Lite"
    assert info["name"] == "hello_world_float"

def test_tflite_quantized_model():
    info = parse_model_file(SAMPLES / "hello_world_int8.tflite")

    assert info["total_params"] == 321
    assert info["precision"] == "INT8"

def test_size_comes_from_file():
    path = SAMPLES / "hello_world_int8.tflite"

    assert parse_model_file(path)["size_mb"] == pytest.approx(path.stat().st_size / (1024 * 1024))

def test_onnx_model():
    info = parse_model(make_onnx_cnn(), "detector.onnx")

    assert info["total_params"] == 8 * 3 * 3 * 3 + 8
    # Each of the 8 x 30 x 30 outputs needs 3 x 3 x 3 MACs
    assert info["macs"] == 8 * 30 * 30 * 27
    assert info["layers"] == 2
    assert info["operators"] == {"Conv": 1, "Relu": 1}
    assert info["input_shape"] == (-1, 3, 32, 32)
    assert info["output_shape"] == (-1, 8, 30, 30)
    assert info["precision"] == "FLOAT32"
    assert info["framework"] == "ONNX"
    assert info["name"] == "detector"

def test_onnx_quantized_weights():
    assert parse_model(make_onnx_cnn(np.int8), "q.onnx")["precision"] == "INT8"

def test_extension_is_case_insensitive():
    assert parse_model(make_onnx_cnn(), "MODEL.ONNX")["framework"] == "ONNX"

@pytest.mark.parametrize("filename", ["model.pt", "model.h5", "model.pb", "model"])
def test_unsupported_format(filename):
    with pytest.raises(ModelParseError, match="Unsupported model format"):
        parse_model(b"data", filename)

@pytest.mark.parametrize("data", [b"", b"not a model", b"1234TFL3" + b"\x00" * 4])
def test_invalid_tflite(data):
    with pytest.raises(ModelParseError):
        parse_model(data, "model.tflite")

@pytest.mark.parametrize("data", [b"", b"\x00\x01garbage\xff\xfe"])
def test_invalid_onnx(data):
    with pytest.raises(ModelParseError):
        parse_model(data, "model.onnx")

def test_format_operators():
    assert format_operators({"CONV_2D": 12, "RELU": 3}) == "CONV_2D x12, RELU x3"
    assert format_operators({}) == "Unknown"

def test_onnx_macs_follow_inferred_shapes():
    """Shapes between layers are inferred, so a dense layer after Flatten is counted too"""
    weights = numpy_helper.from_array(np.zeros((8, 3, 3, 3), np.float32), "W")
    dense = numpy_helper.from_array(np.zeros((8 * 30 * 30, 10), np.float32), "D")
    graph = helper.make_graph(
        [
            helper.make_node("Conv", ["x", "W"], ["c"]),
            helper.make_node("Flatten", ["c"], ["f"]),
            helper.make_node("MatMul", ["f", "D"], ["y"]),
        ],
        "classifier",
        [helper.make_tensor_value_info("x", TensorProto.FLOAT, [1, 3, 32, 32])],
        [helper.make_tensor_value_info("y", TensorProto.FLOAT, [1, 10])],
        [weights, dense],
    )
    info = parse_model(helper.make_model(graph).SerializeToString(), "classifier.onnx")
    
    assert info["macs"] == 8 * 30 * 30 * 27 + 7200 * 10

def test_onnx_gemm_macs():
    weights = numpy_helper.from_array(np.zeros((10, 64), np.float32), "W")
    graph = helper.make_graph(
        [helper.make_node("Gemm", ["x", "W"], ["y"], transB=1)],
        "dense",
        [helper.make_tensor_value_info("x", TensorProto.FLOAT, [1, 64])],
        [helper.make_tensor_value_info("y", TensorProto.FLOAT, [1, 10])],
        [weights],
    )
    
    assert parse_model(helper.make_model(graph).SerializeToString(), "dense.onnx")["macs"] == 64 * 10
