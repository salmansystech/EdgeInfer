# EdgeInfer Deployment Guide

## Quick Start

1. Analyze your model:
```bash
python main.py analyze --model model.pb --hardware esp32
```

2. Generate optimization strategy:
```bash
python main.py optimize --model model.pb --hardware esp32 --level balanced
```

3. Generate inference code:
```bash
python main.py generate --model model.pb --hardware esp32 --output output/
```

4. Benchmark performance:
```bash
python main.py benchmark --model model.pb --hardware esp32
```

## Supported Models

- TensorFlow SavedModel (.pb)
- TensorFlow Lite (.tflite)
- PyTorch (.pt, .pth)
- ONNX (.onnx)
- Keras (.h5)

## Supported Hardware

- ESP32 (WiFi+BLE IoT)
- ESP32-S3 (Enhanced performance)
- ARM Cortex-M4 (STM32L4)
- ARM Cortex-M7 (STM32H7)
- Raspberry Pi Pico
- Arduino Nano 33
- nRF52840 (BLE)
