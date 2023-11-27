import matplotlib.pyplot as plt
import seaborn as sns
from .cleanup_s import DataCleanup_s
from market_research.scraper._visualizer_scheme import Visualizer
class Visualizer_s(Visualizer):

    def __init__(self, df, output_folder_path="results", style="whitegrid", stop_words=None):
        super().__init__(output_folder_path = output_folder_path)
        sns.set_style(style)
        self.dc = DataCleanup_s(df, stop_words=stop_words)

    def group_plot_bar(self, col_group: list = ["display type", "size"], col_plot: str = "price_discount",
                       ylabel_mark: str = "%", figsize=(10, 6), save_plot_name=None):

        df = self.dc.get_price_df()
        col_group_str = '&'.join(col_group)
        grouped_data = df.groupby(col_group)[col_plot].mean().sort_values(ascending=False)

        plt.figure(figsize=figsize)

        grouped_data.plot(kind="bar")
        plt.ylabel(f"{col_plot}({ylabel_mark})")
        sns.despine()

        if save_plot_name is None:
            save_plot_name = f"barplot_{col_plot}_to_{col_group_str}.png"
        plt.savefig(save_plot_name, bbox_inches='tight')  # bbox_inches='tight'를 추가하여 레이블이 잘림 방지
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
            col_selected = [
                            'contrast enhancement', 'peak luminance', 'pixel contrast booster',
                             'color enhancement', 'triluminos', 'smoothing', 'live colour technology',
                             'clarity enhancement', 'dual database processing', 'video processing',
                             'object-based super resolution',
                             'viewing angle (x-wide angle)', 'x-wide angle',
                             'anti reflection (x-anti reflection)', 'x-anti reflection',
                             'picture processor', '4k processor',
                             'color space',
                             'eco friendly',
                             'auto genre picture mode',
                             'features for playstation5 auto genre picture mode',
                             'auto hdr tone mapping',
                             'features for playstation5 auto hdr tone mapping',
                             'multi-view',
                             ]


        data_df = self.dc.get_df_cleaned()
        data_df = data_df[col_selected]
        if display_types is not None:
            condition = data_df.index.get_level_values('display type').str.contains('|'.join(display_types), case=False, na=False)
            data_df = data_df[condition]
        data_df = data_df.replace({"-": 0})
        data_df = data_df.map(lambda x: len(x.split(",")) if isinstance(x, str) else x)
        data_df = data_df.fillna(0)
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

