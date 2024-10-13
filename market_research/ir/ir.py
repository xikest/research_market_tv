import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime
import yfinance as yf
import plotly.graph_objects as go
import plotly.subplots as sp
from datetime import datetime
import requests

class SONY_IR():
    def __init__(self):
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
                if check_url_exists(url):  # URL 
                                file_dict[f"20{filename.upper()}"] = url

        base_url = "https://www.sony.com/en/SonyInfo/IR/library/presen/strategy/pdf"
        years = range(2020, today.year + 1)  

        for year in years:
            for quarter in quarters:
                filename = f"{year}/qa_E"
                url = f"{base_url}/{filename}.pdf"
                if check_url_exists(url):  # URL
                    file_dict[filename.replace('/', '_').upper()] = url

        df = pd.DataFrame(list(file_dict.items()), columns=['filename', 'url'])
        df.loc[:,'year'] = df.filename.map(lambda x: x[:4])
        df.loc[:,"category"] = df.filename.map(lambda x:  "Strategy" if x[-1] == "E" else "Earning")
        df.loc[:,"quarter"]= df[df["category"] == "Earning"].filename.map(lambda x: x[4:6].upper())
        df.loc[:,"quarter"] = df["quarter"].fillna("-")
        return df 

        
    def plot_financials_with_margin(self, ticker='SONY'):
        def format_value(value):

            if value >= 1_000_000_000_000:  # 1T 
                return f'{value/1_000_000_000_000:.1f}T'
            elif value >= 1_000_000_000:  # 1B 
                return f'{value/1_000_000_000:.1f}B'
            elif value >= 1_000_000:  # 1M 
                return f'{value/1_000_000:.1f}M'
            elif value >= 1_000:  # 1K 
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
    
    def plot_usd_exchange(self):
        today = datetime.now()
        start_date = today.replace(year=today.year - 4)
        end_date = today

        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        usd_jpy = fdr.DataReader('FRED:DEXJPUS', start=start_date_str, end=end_date_str)  # USD/JPY 
        usd_mxn = fdr.DataReader('FRED:DEXMXUS', start=start_date_str, end=end_date_str)  # USD/MXN
        usd_myr = fdr.DataReader('FRED:DEXMAUS', start=start_date_str, end=end_date_str)  # USD/MYR 
        eur_usd = fdr.DataReader('FRED:DEXUSEU', start=start_date_str, end=end_date_str)  # EUR/USD 


        jpy_myr = usd_myr['DEXMAUS'] / usd_jpy['DEXJPUS']  # JPY/MYR
        jpy_mxn = usd_mxn['DEXMXUS'] / usd_jpy['DEXJPUS']  # JPY/MXN
        eur_jpy = eur_usd['DEXUSEU'] * usd_jpy['DEXJPUS']  # EUR/JPY


        fig = sp.make_subplots(
            rows=2, cols=1,  
            shared_xaxes=True,  
            subplot_titles=("USD/JPY and JPY/MXN", "EUR/JPY and JPY/MYR"),  
            specs=[[{"secondary_y": True}], [{"secondary_y": True}]] 
        )

        fig.add_trace(go.Scatter(x=usd_jpy.index, y=usd_jpy['DEXJPUS'], mode='lines', name='USD/JPY'), row=1, col=1)
        fig.add_trace(go.Scatter(x=jpy_mxn.index, y=jpy_mxn, mode='lines', name='JPY/MXN'), row=1, col=1, secondary_y=True)
        
        fig.add_trace(go.Scatter(x=eur_jpy.index, y=eur_jpy, mode='lines', name='EUR/JPY'), row=2, col=1)
        fig.add_trace(go.Scatter(x=jpy_myr.index, y=jpy_myr, mode='lines', name='JPY/MYR'), row=2, col=1, secondary_y=True)

        fig.update_layout(
            title="Exchange Rates",
            xaxis_title="",
            yaxis_title="",  # 첫 번째 y축 제목 설정
            template="plotly_dark",
            height=800  # 그래프 높이 설정
        )
        return fig

