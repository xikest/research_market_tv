import pandas as pd
from tools.file import FileManager
import plotly.graph_objs as go
from .data_cleaner import DataCleaner
from market_research.scraper._visualization_scheme import BaseVisualizer
import requests
import plotly.io as pio


class DataVisualizer(BaseVisualizer):
    def __init__(self, df:pd.DataFrame=None, output_folder_path="results", maker=""):
        
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
            
        years = data['year'].unique()
        years = sorted(years)
        
        series_idx = data[['series', 'display type', 'year']].drop_duplicates()
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
                    name=f'{series} [{display}]',
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
                tickvals=tickvals,  
                # gridcolor='lightgray',  
                # gridwidth=1  
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
        x_labels = ['-'.join(map(str, idx)) for idx in heatmap_data.columns]
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,  # 데이터
            x=x_labels,  # x축 레이블
            y=heatmap_data.index,    # y축 레이블
            colorscale=cmap,         # 색상 스케일
            showscale=False,
            zmax=1,                  # 최대값 설정
            hoverinfo='text',        # 호버 정보 설정
            hovertemplate='<b>%{customdata}</b><extra></extra>',
            customdata=mask_data.values
            ))

        # 그래프 제목 및 레이아웃 설정
        fig.update_layout(
            title=f"{self.maker} spec",
            xaxis=dict(title='',tickangle=90),
            yaxis=dict(title='',tickangle=0),
            width=800,  # 그래프 너비
            height=800  # 그래프 높이
        )

        fig.write_html(self.output_folder/f"{self.maker}_heatmap.html")

        if return_fig:
            return fig
        else:
            fig.show()  # 그래프 보여주기
           