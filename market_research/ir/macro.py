import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class MACRO:
    @staticmethod
    def plot_economic_indicator(key:str):
        today = datetime.now()
        start_date = today.replace(year=today.year - 5)  # 5년 전부터 시작
        end_date = today

        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        # FRED에서 데이터 가져오기
        data = fdr.DataReader(f'FRED:{key}', start=start_date_str, end=end_date_str)
        data = data.resample("QE").sum()  # 분기별 총합 계산

        # 전년 동기 데이터 생성
        data_previous = data.shift(4).iloc[-4:]  

        # 최근 4개 분기 데이터 필터링
        recent_data = data.iloc[-4:]

        fig = go.Figure()

        fig.add_trace(go.Bar(x=data_previous.index, y=data_previous.squeeze(), name='Previous Year', opacity=0.5, showlegend=False))
        fig.add_trace(go.Bar(x=recent_data.index, y=recent_data.squeeze(), name='Current Year', showlegend=False))

        # 그래프 레이아웃 설정
        fig.update_layout(
            title=f'{key} - Comparison of Current Quarter and Previous Year',
            xaxis_title='',
            title_font=dict(size=10),
            margin=dict(t=25, b=0)
        )

        # X축 형식 설정
        fig.update_xaxes(
            tickvals=recent_data.index.tolist() + data_previous.index.tolist(),  # X축 값 설정
            ticktext=[f'Q{((x.month-1)//3)+1}' for x in recent_data.index] + 
                      [f'Q{((x.month-1)//3)+1}' for x in data_previous.index],  # 분기 형식으로 텍스트 설정
        )
        fig.update_yaxes(type='log')
        return fig