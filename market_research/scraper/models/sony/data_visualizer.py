import matplotlib.pyplot as plt
import plotly.graph_objs as go
import seaborn as sns
from .data_cleaner import DataCleaner
from market_research.scraper._visualization_scheme import BaseVisualizer

class DataVisualizer(BaseVisualizer):

    def __init__(self, df, output_folder_path="results", style="whitegrid"):

        """
        cleaning_mask에 삭제할 column의 키워드를 리스트로 전달하세요.
        기본 값으로는 사전 정의된 값을 사용합니다.
        """
        super().__init__(output_folder_path = output_folder_path)
        sns.set_style(style)
        self.dc = DataCleaner(df)



    def price_map(self):


        # 데이터 준비

        data = self.dc.get_price_df().copy()
        years = data['year'].unique()
        
        series_idx = data[['series', 'display type', 'year']].drop_duplicates()
        series_idx = series_idx.sort_values(by=['year',  'series'])
        all_series_dict = {}
        for year in series_idx.year.unique():
            df_year = series_idx[series_idx['year']==year]
            all_series_dict[year] = {key: value for key, value in zip(df_year['series'], df_year['display type'])}

        colors = ['#636EFA','#00CC96','#EF553B']
        color_map = {year: colors[i] for i, year in enumerate(years)}

        markers = ['circle', 'square', 'diamond', 'pentagon', 'star', 'hexagon', 'cross']
        marker_map = {i: markers[i % len(markers)] for i in range(len(series_idx))}

        data.loc[:, 'description'] = data.apply(lambda row: 
                    f"{row['description']}<br>release: {row['price_original']}<br>price: {row['price']} ({row['price_gap']}↓)", axis=1)

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
                showgrid=True
            ),
            width=1000,
            height= 800,
            hovermode='closest',
            legend=dict(
                traceorder='reversed' 
            )
        )
        fig.write_html(self.output_folder/"sony_price_map.html")
        fig.show()



    def heatmap_spec(self, display_types:str=None, save_plot_name=None, title="SONY Spec", cmap="Blues", figsize=(8, 8),
                     cbar=False,
                     col_selected: list = None
                     ):
        """
        # YlGnBu
        # GnBu
        # Oranges
        # viridis
        # plasma
        # cividis
        # inferno
        # magma
        # coolwarm
        # Blues
        """
        if col_selected is None:
            col_selected = ['high peak luminance','peak luminance',
                            'contrast enhancement', 'pixel contrast booster', 'dynamic contrast enhancer','xr backlight master drive',
                            'color enhancement', 'triluminos',
                            # 'live colour technology',
                             # 'clarity enhancement', 'dual database processing', 'video processing',
                             # 'object-based super resolution',
                             'viewing angle (x-wide angle)', 'x-wide angle',
                             'anti reflection (x-anti reflection)', 'x-anti reflection',
                             'picture processor', '4k processor',
                             # 'color space',
                             # 'eco friendly',
                             'bravia core calibrated mode','sony pictures core calibrated mode', 'netflix calibrated mode', 'prime video calibrated mode',
                             'auto genre picture mode',
                             'features for playstation5 auto genre picture mode',
                             'auto hdr tone mapping',
                             'features for playstation5 auto hdr tone mapping',
                             'multi-view',
                             ]


        data_df = self.dc.get_df_cleaned().copy()

        available_columns = [col for col in col_selected if col in data_df.columns]
        missing_columns = [col for col in col_selected if col not in data_df.columns]
        # Print missing columns
        if missing_columns:
            print("The following columns are missing from the DataFrame:")
            for col in missing_columns:
                print(col)

        data_df = data_df[available_columns]
        if display_types is not None:
            condition = data_df.index.get_level_values('display type').str.contains('|'.join(display_types), case=False, na=False)
            data_df = data_df[condition]
        data_df = data_df.mask(data_df == '-', 0)
        data_df = data_df.map(lambda x: len(x.split(",")) if isinstance(x, str) else x)
        data_df = data_df.fillna(0)
        idx_names = data_df.index.names
        data_df = data_df.reset_index().drop_duplicates()
        data_df = data_df.set_index(idx_names)
        data_df = data_df.sort_index(ascending=True)
        # Use plt.subplots to get the axis for colorbar
        self.data_df = data_df

        # Use plt.subplots to get the axis for colorbar
        fig, ax = plt.subplots(figsize=figsize)
        sns.heatmap(data_df.T, cmap=cmap, cbar=cbar, ax=ax, vmax=1)
        plt.xticks(rotation=90)
        plt.title(title)
        if save_plot_name is None:
            save_plot_name = f"heatmap_for_{title}.png"
        plt.savefig(self.output_folder/save_plot_name, bbox_inches='tight')
        plt.show()