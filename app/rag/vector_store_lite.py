"""
Milvus Lite 벡터 스토어 모듈

경량화된 임베디드 Milvus 사용
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility,
    MilvusClient
)
import json

logger = logging.getLogger(__name__)


class MilvusLiteVectorStore:
    """Milvus Lite 벡터 데이터베이스 관리 클래스"""
    
    def __init__(self,
                 db_file: str = "./milvus_lite.db",
                 collection_name: str = "gaia_bt_documents",
                 dimension: int = 1024):  # mxbai-embed-large의 기본 차원
        """
        Args:
            db_file: Milvus Lite 데이터베이스 파일 경로
            collection_name: 컬렉션 이름
            dimension: 벡터 차원 수
        """
        self.db_file = db_file
        self.collection_name = collection_name
        self.dimension = dimension
        self.client = None
        
    def connect(self):
        """Milvus Lite 클라이언트 초기화"""
        try:
            # Milvus Lite 클라이언트 생성
            self.client = MilvusClient(self.db_file)
            logger.info(f"Connected to Milvus Lite at {self.db_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Milvus Lite: {str(e)}")
            return False
    
    def create_collection(self):
        """컬렉션 생성"""
        try:
            if not self.client:
                logger.error("Milvus client not initialized")
                return False
            
            # 컬렉션이 이미 존재하는지 확인
            if self.client.has_collection(collection_name=self.collection_name):
                logger.info(f"Collection '{self.collection_name}' already exists")
                return True
            
            # 컬렉션 생성
            self.client.create_collection(
                collection_name=self.collection_name,
                dimension=self.dimension,
                metric_type="IP",  # Inner Product
                consistency_level="Strong"
            )
            
            logger.info(f"Created collection '{self.collection_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection: {str(e)}")
            return False
    
    def insert_documents(self, 
                        texts: List[str],
                        embeddings: List[List[float]],
                        metadata: Optional[List[Dict[str, Any]]] = None) -> bool:
        """
        문서와 임베딩을 Milvus에 삽입
        
        Args:
            texts: 원본 텍스트 리스트
            embeddings: 임베딩 벡터 리스트
            metadata: 메타데이터 리스트
            
        Returns:
            성공 여부
        """
        try:
            if not self.client:
                logger.error("Client not initialized")
                return False
            
            # 메타데이터 처리
            if metadata is None:
                metadata = [{}] * len(texts)
            
            # 데이터 준비
            data = []
            for i, (text, embedding, meta) in enumerate(zip(texts, embeddings, metadata)):
                data.append({
                    "id": i,
                    "vector": embedding,
                    "text": text,
                    "metadata": json.dumps(meta)
                })
            
            # 데이터 삽입
            self.client.insert(
                collection_name=self.collection_name,
                data=data
            )
            
            logger.info(f"Inserted {len(texts)} documents into collection")
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert documents: {str(e)}")
            return False
    
    def search(self, 
               query_embedding: List[float],
               top_k: int = 5,
               filter_expr: Optional[str] = None) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        벡터 유사도 검색
        
        Args:
            query_embedding: 쿼리 임베딩 벡터
            top_k: 반환할 결과 수
            filter_expr: 필터 표현식
            
        Returns:
            [(텍스트, 점수, 메타데이터)] 리스트
        """
        try:
            if not self.client:
                logger.error("Client not initialized")
                return []
            
            # 검색 실행
            results = self.client.search(
                collection_name=self.collection_name,
                data=[query_embedding],
                limit=top_k,
                output_fields=["text", "metadata"],
                filter=filter_expr
            )
            
            # 결과 파싱
            parsed_results = []
            if results and len(results) > 0:
                for result in results[0]:
                    text = result.get("entity", {}).get("text", "")
                    score = result.get("distance", 0.0)
                    metadata_str = result.get("entity", {}).get("metadata", "{}")
                    
                    try:
                        metadata = json.loads(metadata_str)
                    except:
                        metadata = {}
                    
                    parsed_results.append((text, score, metadata))
            
            return parsed_results
            
        except Exception as e:
            logger.error(f"Failed to search: {str(e)}")
            return []
    
    def delete_collection(self):
        """컬렉션 삭제"""
        try:
            if self.client and self.client.has_collection(self.collection_name):
                self.client.drop_collection(self.collection_name)
                logger.info(f"Deleted collection '{self.collection_name}'")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete collection: {str(e)}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """컬렉션 통계 정보 반환"""
        try:
            if not self.client:
                return {}
            
            # 컬렉션 정보 가져오기
            stats = {
                "name": self.collection_name,
                "db_file": self.db_file,
                "exists": self.client.has_collection(self.collection_name)
            }
            
            if stats["exists"]:
                # 문서 수 가져오기
                info = self.client.describe_collection(self.collection_name)
                stats["num_entities"] = info.get("num_entities", 0)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {str(e)}")
            return {}