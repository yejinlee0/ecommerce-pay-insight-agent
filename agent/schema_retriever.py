import json
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# [OpenAI] 현재 사용
from openai import OpenAI
# [Ollama 전환 시] 아래 주석 해제 + OpenAI 관련 주석 처리
# from langchain_ollama import OllamaEmbeddings

class SchemaRetriever:
    """스키마 메타데이터를 Qdrant에 저장하고 관련 컨텍스트를 검색하는 클래스"""

    COLLECTION = "schema_metadata"

    def __init__(self, metadata_path: str):
        self.client   = QdrantClient(":memory:")

        # [OpenAI] 현재 사용
        self.openai = OpenAI()
        # [Ollama 전환 시] 아래 주석 해제 + 위 줄 주석 처리
        # self.embeddings = OllamaEmbeddings(model="nomic-embed-text")

        self.metadata = self._load_metadata(metadata_path)
        self._build_index()

    def _load_metadata(self, path: str) -> dict:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _embed(self, text: str) -> list:
        # [OpenAI] 현재 사용
        response = self.openai.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
        # [Ollama 전환 시] 아래 주석 해제 + 위 줄 주석 처리
        # return self.embeddings.embed_query(text)

    def _build_index(self):
        """스키마 메타데이터 + 샘플 질문을 Qdrant에 임베딩"""
        points = []
        idx    = 0

        for table_name, table_info in self.metadata['tables'].items():
            text = f"테이블: {table_name}\n설명: {table_info['description']}\n"
            text += "컬럼:\n"
            for col, desc in table_info['columns'].items():
                text += f"  - {col}: {desc}\n"

            points.append(PointStruct(
                id      = idx,
                vector  = self._embed(text),
                payload = {"type": "schema", "table": table_name, "content": text}
            ))
            idx += 1

        for sample in self.metadata['sample_questions']:
            text = f"질문: {sample['question']}\nSQL: {sample['sql']}"
            points.append(PointStruct(
                id      = idx,
                vector  = self._embed(text),
                payload = {"type": "sample", "question": sample['question'], "sql": sample['sql'], "content": text}
            ))
            idx += 1

        # [OpenAI] text-embedding-3-small 벡터 크기 1536
        # [Ollama 전환 시] size=768 으로 변경
        self.client.recreate_collection(
            collection_name = self.COLLECTION,
            vectors_config  = VectorParams(size=1536, distance=Distance.COSINE)
        )
        self.client.upsert(collection_name=self.COLLECTION, points=points)
        print(f"Qdrant 인덱스 구축 완료: {len(points)}개 벡터")

    def retrieve(self, question: str, top_k: int = 3) -> str:
        """질문과 유사한 스키마/샘플 검색 후 컨텍스트 문자열 반환"""
        query_vector = self._embed(question)
        results = self.client.query_points(
            collection_name = self.COLLECTION,
            query           = query_vector,
            limit           = top_k
        ).points

        context = "=== 관련 스키마 및 예시 ===\n"
        for r in results:
            context += r.payload['content'] + "\n---\n"
        return context