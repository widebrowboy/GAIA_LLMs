#!/usr/bin/env python3
"""
단순화된 Ollama 클라이언트 - 스트리밍 전용
"""

import json
import asyncio
from typing import Optional, AsyncGenerator
import httpx

class SimpleOllamaClient:
    """단순화된 Ollama 클라이언트"""
    
    def __init__(self, model: str = "gemma3-12b:latest", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self._client = None
    
    async def _get_client(self):
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=httpx.Timeout(600.0))
        return self._client
    
    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def generate_stream(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """
        단순화된 스트리밍 생성
        
        Args:
            prompt: 사용자 프롬프트
            system_prompt: 시스템 프롬프트
            temperature: 생성 온도
            
        Yields:
            str: 생성된 텍스트 청크
        """
        print(f"🔄 질의 시작: {prompt[:50]}...")
        
        # 프롬프트 준비
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n사용자: {prompt}\n\n어시스턴트:"
        
        # 페이로드 구성
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": 500,
                "keep_alive": "5m"
            }
        }
        
        try:
            client = await self._get_client()
            
            async with client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                response.raise_for_status()
                
                print("📡 스트리밍 응답 시작")
                chunk_count = 0
                
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            chunk_data = json.loads(line)
                            
                            if "response" in chunk_data and chunk_data["response"]:
                                chunk_count += 1
                                if chunk_count % 20 == 0:  # 20개 청크마다 로그
                                    print(f"📝 청크 {chunk_count} 수신")
                                yield chunk_data["response"]
                            
                            if chunk_data.get("done", False):
                                print(f"✅ 스트리밍 완료 (총 {chunk_count}개 청크)")
                                return
                                
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            error_msg = f"스트리밍 오류: {str(e)}"
            print(f"❌ {error_msg}")
            yield f"[오류: {error_msg}]"