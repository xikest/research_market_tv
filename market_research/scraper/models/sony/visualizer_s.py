import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.express as px
import seaborn as sns
from .cleanup_s import DataCleanup_s
from market_research.scraper._visualizer_scheme import Visualizer
class Visualizer_s(Visualizer):

    def __init__(self, df, output_folder_path="results", style="whitegrid"):

        """
        cleaning_mask에 삭제할 column의 키워드를 리스트로 전달하세요.
        기본 값으로는 사전 정의된 값을 사용합니다.
        """
        super().__init__(output_folder_path = output_folder_path)
        sns.set_style(style)
        self.dc = DataCleanup_s(df)



    def price_map(self):

        # 데이터 준비
        data = self.dc.get_price_df().copy()
        data['size_group'] = data['size'].map(lambda x: int((int(x)/10))*10)

        # 연도와 사이즈에 따른 색상 및 마커 모양 설정
        years = data['year'].unique()
        sizes = sorted(data['size_group'].unique()) 
        colors = px.colors.qualitative.Plotly
        color_map = {year: colors[i % len(colors)] for i, year in enumerate(years)}

        markers = ['circle', 'square', 'diamond', 'pentagon', 'star', 'hexagon', 'cross']
        marker_map = {size: markers[i % len(markers)] for i, size in enumerate(sizes)}

        # 그래프 생성
        fig = go.Figure()

        # Reference 라인 추가
        fig.add_trace(go.Scatter(
            x=[0, 10000],
            y=[0, 10000],
            mode='lines',
            line=dict(color='lightgray', width=2, dash='solid'),
            name='Original Reference',
            showlegend=False
        ))

        # 사이즈별 데이터 추가 (초기에는 숨김)
        for size in sizes:
            fig.add_trace(go.Scatter(
                x=data[data['size_group'] == size]['price_original'],
                y=data[data['size_group'] == size]['price'],
                mode='markers',
                marker=dict(
                    size=12,
                    color='rgba(211, 211, 211, 0.6)',  
                    symbol= marker_map[size],
                    opacity=0.8,  
                    line=dict(width=3, color='black')
                ),
                text=data[data['size'] == size]['description'],  
                hoverinfo='text',  
                name=f'Size {size}',
                visible='legendonly'  # 사이즈 마커는 기본적으로 숨김
            ))

        # 연도별 데이터 추가
        for year in years:
            fig.add_trace(go.Scatter(
                x=data[data['year'] == year]['price_original'],
                y=data[data['year'] == year]['price'],
                mode='markers',
                marker=dict(
                    size=12,
                    color=color_map[year],
                    symbol='circle',  
                    opacity=0.8,
                ),
                text=data[data['year'] == year]['description'], 
                hoverinfo='text',  
                name=f'Year {year}'
            ))

        # 레이아웃 설정
        fig.update_layout(
            title='Price map',
            xaxis_title='Original Price($)',
            yaxis_title='Current Price($)',
            legend_title='Filter',
            showlegend=True,
            template='simple_white',
            xaxis=dict(
                range=[0, 10000],
                showgrid=True
            ),
            yaxis=dict(
                range=[0, 10000],
                showgrid=False
            ),
            width=1000,
            height= 1000,
            hovermode='closest',
            legend=dict(
                traceorder='reversed' 
            )
        )
        fig.show()


    def group_price_bar(self, col_group: list = ["display type", "size"], col_plot: str = "price",
                       ylabel_mark: str = "", figsize=(10, 6), save_plot_name=None):
        # Fetch the DataFrame
        df = self.dc.get_price_df().copy()

        # Join the column names for the save plot name
        col_group_str = '&'.join(col_group)

        grouped_stats = df.groupby(col_group)[col_plot].agg(['mean', 'max', 'min']).sort_values(by='mean',
                                                                                                ascending=False)
        plt.figure(figsize=figsize)
        ax = grouped_stats.plot(kind="bar", y=["max", "mean", "min"], figsize=figsize)
        plt.ylabel(f"{col_plot} ({ylabel_mark})")
        plt.title(f"Mean, Max, and Min {col_plot} grouped by {col_group_str}")
        sns.despine()

        if save_plot_name is None:
            save_plot_name = f"barplot_{col_plot}_to_{col_group_str}.png"
        plt.savefig(f"{self.output_folder}/{save_plot_name}", bbox_inches='tight')
        plt.show()


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


        data_df = self.dc.get_df_cleaned()

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