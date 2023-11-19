import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt
from typing import Optional, Union


class Rvisualizer:

    def __init__(self, df):
        self.df = df.copy()
        self.data_detail_dict: dict = {}
        self.data_detail_df = None

        self.title_units_dict = {
            "HDR Brightness": "cd/m²",
            "SDR Brightness": "cd/m²",
            "Black Frame Insertion (BFI)": "Hz",
            "Black Uniformity": "%",
            "Color Gamut": "%",
            "Color Volume": "cd/m²",
            "Color Volume(ITP)": "%",
            "Flicker-Free": "Hz",
            "Gray Uniformity": "%",
            "HDR Brightness In Game Mode": "cd/m²",
            "Reflections": "%",
            "Response Time": "ms",
            "Stutter": "ms",
            "Variable Refresh Rate": "Hz",
            "Viewing Angle": "°"
        }

        self._initialize_data()


    def _initialize_data(self):
        self.df.loc[self.df['label'] == '1,000 cd/m² DCI P3 Coverage ITP', 'header'] = 'Color Volume(ITP)'
        self.df.loc[self.df['label'] == '10,000 cd/m² Rec 2020 Coverage ITP', 'header'] = 'Color Volume(ITP)'
        self.df.loc[self.df['label'] == 'Contrast', 'label'] = 'Contrast_'
        label_dict = {'1,000 cd/m² DCI P3 Coverage ITP': "DCI",
                      '10,000 cd/m² Rec 2020 Coverage ITP': "BT2020",
                      'Blue Luminance': "Blue",
                      'Cyan Luminance': "Cyan",
                      'Green Luminance': "Green",
                      'Magenta Luminance': "Magenta",
                      'Red Luminance': "Red",
                      'White Luminance': "White",
                      'Yellow Luminance': "Yellow"}

        value_dict = {"N/A": "0", "Inf ": "1000000"}

        for target, label in label_dict.items():
            self.df.loc[:, "label"] = self.df.label.map(lambda x: x.replace(target, label))
        for target, value in value_dict.items():
            self.df.loc[:, "result_value"] = self.df.result_value.map(lambda x: x.replace(target, value))






        trim_marks = ["cd/m²", ",", "%", "°", "K", "ms", "Hz", "dB", ": 1"]
        for trim_mark in trim_marks:
            try:
                self.df.loc[:, "result_value"] = self._retrim(self.df["result_value"], trim_mark)


            except:
                pass

        self.df = self.df[(self.df['category'] != 'Sound Quality') & (self.df['category'] != 'Smart Features') & (self.df['category'] != 'Inputs')]
        self.df = self.df[~self.df.score.isin([""])]  # score가 있는 데이터만 사용
        self.df['result_value'] = self.df['result_value'].astype(float)
        self.df["score"] = self.df.score.astype(float)


    def _get_data(self, column):
        data_df = self.data_detail_dict.get(column)

        if data_df is None:
            data_df = self._set_data_detail(column)
            self.data_detail_dict.update({column: data_df})
            data_df = self.data_detail_dict.get(column)
        return data_df

    def _set_data_detail(self, column: str = None):
        self._target_column = column
        data_df = self.df[self.df["header"] == column]
        # data_df.loc[:, "result_value"] = data_df["result_value"].str.strip().astype(float)
        data_df = data_df.sort_values(["maker", "product", "label"], ascending=False)
        data_df = data_df.pivot(index=["maker", "product"], columns="label", values='result_value')
        data_df.columns = data_df.columns.map(lambda x: str(x))
        data_df = data_df.reset_index()
        data_df.loc[:, 'model'] = data_df['maker'] + '_' + data_df['product']
        data_df = data_df.drop(["maker", "product"], axis=1)

        data_df = data_df.melt(id_vars=['model'], var_name='label', value_name=column)

        if "brightness" in column.lower():
            data_df = self._brightness_trim(data_df)

        return data_df

    def _retrim(self, ds: pd.Series, mark: str = ","):
        return ds.str.replace(mark, "")

    def _brightness_trim(self, df):
        df_peak = df[df['label'].str.contains("Window") & df['label'].str.contains("Peak")]
        df_peak.loc[:, "label"] = df_peak["label"].map(lambda x: int(x.split("%")[0].split(" ")[-1]))

        df_peak = df_peak.sort_values(["model", "label"], ascending=True)
        df_peak["label"] = df_peak.label.map(lambda x: str(x) + "%")
        df_peak = df_peak.rename(columns={"label": "APL"})
        return df_peak

    def plotsns_facet_bar(self, column: str, col_wrap=4, height=4, facet_yticks: Optional[Union[dict, list]] = None,
                          facet_ylims: Optional[Union[dict, list]] = None, show_annot=True,
                          swap_mode: bool = False):

        df = self._get_data(column)
        mode_dict = self._plot_mode(column, swap_mode)
        col_y = mode_dict.get("col_y")
        col_x = mode_dict.get("col_x")
        col_facet = mode_dict.get("col_facet")

        color_palette = sns.color_palette("Set2", n_colors=len(set(df[col_x])))

        sns.set(style="whitegrid")
        g = sns.FacetGrid(df, col=col_facet, col_wrap=col_wrap, height=height, sharey=False, sharex=False)
        g.map_dataframe(sns.barplot, x=col_x, y=col_y, hue=col_x, palette=color_palette, )
        g.set_axis_labels(col_x, col_y)

        if facet_yticks:
            if isinstance(facet_yticks, dict):
                for idx, ytick in facet_yticks.items():
                    g.axes.flat[int(idx)].yaxis.set_ticks(ytick)
            elif isinstance(facet_yticks, list):
                for ax in g.axes.flat:
                    ax.yaxis.set_ticks(facet_yticks)

        if facet_ylims:
            if isinstance(facet_ylims, dict):
                for idx, ylim in facet_ylims.items():
                    g.axes.flat[idx].set(ylim=ylim)
            elif isinstance(facet_ylims, tuple):
                for ax in g.axes.flat:
                    ax.set(ylim=facet_ylims)

        g.set_xticklabels(rotation=45, horizontalalignment='right')

        suffix = self.title_units_dict.get(col_y)
        if suffix is not None:
            sup_title = f"{col_y} ({suffix})"
        else:
            sup_title = col_y

        g.fig.suptitle(sup_title, y=1.05)
        g.fig.subplots_adjust(top=1)

        if show_annot:
            for ax in g.axes.flat:
                for p in ax.patches:
                    height_val = p.get_height()
                    annot_text = f'{height_val:.0f}' if height_val.is_integer() else f'{height_val:.2f}'
                    if height_val >= 10000:
                        annot_text = f'{height_val / 1000:.1f}K'
                    ax.annotate(annot_text, (p.get_x() + p.get_width() / 2., height_val), ha='center', va='center',
                                xytext=(0, 1), textcoords='offset points')
                ax.yaxis.set_ticks([])

        sns.despine()
        plt.tight_layout()
        plt.show()

    def plot_lines(self, column, swap_mode=True, ylims: list = None,
                   yticks: list = None):

        df = self._get_data(column)
        mode_dict = self._plot_mode(column, swap_mode)
        col_y = mode_dict.get("col_y")
        col_x = mode_dict.get("col_x")
        col_color = mode_dict.get("col_facet")

        suffix = self.title_units_dict.get(col_y)
        if suffix is not None:
            sup_title = f"{col_y} ({suffix})"
        else:
            sup_title = col_y


        if col_color is not None:
            fig = px.line(df, x=col_x, y=col_y, color=col_color, title=sup_title, line_shape='linear',
                          color_discrete_sequence=px.colors.qualitative.Vivid)
        else:
            fig = px.line(df, x=col_x, y=col_y, title=None, line_shape='linear',
                          color_discrete_sequence=px.colors.qualitative.Vivid)

        fig.update_layout(width=1000, height=500, template='plotly_white', margin=dict(l=10, r=10, b=10, t=40))
        if yticks is not None:
            tickvals = [float(y_tick) for y_tick in yticks]
            ticktext = [str(y_tick) for y_tick in yticks]
            fig.update_yaxes(tickvals=tickvals, ticktext=ticktext)
        if ylims is not None:
            fig.update_yaxes(range=ylims)

        fig.show()


    def _plot_mode(self, column, swap_mode):
        col_y = column
        col_x = "model"
        col_facet = "label"

        if "brightness" in col_y.lower():
            col_x = "model"
            col_facet = "APL"

        if swap_mode == True:
            temp = col_x
            col_x = col_facet
            col_facet = temp

        return {"col_y": col_y,
                "col_x": col_x,
                "col_facet": col_facet}



    def heatmap_scores(self, cmap="cividis", cbar=True, annot=True):
        col_socres = ["maker", "product", "category", "header", "score"]
        data_df = self.df[col_socres].drop_duplicates().replace("", np.nan).dropna()
        data_df["score"] = data_df["score"].map(lambda x: float(x))
        data_df["product"] = data_df["product"].map(lambda x: x.replace("-oled", ""))
        data_df = data_df.pivot(index=["maker", "product"], columns=["category", "header"], values='score')
        data_df = data_df.T.reset_index().sort_index(axis=1).drop("category", axis=1).set_index("header")
        data_df = data_df.sort_index(axis=1, level=[0, 1])  # Sort the index levels
        plt.figure(figsize=(8, 10))
        sns.heatmap(data_df, annot=annot, cmap=cmap, cbar=cbar, vmin=0, vmax=10, yticklabels=data_df.index)
        plt.title("Rtings Score heatmap")
        plt.show()

