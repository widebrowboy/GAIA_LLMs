"""
RAG 파이프라인 모듈

문서 처리, 벡터화, 검색, 생성을 통합한 RAG 시스템
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json

from .embeddings import EmbeddingService
from .vector_store_lite import MilvusLiteVectorStore
import requests

logger = logging.getLogger(__name__)


@dataclass
class RAGResponse:
    """RAG 응답 데이터 클래스"""
    answer: str
    sources: List[Dict[str, Any]]
    query: str
    context: List[str]


class RAGPipeline:
    """통합 RAG 파이프라인"""
    
    def __init__(self,
                 embedding_model: str = "mxbai-embed-large",
                 generation_model: str = "gemma3-12b:latest",
                 milvus_lite_db: str = "./milvus_lite.db",
                 collection_name: str = "gaia_bt_documents"):
        """
        Args:
            embedding_model: 임베딩 모델 이름
            generation_model: 생성 모델 이름
            milvus_lite_db: Milvus Lite 데이터베이스 파일 경로
            collection_name: Milvus 컬렉션 이름
        """
        # 서비스 초기화
        self.embedding_service = EmbeddingService(model_name=embedding_model)
        self.generation_model = generation_model
        self.ollama_base_url = "http://localhost:11434"
        
        # 임베딩 차원 확인
        dimension = self.embedding_service.get_embedding_dimension()
        if not dimension:
            logger.warning("Could not determine embedding dimension, using default 1024")
            dimension = 1024
        
        # Milvus Lite 초기화
        self.vector_store = MilvusLiteVectorStore(
            db_file=milvus_lite_db,
            collection_name=collection_name,
            dimension=dimension
        )
        
        # Milvus Lite 연결 및 컬렉션 생성
        if self.vector_store.connect():
            self.vector_store.create_collection()
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        텍스트를 청크로 분할
        
        Args:
            text: 원본 텍스트
            chunk_size: 청크 크기 (문자 수)
            overlap: 청크 간 중첩 크기
            
        Returns:
            청크 리스트
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # 문장 중간에서 끊기지 않도록 조정
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                split_point = max(last_period, last_newline)
                
                if split_point > chunk_size * 0.5:  # 청크의 절반 이상인 경우만
                    chunk = chunk[:split_point + 1]
                    end = start + split_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return [c for c in chunks if c]  # 빈 청크 제거
    
    def add_documents(self, 
                     documents: List[str],
                     metadata: Optional[List[Dict[str, Any]]] = None,
                     chunk_size: int = 500) -> bool:
        """
        문서를 처리하여 벡터 데이터베이스에 추가
        
        Args:
            documents: 문서 리스트
            metadata: 문서별 메타데이터
            chunk_size: 청크 크기
            
        Returns:
            성공 여부
        """
        try:
            all_chunks = []
            all_metadata = []
            
            # 문서별로 청크 생성
            for i, doc in enumerate(documents):
                chunks = self.chunk_text(doc, chunk_size=chunk_size)
                
                # 메타데이터 처리
                doc_metadata = metadata[i] if metadata and i < len(metadata) else {}
                
                for j, chunk in enumerate(chunks):
                    chunk_metadata = {
                        **doc_metadata,
                        "doc_index": i,
                        "chunk_index": j,
                        "total_chunks": len(chunks)
                    }
                    
                    all_chunks.append(chunk)
                    all_metadata.append(chunk_metadata)
            
            # 임베딩 생성
            logger.info(f"Generating embeddings for {len(all_chunks)} chunks...")
            embeddings = self.embedding_service.embed_batch(all_chunks)
            
            # None 값 필터링
            valid_data = [
                (chunk, emb, meta) 
                for chunk, emb, meta in zip(all_chunks, embeddings, all_metadata)
                if emb is not None
            ]
            
            if not valid_data:
                logger.error("No valid embeddings generated")
                return False
            
            # 데이터 분리
            valid_chunks, valid_embeddings, valid_metadata = zip(*valid_data)
            
            # Milvus에 삽입
            success = self.vector_store.insert_documents(
                texts=list(valid_chunks),
                embeddings=list(valid_embeddings),
                metadata=list(valid_metadata)
            )
            
            if success:
                logger.info(f"Successfully added {len(valid_chunks)} chunks to vector store")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to add documents: {str(e)}")
            return False
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        쿼리와 관련된 문서 검색
        
        Args:
            query: 검색 쿼리
            top_k: 반환할 결과 수
            
        Returns:
            [(텍스트, 점수, 메타데이터)] 리스트
        """
        # 쿼리 임베딩
        query_embedding = self.embedding_service.embed_text(query)
        if not query_embedding:
            logger.error("Failed to embed query")
            return []
        
        # 벡터 검색
        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k
        )
        
        return results
    
    def generate_response(self, 
                         query: str,
                         contexts: List[str],
                         system_prompt: Optional[str] = None) -> str:
        """
        검색된 컨텍스트를 기반으로 응답 생성
        
        Args:
            query: 사용자 쿼리
            contexts: 검색된 컨텍스트 리스트
            system_prompt: 시스템 프롬프트
            
        Returns:
            생성된 응답
        """
        if not system_prompt:
            system_prompt = """당신은 신약개발 전문 AI 어시스턴트입니다. 
제공된 컨텍스트를 기반으로 정확하고 도움이 되는 답변을 제공하세요.
컨텍스트에 없는 정보는 추측하지 말고, 모르는 경우 명확히 알려주세요."""
        
        # 컨텍스트 결합
        context_text = "\n\n---\n\n".join(contexts)
        
        # 프롬프트 구성
        prompt = f"""시스템: {system_prompt}

컨텍스트:
{context_text}

질문: {query}

답변:"""
        
        # Ollama를 통한 응답 생성
        try:
            payload = {
                "model": self.generation_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 1000
                }
            }
            
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return "죄송합니다. 응답을 생성하는 중 오류가 발생했습니다."
            
        except Exception as e:
            logger.error(f"Failed to generate response: {str(e)}")
            return "죄송합니다. 응답을 생성하는 중 오류가 발생했습니다."
    
    def query(self, 
              query: str,
              top_k: int = 5,
              system_prompt: Optional[str] = None) -> RAGResponse:
        """
        전체 RAG 파이프라인 실행
        
        Args:
            query: 사용자 쿼리
            top_k: 검색할 문서 수
            system_prompt: 시스템 프롬프트
            
        Returns:
            RAG 응답 객체
        """
        # 1. 관련 문서 검색
        retrieved_docs = self.retrieve(query, top_k=top_k)
        
        if not retrieved_docs:
            return RAGResponse(
                answer="관련 문서를 찾을 수 없습니다.",
                sources=[],
                query=query,
                context=[]
            )
        
        # 2. 컨텍스트 추출
        contexts = [doc[0] for doc in retrieved_docs]
        sources = [
            {
                "text": doc[0],
                "score": doc[1],
                "metadata": doc[2]
            }
            for doc in retrieved_docs
        ]
        
        # 3. 응답 생성
        answer = self.generate_response(query, contexts, system_prompt)
        
        return RAGResponse(
            answer=answer,
            sources=sources,
            query=query,
            context=contexts
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """시스템 통계 정보 반환"""
        return {
            "vector_store": self.vector_store.get_collection_stats(),
            "embedding_model": self.embedding_service.model_name,
            "generation_model": self.generation_model
        }