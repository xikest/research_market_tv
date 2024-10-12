import pandas as pd
from tools.file import FileManager
import plotly.graph_objs as go
from .data_cleaner import DataCleaner
from market_research.scraper._visualization_scheme import BaseVisualizer
import requests
import plotly.io as pio
import plotly.express as px
import streamlit as st

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
        data['year'] = data['year'].astype('str')
        data['price_gap'] = data['price_gap'].fillna(0)
        data['price_gap'] = data['price_gap'].map(lambda x: int(x))
        data = data.sort_values(by=['year',  'series'], ascending=True)
        data.loc[:, 'description'] = data.apply(lambda row: 
                    f"{row['description']}<br>release: ${row['price_original']}<br>price: ${row['price']} ({row['price_gap']}↓)"  
                                                if row['price_gap'] != 0 else 
                                                f"{row['description']}<br>price: ${row['price']}" , axis=1)
        years = sorted(data['year'].unique(), reverse=True)
        series = data.series.unique()

        colors = px.colors.qualitative.Plotly  # Plotly 기본 팔레트
        color_map = {i: colors[i % len(colors)] for i in range(len(series))}
                
        markers = ['circle', 'x', 'square', 'star', 'diamond', 'pentagon',  'hexagon', 'cross', 'octagon',  'hexagon2']
        marker_map = {year: markers[i] for i, year in enumerate(sorted(years, reverse=True))}
                
        fig = go.Figure()
        
        for i, s in enumerate(series):
            data_series = data[data['series'] == s]
            year = data_series['year'].drop_duplicates().item()
        
            fig.add_trace(go.Scatter(
                x=data_series['size'],
                y=data_series['price'],
                mode='markers',
                marker=dict(
                    size=12,
                    color=color_map.get(i),  
                    symbol=marker_map.get(year),
                    opacity=0.8,  
                ),
                
                error_y=dict(
                    type='data',
                    symmetric=False,
                    arrayminus=[0]*len(data),
                    array=data_series['price_gap'],
                    color=color_map.get(i),  
                    thickness=1,
                    width=5
                ), 
                
                text=data_series['description'],  
                hoverinfo='text',  
                name=f'{s.upper()} ({year})',
                showlegend=True,
                visible=(year == years[0])
            ))

        ticks_below_3000 = list(range(0, 3001, 500))
        ticks_above_3000 = list(range(4000, max(int(data['price_original'].max()), int(data['price'].max())) + 2000, 1000))
        tickvals = ticks_below_3000 + ticks_above_3000
        
        year_dropdown = dict(
            buttons= [
                dict(
                    label=year,
                    method='update',
                    args=[
                        {'visible': [year in trace.name for trace in fig.data]}
                    ]
                ) for year in years
            ] +
            [
                dict(
                    label='All',  
                    method='update',
                    args=[
                        {'visible': [True] * len(fig.data)}
                    ]
                )
            ] 
        )
    
        fig.update_layout(
            updatemenus=[{
                'buttons': year_dropdown['buttons'],
                'direction': 'down',
                'showactive': True,
                'x': 0.1,  
                'y': 1.0,  
                'yanchor': 'bottom'  
            }]
        )

        # 레이아웃 설정
        fig.update_layout(
            title='Price map',
            xaxis_title='Size (Inch)',
            yaxis_title='Current Price ($)',
            legend_title='Year',
            showlegend=True,
            template='simple_white',
            # ),
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
                # file_path = "https://raw.githubusercontent.com/xikest/research_market_tv/main/json/col_heatmap.json"
                file_path = "col_heatmap.json"
                
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
        
        years = sorted(heatmap_data.columns.get_level_values(0).unique(), reverse=True)        
        year_heatmapdf_dict = {}
        year_mask_dict = {}
        for year in years:
            year_heatmapdf = heatmap_data.xs(year, level=0, axis=1)
            year_maskdf = mask_data.xs(year, level=0, axis=1)
            year_heatmapdf_dict[year] = year_heatmapdf.loc[(year_heatmapdf != 0).any(axis=1)]
            year_mask_dict[year] = year_maskdf.loc[year_heatmapdf_dict[year].index, year_heatmapdf_dict[year].columns]
            
        initial_year = years[0]
        fig = go.Figure(data=go.Heatmap(
            z=year_heatmapdf_dict.get(initial_year).values,  
            x=[f"{str(idx[0]).upper()} ({initial_year})" for idx in year_heatmapdf_dict.get(initial_year).columns],  
            y=year_heatmapdf_dict.get(initial_year).index.str.capitalize(),   
            colorscale=cmap,         
            showscale=False,
            zmax=1,                  
            hoverinfo='text',        
            hovertemplate='<b>%{customdata}</b><extra></extra>',
            customdata=year_mask_dict.get(initial_year).values
            ))

        year_dropdown = {
            'buttons': [
                dict(
                    label=str(year),
                    method='update',
                    args=[{
                        'z': [year_heatmapdf_dict.get(year).values],
                        'x': [[f"{str(idx[0]).upper()} ({year})" for idx in year_heatmapdf_dict.get(year).columns]],
                        'y': [year_heatmapdf_dict.get(year).index.str.capitalize()],
                        'customdata':[year_mask_dict.get(year).values],
                    }]
                ) for year in years
            ] + [
                dict(
                    label='All',
                    method='update',
                    args=[{
                        'z': [heatmap_data.values],
                        'x': [x_labels],
                        'y': [heatmap_data.index.str.capitalize()],
                        'customdata':[mask_data.values],
                    }]
                )
            ]
        }

        fig.update_layout(
            title=f"{self.maker} spec",
            updatemenus=[dict(
                type="dropdown",
                buttons=year_dropdown['buttons'],
                direction="down",
                showactive=True,
                x=0.1,
                y=1.1,
                yanchor='bottom',
            )],
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