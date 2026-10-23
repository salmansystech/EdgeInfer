# Getting Started

This guide takes you from a fresh clone to a running EdgeInfer, with commands for Windows (PowerShell) and macOS/Linux.

There are three ways to run the project. Pick one:

| Option | Best for | You need |
|---|---|---|
| [A. Docker](#option-a-docker-easiest) | Running the whole app with one command | Docker Desktop |
| [B. Local web app](#option-b-run-locally-web-ui) | Developing the backend or UI | Python 3.10+ and Node.js 18+ |
| [C. CLI only](#option-c-command-line-only) | Quick analysis from the terminal | Python 3.10+ |

All options need a language model. See [Step 1](#step-1-get-the-code-and-choose-a-language-model).

---

## Step 1: Get the code and choose a language model

```bash
git clone https://github.com/salmansystech/EdgeInfer.git
cd EdgeInfer
```

Create your settings file from the template:

```powershell
# Windows (PowerShell)
copy .env.example .env
```
```bash
# macOS / Linux
cp .env.example .env
```

Open `.env` in any editor and fill in **one** of these providers.

**Option 1: Claude (Anthropic)**
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_api_key_here
MODEL=claude-opus-5-5
EFFORT=medium
```
Get a key at [console.anthropic.com](https://console.anthropic.com).

**Option 2: Ollama Cloud**
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=https://ollama.com
OLLAMA_MODEL=gemma4:31b
OLLAMA_API_KEY=your_ollama_key_here
```
Get a key from your account at [ollama.com](https://ollama.com).

**Option 3: Local Ollama (free, runs on your computer)**
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma4:31b
```
Install [Ollama](https://ollama.com/download) and download the model first with `ollama pull gemma4:31b`. Any other Ollama model works too, as long as `OLLAMA_MODEL` matches its name.

> `.env` is listed in `.gitignore`, so your keys are never committed.

### All settings

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `anthropic` | `anthropic` or `ollama` |
| `ANTHROPIC_API_KEY` | none | Claude API key |
| `MODEL` | `claude-opus-5-5` | Claude model ID |
| `EFFORT` | `medium` | Claude reasoning effort: `low`, `medium`, `high`, `xhigh` or `max` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server address |
| `OLLAMA_MODEL` | `gemma4:31b` | Ollama model name |
| `OLLAMA_API_KEY` | none | Only needed for Ollama Cloud |

---

## Option A: Docker (easiest)

**1. Start Docker Desktop** and wait until it shows that the engine is running. Check it with:
```bash
docker info
```
If this prints details without a "failed to connect" error, you're ready.

**2. Build and start** (from the project folder, with `.env` filled in):
```bash
docker compose up -d --build
```
The first build takes a few minutes. Later builds take seconds because Docker caches each step.

**3. Open the app** at **http://localhost:3000**.

### Everyday Docker commands

| Task | Command |
|---|---|
| Start in the background | `docker compose up -d` |
| Start and watch logs | `docker compose up` (the window looks idle until requests arrive) |
| Watch logs of a background run | `docker compose logs -f` |
| Check that both containers are running | `docker compose ps` |
| Rebuild after changing code or `.env` | `docker compose up -d --build` |
| Stop everything | `docker compose down` |

The backend container serves the API on port 5000. The frontend container serves the UI on port 3000 and forwards `/api` requests to the backend.

---

## Option B: Run locally (web UI)

You need two terminals: one for the backend and one for the frontend.

**Terminal 1: backend**
```powershell
# Windows (PowerShell)
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python server.py
```
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python server.py
```
The API is now running at http://localhost:5000. You only need to create the virtual environment and install packages once. Next time, just activate it and run `python server.py`.

**Terminal 2: frontend**
```bash
cd client
npm install
npm run dev
```
Open **http://localhost:3000**. The Vite dev server forwards `/api` requests to the backend, and the page reloads automatically when you edit the UI code.

Stop either server with `Ctrl + C`.

---

## Option C: Command line only

Set up Python as in Option B (`venv`, activate, `pip install -r requirements.txt`). Then:

```bash
# List supported devices and their keys
python main.py list-hardware

# Estimate size, latency, power and energy (no LLM needed)
python main.py benchmark --model examples/sample-models/hello_world_float.tflite --hardware esp32

# Feasibility analysis, then ask follow-up questions (type 'exit' to quit)
python main.py analyze --model examples/sample-models/hello_world_int8.tflite --hardware esp32

# Optimization plan, then refine it with feedback (type 'done' to finish)
python main.py optimize --model examples/sample-models/hello_world_float.tflite --hardware arm_cortex_m4 --level balanced

# Generate C++ inference code and save it to output/inference.md
python main.py generate --model examples/sample-models/hello_world_int8.tflite --hardware esp32_s3 --output output/
```

| Option | Used by | Values |
|---|---|---|
| `--model`, `-m` | all commands | Path to a `.tflite` or `.onnx` file (required) |
| `--hardware`, `-hw` | all commands | `esp32` (default), `esp32_s3`, `arm_cortex_m4`, `arm_cortex_m7`, `raspberry_pi_pico`, `arduino_nano_33`, `nrf52840` |
| `--level`, `-l` | `optimize` | `conservative`, `balanced` (default), `aggressive` |
| `--optimization`, `-o` | `benchmark` | Comma-separated techniques: `quantization`, `pruning`, `fusion` (default `quantization,pruning`) |
| `--output`, `-out` | `generate` | Folder to save the generated code in |

Add `--help` to any command for its full options, for example `python main.py analyze --help`.

---

## Using the web app

1. **Upload a model.** Drag a `.tflite` or `.onnx` file onto the upload box, or click **Select File**. No model handy? Use one from `examples/sample-models/`. A card appears showing the model's parameters, MACs, layers, precision, input/output shapes and operators.
2. **Pick a target device**, such as ESP32.
3. **Pick an optimization level.** Balanced is a good start.
4. **Click Analyze & Optimize.**
   - The performance estimate (size, latency, power, energy, accuracy) appears instantly.
   - The model analysis and optimization plan from the LLM appear when ready, usually within a few seconds to a minute depending on the model and provider.
5. **Click Generate Inference Code** to get C++ code for TensorFlow Lite Micro.
6. **Click Download** on any result to save it as a Markdown file.

Changing the model, device or level clears the results, so you can compare devices quickly.

---

## Running the tests

```bash
pip install -r requirements-dev.txt
python -m pytest
```

All LLM calls are mocked, so the tests need no API key or internet connection and finish in about a second. To check the frontend compiles:

```bash
cd client
npm run build
```

GitHub Actions runs both automatically on every push to `main`.

---

## Troubleshooting

| Problem | Cause and fix |
|---|---|
| `failed to connect to the docker API` | Docker Desktop isn't running. Start it and wait for the engine to be ready. |
| `port is already allocated` / `Address already in use` | Something else is using port 3000 or 5000. Stop it, or run `docker compose down` if it's an earlier EdgeInfer run. |
| `docker compose up` seems stuck after `Attaching to ...` | It's running and showing live logs. Open http://localhost:3000. Use `docker compose up -d` to get your terminal back. |
| UI shows "Could not reach the backend" | The backend isn't running. Start `python server.py` (Option B) or check `docker compose ps` (Option A). |
| `Invalid or missing ANTHROPIC_API_KEY` / `OLLAMA_API_KEY` | The key in `.env` is wrong or missing. Fix it, then restart the backend (Docker: `docker compose up -d --build`). |
| `Could not reach Ollama at http://localhost:11434` | Local Ollama isn't running. Start the Ollama app, or switch to Ollama Cloud. |
| `Unsupported model format` | Only `.tflite` and `.onnx` are supported. Convert TensorFlow/Keras models with the TFLite converter, or PyTorch models with `torch.onnx.export`. |
| `'python' is not recognized` (Windows) | Install Python from python.org and tick "Add Python to PATH", or use `py` instead of `python`. |
| Emoji show as `?` in the CLI | Use Windows Terminal or a recent PowerShell. EdgeInfer already forces UTF-8 output. |
| The Flask "development server" warning | Expected when running locally. It only matters for a public deployment. |
