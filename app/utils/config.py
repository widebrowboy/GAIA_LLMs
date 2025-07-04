"""
Configuration management for the CLI chatbot.

This module loads environment variables and provides configuration settings
for the chatbot application.
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ollama API settings
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "Gemma3:27b-it-q4_K_M")

# 사용 가능한 모델 목록
AVAILABLE_MODELS = [
    "Gemma3:27b-it-q4_K_M",     # 기본 모델 (27B 파라미터, 4비트 양자화)
    "Gemma3:latest",             # 일반 모델
    "txgemma-chat:latest",       # 대화형 모델
    "txgemma-predict:latest",    # 텍스트 생성 모델
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
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs/research")

# Ensure output directory exists
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

@dataclass
class Config:
    """챗봇 설정을 관리하는 클래스"""
    def __init__(self, model: str = "Gemma3:27b-it-q4_K_M", debug_mode: bool = False):
        self.model = model
        self.debug_mode = debug_mode
        self.feedback_depth = 3
        self.feedback_width = 5
        self.min_response_length = 100
        self.min_references = 2
        self.temperature = 0.7
        self.max_tokens = 2000
        # MCP 출력 표시 옵션 (기본값: False - 숨김)
        self.show_mcp_output = False
