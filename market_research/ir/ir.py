import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import requests

class SONY_IR():
    def __init__(self):
        # self.tas = TextAnalysis()
        
        self.cleaning_words = [  #사전 필터링하는 단어
                            "half","fy2021","fy2020", "month","way", "input","earnings",
                            "forecast","please","terms","market","g","ns", "unit","assets",
                            "fy2022","levels","q","fy2023","numbers","result","units",
                            "factors","costs","ss","q1","part",'segment', 'quarter', 
                            'statements', 'business', 'question', 'yen', 'year', 'sony', 'results',
                            "end","q2","questioner",
                            "session","fy2024",
                            # "sale","plan","capacity","growth","demand",
                            "outlook","increase","investment",
                            "example","rate","flow","time","a2","a1","sfh","r","dtc", "statement",
                            "plan", "tax", "value", "term","capital", "growth","company","group", "service",
                            "risk","profit","minotrity"
                        ]     
        
        
        self.replacement_mapping = {  #사전에 교체하는 단어
                            "games": "game",
                            "plans": "plan",
                            "sensors": "sensor",
                            "changes": "change",
                            "risks": "risk",
                            "services": "service",
                            "margins": "margin",
                            "profits": "profit",
                            "wafers": "wafer",
                            "sizes": "size",
                            "customers": "customer",
                            "applications": "application",
                            "shortages": "shortage",
                            "expenses": "expense",
                            "sales":"sale",
                            "titles":"title",
                            "conditions":"condition",
                            "prices":"price",
                            "investments":"investment",
                            "rates":"rate",
                            "inventories":"inventory",
                            "uncertainties":"uncertainty",
                            "cameras":"camera",
                            "opportunities":"opportunity",
                            "volumes":"volume",
                            "costs":"cost",
                            "technologies":"technology",
                            "employees":"employee",
                            "companies":"company",
                            "creators":"creator",
                            "challenges":"challenge",
                            "businesses":"business",
                            "years":"year",
                            "electronics":"electronic",
                            "strategies":"strategy",
                            "electronics":"electronic",
                            "targets":"target",
                            "statements":"statement"
                        }
        pass

    def get_ir_script(self) -> dict:
        def check_url_exists(url: str) -> bool:
            try:
                response = requests.head(url)
                # 200 OK
                return response.status_code == 200
            except requests.RequestException:
                return False
        
        today = datetime.now()
        start_date = today.replace(year=today.year - 4)

        file_dict = {}
        
        base_url = "https://www.sony.com/en/SonyInfo/IR/library/presen/er/pdf/"
        years = range(start_date.year, today.year + 1)  
        quarters = range(1, 5)
        for year in years:
            for quarter in quarters:
                filename = f"{year%100}q{quarter}_qa"  
                url = f"{base_url}{filename}.pdf"
                if check_url_exists(url):  # URL 존재 여부 확인
                                file_dict[f"20{filename.upper()}"] = url

        base_url = "https://www.sony.com/en/SonyInfo/IR/library/presen/strategy/pdf"
        years = range(2020, today.year + 1)  

        for year in years:
            for quarter in quarters:
                filename = f"{year}/qa_E"
                url = f"{base_url}/{filename}.pdf"
                if check_url_exists(url):  # URL 존재 여부 확인
                    file_dict[filename.replace('/', '_').upper()] = url

        df = pd.DataFrame(list(file_dict.items()), columns=['filename', 'url'])
        df.loc[:,'year'] = df.filename.map(lambda x: x[:4])
        df.loc[:,"category"] = df.filename.map(lambda x:  "Strategy" if x[-1] == "E" else "Earning")
        df.loc[:,"quarter"]= df[df["category"] == "Earning"].filename.map(lambda x: x[4:6].upper())
        df.loc[:,"quarter"] = df["quarter"].fillna("-")
        return df 
        
    def plot_financials_with_margin(self, ticker='SONY'):
        def format_value(value):
            """ 숫자를 K, M, T 단위로 포맷팅하는 함수 """
            if value >= 1_000_000_000_000:  # 1T 이상
                return f'{value/1_000_000_000_000:.1f}T'
            elif value >= 1_000_000_000:  # 1B 이상
                return f'{value/1_000_000_000:.1f}B'
            elif value >= 1_000_000:  # 1M 이상
                return f'{value/1_000_000:.1f}M'
            elif value >= 1_000:  # 1K 이상
                return f'{value/1_000:.1f}K'
            else:
                return str(value)
                
        
        stock = yf.Ticker(ticker)
        financials = stock.financials
        
        operating_income = financials.loc['Operating Income'].dropna()
        total_revenue = financials.loc['Total Revenue'].dropna()

        latest_quarter = sorted(operating_income.index, reverse=True)[0]
        cols = sorted(stock.quarterly_financials.columns)
        financials_q = stock.quarterly_financials[cols[cols.index(latest_quarter) + 1:]]
        
        operating_income_q = financials_q.loc['Operating Income'].cumsum()
        total_revenue_q = financials_q.loc['Total Revenue'].cumsum()

        operating_income = pd.concat([operating_income_q, operating_income], axis=0)
        total_revenue = pd.concat([total_revenue_q, total_revenue], axis=0)

        operating_income.index = pd.to_datetime(operating_income.index)
        total_revenue.index = pd.to_datetime(total_revenue.index)

        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=total_revenue.index, 
            y=total_revenue.values, 
            name='Total Revenue',
            text=[format_value(val) for val in total_revenue.values],  
            textposition='auto',
            textfont=dict(color='black'), 
            hoverinfo='none'    
        ))
        
        fig.add_trace(go.Bar(
            x=operating_income.index, 
            y=operating_income.values, 
            name='Operating Income',
            text=[format_value(val) for val in operating_income.values], 
            textposition='outside',
            textfont=dict(color='white'), 
            hoverinfo='none'    
        ))

        fig.update_layout(
            title=f"{ticker} Financials (Revenue, Operating Income)",
            xaxis_title="Date",
            yaxis_title="Amount (in USD)",
            barmode='overlay', 
            legend=dict(
                x=0,  
                y=1,  
                traceorder='normal',
                orientation='v'  
            ),
            xaxis=dict(
                tickformat="%b %Y",  
                tickvals=total_revenue.index,  
                ticktext=total_revenue.index.strftime("%b %Y")  
            ),
        )
        return fig
    
    def plot_usd_jpy_and_japan_gdp(self):
        today = datetime.now()
        start_date = today.replace(year=today.year - 4)
        end_date = today

        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        usd_jpy = fdr.DataReader('FRED:DEXJPUS',  start=start_date_str, end=end_date_str)  # USD/JPY 환율
        gdp_japan = fdr.DataReader('FRED:JPNNGDP', start=start_date_str, end=end_date_str)  # 일본 GDP

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=usd_jpy.index, y=usd_jpy['DEXJPUS'], mode='lines', name='USD/JPY'))
        fig.add_trace(go.Scatter(x=gdp_japan.index, y=gdp_japan['JPNNGDP'], mode='lines', name='Japan GDP', yaxis='y2'))
        
        fig.update_layout(
            title="USD/JPY Exchange Rate and Japan GDP",
            xaxis_title="Date",
            yaxis_title="USD/JPY Exchange Rate",
            yaxis2=dict(title="Japan GDP", overlaying='y', side='right'),
            legend=dict(x=0, y=1.1),
            template="plotly_dark"
        )
        
        return fig
