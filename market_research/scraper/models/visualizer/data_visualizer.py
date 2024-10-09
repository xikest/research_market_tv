import pandas as pd
from tools.file import FileManager
import plotly.graph_objs as go
from .data_cleaner import DataCleaner
from market_research.scraper._visualization_scheme import BaseVisualizer
import requests
import plotly.io as pio


class DataVisualizer(BaseVisualizer):
    def __init__(self, df:pd.DataFrame=None, maker="", output_folder_path="results"):
        
        pio.templates.default='ggplot2'
        
        self.maker = maker
        super().__init__(output_folder_path = output_folder_path)
        FileManager.make_dir(output_folder_path)
        
        if df is not None:
            self.dc = DataCleaner(df)


    def price_map(self, data=None, return_data=False, return_fig=False):
        # 데이터 준비
        if data is not None and isinstance(data, pd.DataFrame):   
            data =  data
        else:
            data = self.dc.get_price_df().copy()
        data = data.dropna(subset=['price'])  #
        
        years = data['year'].unique()
        years = sorted(years)
        
        series_idx = data[['series', 'display type', 'year']]
        series_idx = series_idx.sort_values(by=['year',  'series'], ascending=True)
        all_series_dict = {}
        for year in series_idx.year.unique():
            df_year = series_idx[series_idx['year']==year]
            all_series_dict[year] = {key: value for key, value in zip(df_year['series'], df_year['display type'])}

        colors = ['#EF553B', '#00CC96', '#636EFA', '#CCFFFF', '#FFCCFF', '#FFFFCC']
        color_map = {year: colors[i] for i, year in enumerate(sorted(years, reverse=True))}


        markers = ['circle', 'square', 'diamond', 'pentagon', 'star', 'hexagon', 'cross', 'octagon', 'bowtie', 'hourglass', 'x',
                'triangle-up', 'triangle-down', 'triangle-left', 'triangle-right',
                'hexagon2', 'arrow-up', 'arrow-down', 
                'arrow-left', 'arrow-right']

        marker_map = {i: markers[i % len(markers)] for i in range(len(series_idx))}
        data['price_gap'] = data['price_gap'].fillna(0)
        data['price_gap'] = data['price_gap'].map(lambda x: int(x))

        data.loc[:, 'description'] = data.apply(lambda row: 
                    f"{row['description']}<br>release: ${row['price_original']}<br>price: ${row['price']} ({row['price_gap']}↓)"  
                                                if row['price_gap'] != 0 else 
                                                f"{row['description']}<br>price: ${row['price']}" , axis=1)

        # 그래프 생성
        fig = go.Figure()

        for year in years:
            
            data_year = data[data['year']==year]
            series_dict = all_series_dict.get(year)
            for seq, series, display in zip(range(len(series_dict.keys())), series_dict.keys(), series_dict.values()):
                data_series = data_year[data_year['series'] == series].copy()
                fig.add_trace(go.Scatter(
                    x=data_series['size'],
                    y=data_series['price'],
                    mode='markers',
                    marker=dict(
                        size=12,
                        color='rgba(211, 211, 211, 0.6)',  
                        symbol=marker_map[seq],
                        opacity=0.8,  
                        line=dict(width=3, color='black')
                    ),
                    text=data_series['description'],  
                    hoverinfo='text',  
                    name=f'{series.upper()}',
                    # name=f'{series.upper()} [{display.capitalize()}]',
                    visible='legendonly'  # 사이즈 마커는 기본적으로 숨김
                ))


            fig.add_trace(go.Scatter(
                x=data_year['size'],
                y=data_year['price'],
                mode='markers',
                marker=dict(size=10,
                            color=color_map[year],
                            symbol='circle'),
                error_y=dict(
                    type='data',
                    symmetric=False,
                    arrayminus=[0]*len(data),
                    array=data_year['price_gap'],
                    color=color_map[year],
                    thickness=1,
                    width=5
                ),
                text=data_year['description'],
                hoverinfo='text',
                name=str(year),
                showlegend=True
            ))


        size_categories = sorted(data['size'].unique())
        ticks_below_3000 = list(range(0, 3001, 500))
        ticks_above_3000 = list(range(4000, max(int(data['price_original'].max()), int(data['price'].max())) + 2000, 1000))
        tickvals = ticks_below_3000 + ticks_above_3000

        # 레이아웃 설정
        fig.update_layout(
            title='Price map',
            xaxis_title='Size (Inch)',
            yaxis_title='Current Price ($)',
            legend_title='Year',
            showlegend=True,
            template='simple_white',
            xaxis=dict(
                type='category',
                categoryorder='array',
                categoryarray=size_categories,
                range = [-1, len(size_categories)],
                showgrid=False

            ),
            yaxis=dict(
                range=[0, max(data['price_original'].max(),
                            data['price'].max()) + 1000],
                showgrid=True,
                tickmode='array',  
                tickvals=tickvals
            ),
            width=1000,
            height= 800,
            hovermode='closest',
            legend=dict(
                traceorder='reversed' 
            )
        )
        fig.write_html(self.output_folder/f"{self.maker}_pricemap.html")
        
        if return_fig:
            return fig
        else:
            fig.show()
        if return_data:
            data['series'] = data['series'].map(lambda x: f'{self.maker}_{x}')
            return data


    def heatmap_spec(self, col_selected:list=None, display_types:str=None, cmap="Blues", return_fig=False):
        if col_selected is None:
            try:
                file_path = "https://raw.githubusercontent.com/xikest/research_market_tv/main/json/col_heatmap.json"
                response = requests.get(file_path)
                data = response.json()
                col_selected = data.get(self.maker)
            except Exception as e:
                file_path = "col_heatmap.json"
                with open(file_path, 'r') as file:
                    import json
                    data = json.load(file)
                col_selected = data.get(self.maker)
                print(e)
        else:   
            if isinstance(col_selected, list):
                col_selected = col_selected
                col_selected =[c.lower() for c in col_selected]
            else:
                raise ValueError
        
        data_df = self.dc.get_df_cleaned().copy()
        available_columns = [col for col in col_selected if col in data_df.columns]
        missing_columns = [col for col in col_selected if col not in data_df.columns]
        if missing_columns:
            print("The following columns are missing from the DataFrame:")
            for col in missing_columns:
                print(col)

        data_df = data_df[available_columns]
        if display_types is not None:
            condition = data_df.index.get_level_values('display type').str.contains('|'.join(display_types), case=False, na=False)
            data_df = data_df[condition]
        data_df = data_df.mask(data_df == '-', 0)
        data_df = data_df.fillna(0)
        
        data_df = data_df[data_df.columns[::-1]]
        
        mask_data = data_df.reset_index().copy()
        data_df = data_df.map(lambda x: 1 if isinstance(x, str) else x)
        idx_names = data_df.index.names
        
        data_df['row_sum'] = data_df.sum(axis=1)
        data_df = data_df.reset_index().sort_values(by = idx_names + ['row_sum'], ascending=False).drop_duplicates(subset=idx_names).drop(['row_sum'], axis=1)
        mask_data = mask_data.loc[data_df.index, :]

        data_df = data_df.set_index(idx_names)
        data_df = data_df.sort_index(ascending=True)
        self.data_df = data_df
        heatmap_data = data_df.T
        
        mask_data = mask_data.replace(0, '').set_index(idx_names).sort_index(ascending=True).T
        x_labels = [f"{str(idx[1]).upper()} ({str(idx[0])})" for idx in heatmap_data.columns]

        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,  
            x=x_labels,  
            y=heatmap_data.index.str.capitalize(),   
            colorscale=cmap,         
            showscale=False,
            zmax=1,                  
            hoverinfo='text',        
            hovertemplate='<b>%{customdata}</b><extra></extra>',
            customdata=mask_data.values
            ))

        fig.update_layout(
            title=f"{self.maker} spec",
            xaxis=dict(title='',tickangle=90),
            yaxis=dict(title='',tickangle=0),
            width=800,  
            height=800  
        )

        fig.write_html(self.output_folder/f"{self.maker}_heatmap.html")

        if return_fig:
            return fig
        else:
            fig.show()  
           

    def plot_headertxt(self, data=None, return_fig=False):
        if data is not None and isinstance(data, pd.DataFrame):   
            data = data
        else:
            data = self.dc.get_price_df().copy()

        data['year'] = data['year'].astype('str')
        data = data[['year', 'series', 'text0']].drop_duplicates().dropna()
        data = data.groupby(['text0', 'year']).agg({
            'series': '/ '.join 
        }).reset_index()
        data = data.sort_values(by=['year', 'series'], ascending=[False, True]).reset_index(drop=True)
        marker_size = 16  

        fig = go.Figure()

        for _, group in data.groupby('year'):
            fig.add_trace(go.Scatter(
                x=[group['year'].iloc[0]] * len(group),  
                y=group['series'].str.upper(),  
                mode="markers+text",
                text=group['text0'].str.capitalize(), 
                textposition="middle right",  
                marker=dict(size=marker_size),  
                hovertext=group['series'].str.upper(), 
                hoverinfo="text",
                textfont=dict(size=16),  
                name=group['year'].iloc[0] 
            ))
            
        # 최대 연도 구하기
        min_year = data['year'].astype(int).min()
        dummy_years = [str(min_year + i + 1) for i in range(30)]

        # 더미 연도 추가
        for year in dummy_years:
            fig.add_trace(go.Scatter(
                x=[year] * 1, 
                y=[None],  
                mode='markers',  
                marker=dict(size=marker_size),  
                showlegend=False  
            ))
            
        # 레이아웃 업데이트
        fig.update_layout(
            xaxis=dict(
                showgrid=False,
                visible=False,
                categoryorder='array',  # 카테고리 순서 설정
                categoryarray=list(reversed(sorted(data['year'].unique())))  # 연도를 역순으로 설정
            ),
            yaxis=dict(showgrid=False),
            showlegend=True,
            height=600,
            width=800,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='black'),
            legend=dict(
                orientation="h",    
                yanchor="top",      
                xanchor="center",   
                x=0.5,              
                y=0               
            )
        )
        
        if return_fig:
            return fig

        fig.show()