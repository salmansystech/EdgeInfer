# EdgeInfer - AI Model Deployment for Edge Devices

[![CI](https://github.com/salmansystech/EdgeInfer/actions/workflows/ci.yml/badge.svg)](https://github.com/salmansystech/EdgeInfer/actions/workflows/ci.yml)

An **LLM-powered assistant** for deploying machine learning models to resource-constrained embedded devices. Upload a `.tflite` or `.onnx` model and pick a microcontroller, and EdgeInfer reads the model's architecture, then produces a feasibility analysis, an optimization plan, and C/C++ inference code for TensorFlow Lite Micro.

Use it from the **command line** or through a **React web UI**, with either **Claude** (Anthropic) or any **Ollama** model (local or Ollama Cloud) as the language model.

## 🎯 Features

### 📦 Model Parsing
- Reads **TensorFlow Lite** (`.tflite`) and **ONNX** (`.onnx`) files
- Extracts parameter count, layers, operator types, input/output shapes and weight precision (e.g. FLOAT32 or INT8)
- These real details are passed to every analysis, plan and code generation step

### 🔍 Model Analysis
- Feasibility assessment against the target device's RAM, Flash and CPU
- Memory, latency and power considerations
- Optimization opportunities ranked by impact
- Interactive follow-up questions (CLI)

### ⚡ Optimization Planning
- Conservative, balanced or aggressive strategies
- Quantization (FP32 → INT8/INT16), pruning, layer fusion and distillation recommendations
- Trade-off analysis between accuracy, size and latency
- Iterative refinement with your feedback (CLI)

### 💻 Code Generation
- C/C++ inference code for TensorFlow Lite Micro
- Hardware-specific notes (e.g. ESP-NN on ESP32, CMSIS-NN on Cortex-M)
- Memory management, error handling and integration guidance

### 📊 Performance Estimator
- Quick, rule-based estimates of optimized size, latency, power and accuracy retention
- Checks whether the optimized model fits in the device's Flash
- Recognizes models that are already INT8-quantized
- Runs locally with no API call

## 🏆 Supported Platforms

| Device | RAM | Flash | CPU |
|---|---|---|---|
| ESP32 | 520 KB | 4 MB | 240 MHz |
| ESP32-S3 | 512 KB | 8 MB | 240 MHz |
| ARM Cortex-M4 (STM32L4) | 256 KB | 1 MB | 168 MHz |
| ARM Cortex-M7 (STM32H7) | 512 KB | 2 MB | 216 MHz |
| Raspberry Pi Pico (RP2040) | 264 KB | 2 MB | 125 MHz |
| Arduino Nano 33 | 256 KB | 1 MB | 64 MHz |
| nRF52840 | 256 KB | 1 MB | 64 MHz |

Hardware targets are defined in [`src/config.py`](src/config.py) and are easy to extend.

## 🚀 Quick Start

### 1. Install

Requires Python 3.10+ (and Node.js 18+ for the web UI).

```bash
git clone https://github.com/salmansystech/EdgeInfer.git
cd EdgeInfer

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
```

### 2. Choose a language model

Edit `.env` and pick one provider:

**Claude (Anthropic)**
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_api_key_here
MODEL=claude-opus-5-5
EFFORT=medium
```

**Ollama Cloud**
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=https://ollama.com
OLLAMA_MODEL=gemma4:31b
OLLAMA_API_KEY=your_ollama_key_here
```

**Local Ollama** (no key needed)
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma4:31b
```

### 3a. Use the CLI

```bash
# List supported hardware
python main.py list-hardware

# Analyze a model for a device (then ask follow-up questions; type 'exit' to quit)
python main.py analyze --model examples/sample-models/hello_world_int8.tflite --hardware esp32

# Generate an optimization strategy (then refine it with feedback; type 'done' to finish)
python main.py optimize --model examples/sample-models/hello_world_float.tflite --hardware esp32 --level balanced

# Generate inference code and save it to output/inference.md
python main.py generate --model examples/sample-models/hello_world_int8.tflite --hardware esp32 --output output/

# Estimate optimized size, latency and power
python main.py benchmark --model examples/sample-models/hello_world_float.tflite --hardware esp32 --optimization quantization,pruning
```

Use your own `.tflite` or `.onnx` file, or the [sample models](examples/sample-models/) included in the repo. Each command starts by printing what it read from the model:

```
📦 hello_world_int8 (TensorFlow Lite, 2.6 KB)
   Parameters: 321 | Layers: 3 | Precision: INT8
   Input: (1, 1) | Output: (1, 1)
   Operators: FULLY_CONNECTED x3
```

### 3b. Use the web UI

```bash
# Terminal 1 - backend API on http://localhost:5000
python server.py

# Terminal 2 - UI on http://localhost:3000
cd client
npm install
npm run dev
```

Upload a `.tflite` or `.onnx` model (or a sample from `examples/sample-models/`) to see its parameters, layers, precision and operators. Then pick a device and optimization level and click **Analyze & Optimize**. The UI shows the estimates, the analysis and the optimization plan, and can then generate inference code. Each result can be downloaded as Markdown.

### 3c. Or run everything with Docker

```bash
docker compose up --build
```

The UI is served on `http://localhost:3000` and the API on `http://localhost:5000`. Settings are read from `.env`.

## 📊 System Architecture

```
.tflite / .onnx file
    ↓
Model Parser                  (no LLM)
└─ Parameters, layers, operators, shapes, precision
    ↓
Model details + target device + optimization level
    ↓
Step 1: Model Analysis        (LLM)
├─ Feasibility vs. RAM / Flash / CPU
├─ Memory and latency considerations
└─ Ranked optimization opportunities
    ↓
Step 2: Optimization Plan     (LLM)
├─ Quantization / pruning / fusion strategy
├─ Trade-off analysis
└─ Expected size, latency and accuracy
    ↓
Step 3: Code Generation       (LLM, uses the plan from step 2)
├─ TensorFlow Lite Micro inference code
├─ Hardware-specific optimizations
└─ Integration and deployment notes

Performance Estimator         (rule-based, no LLM)
└─ Size, latency, power and fit-in-Flash estimates
```

All LLM calls go through [`src/llm.py`](src/llm.py), so switching between Claude and Ollama is a single setting.

### REST API

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/hardware-targets` | List supported devices |
| POST | `/api/parse-model` | Upload a `.tflite` or `.onnx` file (multipart field `file`) and get its architecture details |
| POST | `/api/analyze` | Model analysis |
| POST | `/api/optimize` | Optimization plan plus estimated size reduction and speed-up |
| POST | `/api/generate-code` | Inference code based on an optimization plan |
| POST | `/api/benchmark` | Rule-based performance estimate |

## 📁 Project Structure

```
EdgeInfer/
├── src/
│   ├── config.py               # Hardware targets and settings
│   ├── llm.py                  # Claude / Ollama provider layer
│   ├── model_parser.py         # .tflite / .onnx model reader
│   ├── model_analyzer.py       # Model analysis step
│   ├── optimization_agent.py   # Optimization planning step
│   ├── code_generator.py       # Code generation step
│   ├── benchmarker.py          # Rule-based performance estimator
│   └── cli.py                  # Click CLI
├── client/                     # React + TypeScript + Vite web UI
├── examples/
│   ├── sample-models/          # Small TFLite models to try
│   ├── model_info_example.json
│   └── deployment_guide.md
├── tests/                      # pytest suite
├── main.py                     # CLI entry point
├── server.py                   # Flask REST API
├── Dockerfile                  # Backend image
├── docker-compose.yml          # Backend + UI
├── requirements.txt
└── setup.py
```

## 🤖 Technology Stack

- **LLM:** Claude API (Anthropic) or Ollama (local or Ollama Cloud)
- **Backend:** Python 3.10+, Flask, Click
- **Model parsing:** `tflite` (FlatBuffers schema), `onnx`
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS
- **Deployment:** Docker, Docker Compose
- **Generated code targets:** TensorFlow Lite Micro, ESP-NN, CMSIS-NN

## 🧪 Running Tests

```bash
pip install -r requirements-dev.txt
python -m pytest
```

The tests cover the model parser, the performance estimator, the Claude and Ollama provider layer, and every API endpoint. LLM calls are mocked, so no API key or network access is needed. GitHub Actions runs the tests (Python 3.10 and 3.13) and the frontend build on every push.

## ⚠️ Current Limitations

EdgeInfer is a working prototype. Please keep in mind:

- **Only `.tflite` and `.onnx` are supported.** Convert TensorFlow/Keras or PyTorch models to one of these formats first.
- **Performance numbers are estimates.** The benchmark uses fixed rules of thumb per technique (for example, quantization ≈ 4× smaller). It is not measured on hardware.
- **LLM output should be reviewed.** Analyses, plans and generated code come from a language model and need checking before production use.
- **Not hardened for public hosting.** The API has no authentication or rate limiting, so anyone who can reach it can spend your API credits.

## 🔮 Roadmap

- [ ] Device-aware latency estimates based on clock speed and model FLOPs
- [ ] Render Markdown output in the UI
- [ ] Follow-up questions in the web UI
- [ ] Authentication and rate limiting for hosted deployments
- [ ] Real hardware testing

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT.md)
- [Model Deployment Walkthrough](examples/deployment_guide.md)
- [Sample Models](examples/sample-models/)
- [Model Information Example](examples/model_info_example.json)
- [Web UI](client/README.md)

## 📄 License

MIT License - See LICENSE file

This is a personal portfolio project and is not accepting outside contributions.

## 👨‍💻 Author

**Salman Khan** - [GitHub](https://github.com/salmansystech)

---

**Deploy intelligent AI to microcontrollers. Optimize once, run everywhere.** 🚀
