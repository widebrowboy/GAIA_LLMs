#!/usr/bin/env python3
"""
설정 관리 모듈
환경 변수 및 시스템 설정 관리
"""

import json
import os
from typing import Any, Dict

from dotenv import load_dotenv


class ConfigManager:
    """
    설정 관리 클래스
    환경 변수 로드 및 시스템 설정 관리
    """

    def __init__(self, env_file: str = '.env', config_file: str = 'config.json'):
        """
        설정 관리자 초기화

        Args:
            env_file: 환경 변수 파일 경로
            config_file: 설정 파일 경로
        """
        # 환경 변수 로드
        self.env_file = env_file
        load_dotenv(env_file)

        # 설정 파일 로드 시도
        self.config_file = config_file
        self.config = {}

        if os.path.exists(config_file):
            try:
                with open(config_file, encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"설정 파일 로드 중 오류 발생: {e!s}")

        # 기본 설정
        self.defaults = {
            'ollama_url': 'http://localhost:11434',
            'ollama_model': 'gemma3:4b',
            'output_dir': './research_outputs',
            'feedback_depth': 2,
            'feedback_width': 2,
            'min_response_length': 1000,
            'concurrent_research': 2
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        설정값 조회 (환경 변수 > 설정 파일 > 기본값 순서로 확인)

        Args:
            key: 설정 키
            default: 기본값

        Returns:
            Any: 설정값
        """
        # 환경 변수 확인 (대문자 형태로 변환하여 검색)
        env_key = key.upper()
        if env_key in os.environ:
            return os.environ[env_key]

        # 설정 파일 확인
        if key.lower() in self.config:
            return self.config[key.lower()]

        # 기본값 확인
        if key.lower() in self.defaults:
            return self.defaults[key.lower()]

        # 기본값 반환
        return default

    def get_ollama_url(self) -> str:
        """Ollama API URL 조회"""
        return self.get('OLLAMA_BASE_URL', self.defaults['ollama_url'])

    def get_ollama_model(self) -> str:
        """Ollama 모델명 조회"""
        return self.get('OLLAMA_MODEL', self.defaults['ollama_model'])

    def get_output_dir(self) -> str:
        """출력 디렉토리 경로 조회"""
        return self.get('OUTPUT_DIR', self.defaults['output_dir'])

    def get_feedback_depth(self) -> int:
        """피드백 루프 깊이 조회"""
        depth = self.get('FEEDBACK_DEPTH', self.defaults['feedback_depth'])
        # 문자열로 반환된 경우 정수 변환 시도
        if isinstance(depth, str):
            try:
                depth = int(depth)
            except ValueError:
                depth = self.defaults['feedback_depth']
        return max(1, min(10, depth))  # 1~10 범위 보장

    def get_feedback_width(self) -> int:
        """피드백 루프 너비 조회"""
        width = self.get('FEEDBACK_WIDTH', self.defaults['feedback_width'])
        # 문자열로 반환된 경우 정수 변환 시도
        if isinstance(width, str):
            try:
                width = int(width)
            except ValueError:
                width = self.defaults['feedback_width']
        return max(1, min(10, width))  # 1~10 범위 보장

    def get_min_response_length(self) -> int:
        """최소 응답 길이 조회"""
        length = self.get('MIN_RESPONSE_LENGTH', self.defaults['min_response_length'])
        # 문자열로 반환된 경우 정수 변환 시도
        if isinstance(length, str):
            try:
                length = int(length)
            except ValueError:
                length = self.defaults['min_response_length']
        return max(100, length)

    def get_concurrent_research(self) -> int:
        """동시 연구 프로세스 수 조회"""
        concurrent = self.get('CONCURRENT_RESEARCH', self.defaults['concurrent_research'])
        # 문자열로 반환된 경우 정수 변환 시도
        if isinstance(concurrent, str):
            try:
                concurrent = int(concurrent)
            except ValueError:
                concurrent = self.defaults['concurrent_research']
        return max(1, concurrent)

    def get_gpu_params(self) -> Dict[str, Any]:
        """GPU 최적화 파라미터 조회"""
        return {
            "num_gpu": 99,  # 사용 가능한 모든 GPU 활용
            "num_thread": 8,  # 병렬 스레드 활용
            "f16_kv": True,  # 메모리 효율성
            "mirostat": 2  # 고급 샘플링
        }

    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        설정 파일 저장

        Args:
            config: 저장할 설정

        Returns:
            bool: 성공 여부
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            self.config = config
            return True
        except Exception as e:
            print(f"설정 파일 저장 중 오류 발생: {e!s}")
            return False

    def create_default_config_file(self) -> bool:
        """
        기본 설정 파일 생성

        Returns:
            bool: 성공 여부
        """
        # 기존 환경 변수 값 가져오기
        config = {}
        for key, default in self.defaults.items():
            env_key = key.upper()
            if env_key in os.environ:
                config[key] = os.environ[env_key]
            else:
                config[key] = default

        return self.save_config(config)


# 모듈 직접 실행 시 테스트
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='설정 관리 모듈 테스트')
    parser.add_argument('--create', '-c', action='store_true',
                       help='기본 설정 파일 생성')
    parser.add_argument('--env', '-e', type=str, default='.env',
                       help='환경 변수 파일 경로')
    parser.add_argument('--config', '-f', type=str, default='config.json',
                       help='설정 파일 경로')

    args = parser.parse_args()

    # 설정 관리자 생성
    config_manager = ConfigManager(args.env, args.config)

    # 기본 설정 파일 생성
    if args.create:
        print(f"기본 설정 파일 생성 중: {args.config}")

        if config_manager.create_default_config_file():
            print(f"✅ 설정 파일 생성 완료: {args.config}")
        else:
            print("❌ 설정 파일 생성 실패")

    # 현재 설정 출력
    print("\n=== 현재 설정 ===")
    print(f"Ollama URL: {config_manager.get_ollama_url()}")
    print(f"Ollama 모델: {config_manager.get_ollama_model()}")
    print(f"출력 디렉토리: {config_manager.get_output_dir()}")
    print(f"피드백 루프 깊이: {config_manager.get_feedback_depth()}")
    print(f"피드백 루프 너비: {config_manager.get_feedback_width()}")
    print(f"최소 응답 길이: {config_manager.get_min_response_length()}")
    print(f"동시 연구 프로세스 수: {config_manager.get_concurrent_research()}")
    print(f"GPU 최적화 파라미터: {config_manager.get_gpu_params()}")
