import os
from dotenv import load_dotenv
from typing import Dict

load_dotenv()

class Config:
    """EdgeInfer Configuration"""
    # Language model provider: "anthropic" (Claude) or "ollama"
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic").lower()
    
    API_KEY = os.getenv("ANTHROPIC_API_KEY")
    MODEL = os.getenv("MODEL", "claude-opus-5-5")
    EFFORT = os.getenv("EFFORT", "medium")  # low | medium | high | xhigh | max
    
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:31b")
    OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")  # only needed for Ollama Cloud
    
    # Supported model formats
    SUPPORTED_FORMATS = ["pb", "tflite", "onnx", "pt", "pth", "h5"]
    
    # Target hardware specifications
    HARDWARE_TARGETS: Dict = {
        "arm_cortex_m4": {
            "name": "ARM Cortex-M4",
            "ram_kb": 256,
            "flash_kb": 1024,
            "cpu_mhz": 168,
            "power_mw": 100,
            "platform": "STM32L4"
        },
        "arm_cortex_m7": {
            "name": "ARM Cortex-M7",
            "ram_kb": 512,
            "flash_kb": 2048,
            "cpu_mhz": 216,
            "power_mw": 150,
            "platform": "STM32H7"
        },
        "esp32": {
            "name": "ESP32",
            "ram_kb": 520,
            "flash_kb": 4096,
            "cpu_mhz": 240,
            "power_mw": 80,
            "platform": "ESP32"
        },
        "esp32_s3": {
            "name": "ESP32-S3",
            "ram_kb": 512,
            "flash_kb": 8192,
            "cpu_mhz": 240,
            "power_mw": 90,
            "platform": "ESP32-S3"
        },
        "raspberry_pi_pico": {
            "name": "Raspberry Pi Pico",
            "ram_kb": 264,
            "flash_kb": 2048,
            "cpu_mhz": 125,
            "power_mw": 50,
            "platform": "RP2040"
        },
        "arduino_nano_33": {
            "name": "Arduino Nano 33",
            "ram_kb": 256,
            "flash_kb": 1024,
            "cpu_mhz": 64,
            "power_mw": 40,
            "platform": "nRF52840"
        },
        "nrf52840": {
            "name": "nRF52840",
            "ram_kb": 256,
            "flash_kb": 1024,
            "cpu_mhz": 64,
            "power_mw": 45,
            "platform": "nRF52840"
        }
    }
    
    # Optimization levels
    OPTIMIZATION_LEVELS = {
        "conservative": {
            "quantization": False,
            "pruning": False,
            "fusion": False,
            "description": "No optimization, maximum accuracy"
        },
        "balanced": {
            "quantization": True,
            "pruning": True,
            "fusion": True,
            "description": "Moderate optimization"
        },
        "aggressive": {
            "quantization": True,
            "pruning": True,
            "fusion": True,
            "description": "Maximum compression"
        }
    }
    
    # Analysis settings
    MAX_MODEL_SIZE = 500_000_000  # 500MB
    TIMEOUT = 300  # seconds
    TEMP_DIR = "temp_models"
