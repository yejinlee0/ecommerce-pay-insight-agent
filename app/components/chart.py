import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 차트 색상
COLOR_SEQUENCE = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
COLOR_SCALE    = 'Blues'

def _detect_chart_type(df: pd.DataFrame, question: str) -> str:
    # 질문 키워드와 데이터 구조로 차트 타입 결정
    q = question.lower()
    cols   = df.columns.tolist()
    n_cols = len(cols)
    n_rows = len(df)

    # 시계열
    time_cols = [c for c in cols if c in ('year', 'month', 'quarter', 'weekday')]
    if time_cols:
        return 'line'

    # 질문 키워드 기반
    if any(k in q for k in ['비율', '분포', '구성', '차지']):
        return 'pie'
    if any(k in q for k in ['추이', '변화', '트렌드']):
        return 'line'
    if any(k in q for k in ['비교', 'vs', '차이']):
        return 'bar_group'
    if any(k in q for k in ['top', '순위', '많은', '높은', '낮은']):
        return 'bar_h'

    # 데이터 구조 기반
    if n_cols == 1:
        return 'indicator'
    if n_cols == 2:
        return 'bar_h' if n_rows > 6 else 'bar'
    if n_cols >= 3:
        return 'bar_group'

    return 'bar'


def auto_chart(df: pd.DataFrame, question: str):
    # DataFrame과 질문으로 적절한 차트 자동 생성

    if df is None or df.empty or 'error' in df.columns:
        return None

    cols      = df.columns.tolist()
    n_cols    = len(cols)
    chart_type = _detect_chart_type(df, question)

    # 시계열 라인차트
    if chart_type == 'line':
        time_cols = [c for c in cols if c in ('year', 'month', 'quarter', 'weekday')]
        x_col     = time_cols[-1] if time_cols else cols[0]
        y_cols    = [c for c in cols if c not in time_cols and c != x_col]

        if len(y_cols) == 1:
            fig = px.line(
                df, x=x_col, y=y_cols[0],
                title=question,
                markers=True,
                color_discrete_sequence=COLOR_SEQUENCE,
                labels={x_col: x_col, y_cols[0]: y_cols[0]}
            )
        else:
            fig = px.line(
                df, x=x_col, y=y_cols,
                title=question,
                markers=True,
                color_discrete_sequence=COLOR_SEQUENCE
            )
        fig.update_layout(xaxis_title=x_col, hovermode='x unified')
        return fig

    # 파이차트
    if chart_type == 'pie':
        cat_col = cols[0]
        val_col = cols[1] if n_cols > 1 else cols[0]
        fig = px.pie(
            df,
            names  = cat_col,
            values = val_col,
            title  = question,
            color_discrete_sequence = COLOR_SEQUENCE,
            hole   = 0.3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return fig

    # 가로 막대차트
    if chart_type == 'bar_h':
        cat_col = cols[0]
        val_col = cols[1]
        fig = px.bar(
            df.sort_values(val_col),
            x           = val_col,
            y           = cat_col,
            orientation = 'h',
            title       = question,
            color       = val_col,
            color_continuous_scale = COLOR_SCALE,
            text        = val_col
        )
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig.update_layout(yaxis_title='', xaxis_title=val_col)
        return fig

    # 세로 막대차트
    if chart_type == 'bar':
        cat_col = cols[0]
        val_col = cols[1]
        fig = px.bar(
            df,
            x     = cat_col,
            y     = val_col,
            title = question,
            color = val_col,
            color_continuous_scale = COLOR_SCALE,
            text  = val_col
        )
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig.update_layout(xaxis_title='', yaxis_title=val_col)
        return fig

    # 그룹 막대차트
    if chart_type == 'bar_group':
        cat_col  = cols[0]
        val_cols = cols[1:]
        fig = px.bar(
            df,
            x        = cat_col,
            y        = val_cols,
            title    = question,
            barmode  = 'group',
            color_discrete_sequence = COLOR_SEQUENCE
        )
        fig.update_layout(xaxis_title='', legend_title='지표')
        return fig

    # 단일 수치 지표
    if chart_type == 'indicator':
        fig = go.Figure(go.Indicator(
            mode  = "number",
            value = float(df.iloc[0, 0]),
            title = {"text": question, "font": {"size": 16}},
            number = {"font": {"size": 48}}
        ))
        fig.update_layout(height=200)
        return fig

    return None