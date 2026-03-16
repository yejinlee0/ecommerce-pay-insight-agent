import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from dotenv import load_dotenv

from agent.agent              import PayInsightAgent
from app.components.chart     import auto_chart
from app.components.chat      import render_chat_history
from app.components.sentiment import get_sentiment_summary

load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title = "E-Commerce Pay Insight Agent",
    page_icon  = "💳",
    layout     = "wide"
)

# Agent 초기화
@st.cache_resource
def load_agent():
    return PayInsightAgent(
        db_path       = 'data/ecommerce_payinsight.duckdb',
        metadata_path = 'docs/schema_metadata.json'
    )

agent = load_agent()

# 사이드바
with st.sidebar:
    st.title("💳 Pay Insight Agent")
    st.caption("E-Commerce 결제 데이터 분석")
    st.divider()

    # 감성 분석 요약
    st.subheader("📊 리뷰 감성 분석")
    sentiment = get_sentiment_summary()
    st.dataframe(sentiment['summary'], use_container_width=True, hide_index=True)

    st.divider()

    st.subheader("🗺️ 지역별 평균 리뷰")
    st.dataframe(sentiment['regional'], use_container_width=True, hide_index=True)

    st.divider()

    st.subheader("🚚 배송 지연 영향")
    st.dataframe(sentiment['delay_impact'], use_container_width=True, hide_index=True)

    st.divider()

    # 샘플 질문 버튼
    st.subheader("💡 샘플 질문")
    sample_questions = [
        "결제수단별 평균 결제금액은?",
        "지역별 평균 배송일은?",
        "캠페인별 전환율은?",
        "월별 주문 수 추이는?",
        "배송 지연된 주문의 평균 리뷰 점수는?",
        "가격대별 평균 리뷰 점수는?",
    ]
    for q in sample_questions:
        if st.button(q, use_container_width=True):
            st.session_state['input'] = q

# 메인 영역
st.title("💳 E-Commerce Pay Insight Agent")
st.caption("자연어로 질문하면 AI가 SQL 생성 → 차트 → 인사이트를 자동으로 분석합니다.")

# 채팅 히스토리 초기화
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# 채팅 히스토리 렌더링
render_chat_history(st.session_state['messages'])

# 입력창
user_input = st.chat_input("질문을 입력하세요. 예: 결제수단별 평균 결제금액은?")

# 사이드바 버튼으로 입력된 경우
if 'input' in st.session_state and st.session_state['input']:
    user_input = st.session_state['input']
    st.session_state['input'] = None

# 질문 처리
if user_input:
    # 사용자 메시지 추가
    st.session_state['messages'].append({
        'role'   : 'user',
        'content': user_input
    })

    with st.chat_message("user"):
        st.write(user_input)

    # Agent 실행
    with st.chat_message("assistant"):
        with st.spinner("분석 중..."):
            result = agent.query(user_input)

        # 차트 생성
        chart = auto_chart(result['dataframe'], user_input)

        # 결과 표시
        st.write(result['insight'])

        with st.expander("🔍 생성된 SQL 보기"):
            st.code(result['sql'], language='sql')

        if chart is not None:
            st.plotly_chart(chart, use_container_width=True)

        if not result['dataframe'].empty:
            with st.expander("📊 데이터 테이블 보기"):
                st.dataframe(result['dataframe'], use_container_width=True)

    # 어시스턴트 메시지 저장
    st.session_state['messages'].append({
        'role'     : 'assistant',
        'content'  : result['insight'],
        'sql'      : result['sql'],
        'chart'    : chart,
        'dataframe': result['dataframe']
    })