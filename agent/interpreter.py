# [OpenAI] 현재 사용
from langchain_openai import ChatOpenAI
# [Ollama 전환 시] 아래 주석 해제 + OpenAI 관련 주석 처리
# from langchain_ollama import ChatOllama

from agent.prompt import INTERPRET_PROMPT

class ResultInterpreter:
    """SQL 결과를 LLM으로 자연어 해석하는 클래스"""

    def __init__(self):
        # [OpenAI] 현재 사용
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        # [Ollama 전환 시] 아래 주석 해제 + 위 줄 주석 처리
        # self.llm = ChatOllama(model="llama3.2", temperature=0)

        self.chain = INTERPRET_PROMPT | self.llm

    def interpret(self, question: str, result: str) -> str:
        response = self.chain.invoke({
            "question": question,
            "result"  : result
        })
        return response.content