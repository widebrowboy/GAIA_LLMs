"""
Milvus 벡터 스토어 모듈

벡터 데이터베이스 연결 및 관리
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility
)
import numpy as np

logger = logging.getLogger(__name__)


class MilvusVectorStore:
    """Milvus 벡터 데이터베이스 관리 클래스"""
    
    def __init__(self,
                 host: str = "localhost",
                 port: str = "19530",
                 collection_name: str = "gaia_bt_documents",
                 dimension: int = 1024):  # mxbai-embed-large의 기본 차원
        """
        Args:
            host: Milvus 서버 호스트
            port: Milvus 서버 포트
            collection_name: 컬렉션 이름
            dimension: 벡터 차원 수
        """
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.dimension = dimension
        self.collection = None
        
    def connect(self):
        """Milvus 서버에 연결"""
        try:
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port
            )
            logger.info(f"Connected to Milvus at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {str(e)}")
            return False
    
    def create_collection(self):
        """컬렉션 생성"""
        try:
            # 컬렉션이 이미 존재하는지 확인
            if utility.has_collection(self.collection_name):
                logger.info(f"Collection '{self.collection_name}' already exists")
                self.collection = Collection(self.collection_name)
                return True
            
            # 스키마 정의
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dimension),
                FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=65535)
            ]
            
            schema = CollectionSchema(
                fields=fields,
                description="GAIA-BT document embeddings for RAG"
            )
            
            # 컬렉션 생성
            self.collection = Collection(
                name=self.collection_name,
                schema=schema,
                consistency_level="Strong"
            )
            
            # 인덱스 생성
            index_params = {
                "metric_type": "IP",  # Inner Product
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024}
            }
            
            self.collection.create_index(
                field_name="embedding",
                index_params=index_params
            )
            
            logger.info(f"Created collection '{self.collection_name}' with index")
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
            if not self.collection:
                logger.error("Collection not initialized")
                return False
            
            # 메타데이터 처리
            if metadata is None:
                metadata = [{}] * len(texts)
            
            # 메타데이터를 JSON 문자열로 변환
            import json
            metadata_strs = [json.dumps(m) for m in metadata]
            
            # 데이터 삽입
            entities = [
                texts,
                embeddings,
                metadata_strs
            ]
            
            self.collection.insert(entities)
            self.collection.flush()
            
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
            if not self.collection:
                logger.error("Collection not initialized")
                return []
            
            # 컬렉션 로드
            self.collection.load()
            
            # 검색 파라미터
            search_params = {
                "metric_type": "IP",
                "params": {"nprobe": 10}
            }
            
            # 검색 실행
            results = self.collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                output_fields=["text", "metadata"],
                expr=filter_expr
            )
            
            # 결과 파싱
            parsed_results = []
            for hits in results:
                for hit in hits:
                    text = hit.entity.get("text", "")
                    score = hit.score
                    metadata_str = hit.entity.get("metadata", "{}")
                    
                    import json
                    metadata = json.loads(metadata_str)
                    
                    parsed_results.append((text, score, metadata))
            
            return parsed_results
            
        except Exception as e:
            logger.error(f"Failed to search: {str(e)}")
            return []
    
    def delete_collection(self):
        """컬렉션 삭제"""
        try:
            if utility.has_collection(self.collection_name):
                utility.drop_collection(self.collection_name)
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
            
            self.collection.flush()
            stats = {
                "name": self.collection_name,
                "num_entities": self.collection.num_entities,
                "loaded": self.collection.is_empty == False
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {str(e)}")
            return {}