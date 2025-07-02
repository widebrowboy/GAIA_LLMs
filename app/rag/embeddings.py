"""
임베딩 서비스 모듈

Ollama의 mxbai-embed-large 모델을 사용하여 텍스트를 벡터로 변환
"""

import logging
from typing import List, Optional
import requests
import json
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Ollama를 통한 텍스트 임베딩 서비스"""
    
    def __init__(self, 
                 model_name: str = "mxbai-embed-large",
                 ollama_base_url: str = "http://localhost:11434"):
        """
        Args:
            model_name: 사용할 임베딩 모델 이름
            ollama_base_url: Ollama 서버 URL
        """
        self.model_name = model_name
        self.ollama_base_url = ollama_base_url
        self.embedding_endpoint = f"{ollama_base_url}/api/embeddings"
        
    def embed_text(self, text: str) -> Optional[List[float]]:
        """
        단일 텍스트를 임베딩 벡터로 변환
        
        Args:
            text: 임베딩할 텍스트
            
        Returns:
            임베딩 벡터 (리스트) 또는 None
        """
        try:
            payload = {
                "model": self.model_name,
                "prompt": text
            }
            
            response = requests.post(
                self.embedding_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                embedding = result.get("embedding", [])
                logger.debug(f"Successfully embedded text (dim: {len(embedding)})")
                return embedding
            else:
                logger.error(f"Embedding failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error during embedding: {str(e)}")
            return None
    
    def embed_batch(self, texts: List[str], batch_size: int = 10) -> List[Optional[List[float]]]:
        """
        여러 텍스트를 배치로 임베딩
        
        Args:
            texts: 임베딩할 텍스트 리스트
            batch_size: 배치 크기
            
        Returns:
            임베딩 벡터 리스트
        """
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            for text in batch:
                embedding = self.embed_text(text)
                embeddings.append(embedding)
                
        return embeddings
    
    def get_embedding_dimension(self) -> Optional[int]:
        """
        임베딩 모델의 차원 수 확인
        
        Returns:
            임베딩 차원 수 또는 None
        """
        test_embedding = self.embed_text("test")
        if test_embedding:
            return len(test_embedding)
        return None