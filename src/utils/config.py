"""
Configuration management for the CLI chatbot.

This module loads environment variables and provides configuration settings
for the chatbot application.
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Ollama API settings
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "Gemma3:latest")

# 사용 가능한 모델 목록
AVAILABLE_MODELS = [
    "Gemma3:latest",       # 기본 모델
    "txgemma-chat:latest",   # 대화형 모델
    "txgemma-predict:latest",  # 텍스트 생성 모델
]

# GPU optimization parameters
OLLAMA_PARAMS = {
    "num_gpu": 99,  # Use all available GPUs
    "num_thread": 8,  # Parallel threads
    "f16_kv": True,  # Memory efficiency
    "mirostat": 2,  # Advanced sampling
}

# Research settings
DEFAULT_FEEDBACK_DEPTH = 2  # Default feedback loop depth
DEFAULT_FEEDBACK_WIDTH = 2  # Default feedback loop width
MIN_RESPONSE_LENGTH = 100  # Minimum response length in characters
MIN_REFERENCES = 2  # Minimum number of references

# Output directory for research results
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "research_outputs")

# Ensure output directory exists
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
