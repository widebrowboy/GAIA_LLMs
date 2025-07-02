"""
ChromaDB 벡터 스토어 모듈

로컬 벡터 데이터베이스로 ChromaDB 사용
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings
import json

logger = logging.getLogger(__name__)


class ChromaVectorStore:
    """ChromaDB 벡터 데이터베이스 관리 클래스"""
    
    def __init__(self,
                 persist_directory: str = "./chroma_db",
                 collection_name: str = "gaia_bt_documents"):
        """
        Args:
            persist_directory: ChromaDB 저장 디렉토리
            collection_name: 컬렉션 이름
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        
    def connect(self):
        """ChromaDB 클라이언트 초기화"""
        try:
            # ChromaDB 클라이언트 생성
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info(f"ChromaDB client initialized at {self.persist_directory}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            return False
    
    def create_collection(self):
        """컬렉션 생성 또는 가져오기"""
        try:
            if not self.client:
                logger.error("ChromaDB client not initialized")
                return False
            
            # 기존 컬렉션 가져오기 또는 새로 생성
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "GAIA-BT document embeddings for RAG"}
            )
            
            logger.info(f"Collection '{self.collection_name}' ready")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create/get collection: {str(e)}")
            return False
    
    def insert_documents(self, 
                        texts: List[str],
                        embeddings: List[List[float]],
                        metadata: Optional[List[Dict[str, Any]]] = None,
                        ids: Optional[List[str]] = None) -> bool:
        """
        문서와 임베딩을 ChromaDB에 삽입
        
        Args:
            texts: 원본 텍스트 리스트
            embeddings: 임베딩 벡터 리스트
            metadata: 메타데이터 리스트
            ids: 문서 ID 리스트 (선택사항)
            
        Returns:
            성공 여부
        """
        try:
            if not self.collection:
                logger.error("Collection not initialized")
                return False
            
            # ID 생성 (제공되지 않은 경우)
            if ids is None:
                import uuid
                ids = [str(uuid.uuid4()) for _ in range(len(texts))]
            
            # 메타데이터 처리
            if metadata is None:
                metadata = [{}] * len(texts)
            
            # ChromaDB에 추가
            self.collection.add(
                ids=ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadata
            )
            
            logger.info(f"Inserted {len(texts)} documents into collection")
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert documents: {str(e)}")
            return False
    
    def search(self, 
               query_embedding: List[float],
               top_k: int = 5,
               filter_dict: Optional[Dict[str, Any]] = None) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        벡터 유사도 검색
        
        Args:
            query_embedding: 쿼리 임베딩 벡터
            top_k: 반환할 결과 수
            filter_dict: 필터 조건 (ChromaDB where 절)
            
        Returns:
            [(텍스트, 점수, 메타데이터)] 리스트
        """
        try:
            if not self.collection:
                logger.error("Collection not initialized")
                return []
            
            # 검색 실행
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter_dict,
                include=["documents", "metadatas", "distances"]
            )
            
            # 결과 파싱
            parsed_results = []
            
            if results['documents'] and len(results['documents'][0]) > 0:
                documents = results['documents'][0]
                distances = results['distances'][0]
                metadatas = results['metadatas'][0]
                
                for doc, dist, meta in zip(documents, distances, metadatas):
                    # 거리를 유사도 점수로 변환 (낮은 거리 = 높은 유사도)
                    score = 1.0 / (1.0 + dist)
                    parsed_results.append((doc, score, meta))
            
            return parsed_results
            
        except Exception as e:
            logger.error(f"Failed to search: {str(e)}")
            return []
    
    def delete_collection(self):
        """컬렉션 삭제"""
        try:
            if self.client and self.collection:
                self.client.delete_collection(name=self.collection_name)
                logger.info(f"Deleted collection '{self.collection_name}'")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete collection: {str(e)}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """컬렉션 통계 정보 반환"""
        try:
            if not self.collection:
                return {}
            
            count = self.collection.count()
            
            stats = {
                "name": self.collection_name,
                "num_entities": count,
                "persist_directory": self.persist_directory
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {str(e)}")
            return {}
    
    def update_document(self,
                       doc_id: str,
                       text: Optional[str] = None,
                       embedding: Optional[List[float]] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        기존 문서 업데이트
        
        Args:
            doc_id: 문서 ID
            text: 새로운 텍스트 (선택사항)
            embedding: 새로운 임베딩 (선택사항)
            metadata: 새로운 메타데이터 (선택사항)
            
        Returns:
            성공 여부
        """
        try:
            if not self.collection:
                logger.error("Collection not initialized")
                return False
            
            update_params = {"ids": [doc_id]}
            
            if text is not None:
                update_params["documents"] = [text]
            if embedding is not None:
                update_params["embeddings"] = [embedding]
            if metadata is not None:
                update_params["metadatas"] = [metadata]
            
            self.collection.update(**update_params)
            
            logger.info(f"Updated document {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update document: {str(e)}")
            return False
    
    def delete_documents(self, doc_ids: List[str]) -> bool:
        """
        문서 삭제
        
        Args:
            doc_ids: 삭제할 문서 ID 리스트
            
        Returns:
            성공 여부
        """
        try:
            if not self.collection:
                logger.error("Collection not initialized")
                return False
            
            self.collection.delete(ids=doc_ids)
            
            logger.info(f"Deleted {len(doc_ids)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete documents: {str(e)}")
            return False