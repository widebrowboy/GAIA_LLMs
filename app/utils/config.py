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
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3-12b:latest")

# 사용 가능한 모델 목록
AVAILABLE_MODELS = [
    "gemma3-12b:latest",         # 기본 모델 (12B 파라미터, 4비트 양자화) - 메모리 효율적
    "Gemma3:27b-it-q4_K_M",     # 대용량 모델 (27B 파라미터, 4비트 양자화)
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

# Debug mode setting
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() in ["true", "1", "yes"]

# Output directory for research results
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs/research")

# Ensure output directory exists
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# 프롬프트 관련 설정
AVAILABLE_PROMPT_TYPES = [
    "default",     # 기본 신약개발 프롬프트
    "clinical",    # 임상시험 전문 프롬프트
    "research",    # 연구 분석 전문 프롬프트
    "chemistry",   # 의약화학 전문 프롬프트
    "regulatory",  # 규제 전문 프롬프트
    "patent"       # 특허 검색 및 분석 전문 프롬프트
]

DEFAULT_PROMPT_TYPE = "default"

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
        # MCP 활성화 상태 (기본값: False)
        self.mcp_enabled = False
        # 프롬프트 타입 (기본값: default)
        self.prompt_type = DEFAULT_PROMPT_TYPE
