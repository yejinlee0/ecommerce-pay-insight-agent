from dotenv import load_dotenv

# [OpenAI] 현재 사용
from langchain_openai import ChatOpenAI
# [Ollama 전환 시] 아래 주석 해제 + OpenAI 관련 주석 처리
# from langchain_ollama import ChatOllama

from agent.schema_retriever import SchemaRetriever
from agent.prompt           import SQL_PROMPT, FEW_SHOT_EXAMPLES
from agent.sql_executor     import SQLExecutor
from agent.interpreter      import ResultInterpreter

load_dotenv()

class PayInsightAgent:
    """E-Commerce Pay-Insight Text2SQL Agent"""

    def __init__(self, db_path: str, metadata_path: str):
        print("Agent 초기화 중...")
        self.retriever   = SchemaRetriever(metadata_path)
        self.executor    = SQLExecutor(db_path)
        self.interpreter = ResultInterpreter()

        # [OpenAI] 현재 사용
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        # [Ollama 전환 시] 아래 주석 해제 + 위 줄 주석 처리
        # self.llm = ChatOllama(model="llama3.2", temperature=0)

        self.sql_chain = SQL_PROMPT | self.llm
        print("Agent 초기화 완료!")

    def query(self, question: str) -> dict:
        """자연어 질문 → SQL → 결과 → 인사이트 반환"""

        # 1. 관련 스키마 검색
        context = self.retriever.retrieve(question)

        # 2. SQL 생성
        sql_response = self.sql_chain.invoke({
            "question" : question,
            "few_shot" : FEW_SHOT_EXAMPLES,
            "context"  : context
        })
        sql = sql_response.content.strip()

        # 3. SQL 실행
        df, result_str = self.executor.execute(sql)

        # 4. 결과 해석
        if df.empty:
            insight = "SQL 실행에 실패했습니다. 질문을 다시 표현해주세요."
        else:
            insight = self.interpreter.interpret(question, result_str)

        return {
            "question" : question,
            "sql"      : sql,
            "dataframe": df,
            "insight"  : insight
        }


if __name__ == '__main__':
    agent = PayInsightAgent(
        db_path       = 'data/ecommerce_payinsight.duckdb',
        metadata_path = 'docs/schema_metadata.json'
    )

    questions = [
        "결제수단별 평균 결제금액은?",
        "지역별 평균 배송일은?",
        "배송 지연된 주문의 평균 리뷰 점수는?",
        "캠페인별 전환율은?",
        "Southeast 지역에서 가장 많이 팔린 카테고리 Top 5는?"
    ]

    for q in questions:
        print(f"\n{'='*55}")
        print(f"Q: {q}")
        result = agent.query(q)
        print(f"SQL: {result['sql']}")
        print(f"결과:\n{result['dataframe']}")
        print(f"인사이트: {result['insight']}")