# EdgeInfer Model Deployment Walkthrough

A typical workflow for taking a model to a microcontroller with the CLI. Setup instructions are in [docs/GETTING_STARTED.md](../docs/GETTING_STARTED.md).

## Quick Start

1. Check how the model would perform on your device (instant, no LLM):
```bash
python main.py benchmark --model examples/sample-models/hello_world_float.tflite --hardware esp32
```

2. Analyze feasibility:
```bash
python main.py analyze --model examples/sample-models/hello_world_float.tflite --hardware esp32
```

3. Generate an optimization strategy:
```bash
python main.py optimize --model examples/sample-models/hello_world_float.tflite --hardware esp32 --level balanced
```

4. Generate inference code:
```bash
python main.py generate --model examples/sample-models/hello_world_int8.tflite --hardware esp32 --output output/
```

Replace the sample model with your own `.tflite` or `.onnx` file.

## Supported Models

- TensorFlow Lite (`.tflite`)
- ONNX (`.onnx`)

Other formats need converting first:

| From | Convert with |
|---|---|
| TensorFlow / Keras (SavedModel, `.h5`, `.keras`) | `tf.lite.TFLiteConverter` → `.tflite` |
| PyTorch (`.pt`, `.pth`) | `torch.onnx.export` → `.onnx` |

## Supported Hardware

- ESP32 (WiFi+BLE IoT)
- ESP32-S3 (Enhanced performance, vector instructions)
- ARM Cortex-M4 (STM32L4)
- ARM Cortex-M7 (STM32H7)
- Raspberry Pi Pico
- Arduino Nano 33
- nRF52840 (BLE)

Run `python main.py list-hardware` for each device's key and specs.
