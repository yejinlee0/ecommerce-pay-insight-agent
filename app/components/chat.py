import streamlit as st

def render_chat_history(messages: list):
    # 채팅 히스토리 렌더링
    for msg in messages:
        with st.chat_message(msg['role']):
            st.write(msg['content'])

            # SQL 토글
            if 'sql' in msg and msg['sql']:
                with st.expander("생성된 SQL 보기"):
                    st.code(msg['sql'], language='sql')

            # 차트
            if 'chart' in msg and msg['chart'] is not None:
                st.plotly_chart(msg['chart'], use_container_width=True)

            # 데이터프레임
            if 'dataframe' in msg and msg['dataframe'] is not None:
                if not msg['dataframe'].empty:
                    with st.expander("데이터 테이블 보기"):
                        st.dataframe(msg['dataframe'], use_container_width=True)