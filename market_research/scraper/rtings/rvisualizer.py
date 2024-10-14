import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from market_research.scraper._visualization_scheme import BaseVisualizer
import plotly.graph_objects as go  
import plotly.express as px
import plotly.io as pio
from plotly.subplots import make_subplots
import plotly.colors as colors
import streamlit as st

class Rvisualizer(BaseVisualizer):

    def __init__(self, data:dict=None, maker_filter=None, output_folder_path="results"):
        
        def initialize_data(data:dict, maker_filter=None, measurement_selection:list=None):
            def retrim(ds: pd.Series, mark: str = ","):
                return ds.str.replace(mark, "")
            def label_cleaning(df):
                def brightness_label(df):
                    select_brightness = df['label'].str.contains("Window") & df['label'].str.contains("Peak")
                    df_brightness = df[select_brightness]
                    df_brightness.loc[:, "label"] = df_brightness["label"].map(lambda x: int(x.split("%")[0].split(" ")[-1]))
                    df_brightness = df_brightness.sort_values(["series", "label"], ascending=True)
                    df_brightness["label"] = df_brightness.label.map(lambda x: str(x) + "%")
                    self.brightness_label = df_brightness['label'].unique()
                    df[select_brightness] = df_brightness
                    return df
                
                df = df.rename(columns={"header":"category", "category": "header"})
                valid_measurements = set(df['category']).intersection(measurement_selection)
                df = df[df['category'].isin(valid_measurements)]
                label_dict = {'1,000 cd/m² DCI P3 Coverage ITP': "DCI",
                                        '10,000 cd/m² Rec 2020 Coverage ITP': "BT2020",
                                        'Blue Luminance': "Blue",
                                        'Cyan Luminance': "Cyan",
                                        'Green Luminance': "Green",
                                        'Magenta Luminance': "Magenta",
                                        'Red Luminance': "Red",
                                        'White Luminance': "White",
                                        'Yellow Luminance': "Yellow"}
                
                for target, label in label_dict.items():
                    df.loc[:, "label"] = df.label.map(lambda x: x.replace(target, label))
                df.loc[:, "result_value"] = df.loc[:, "result_value"].map(lambda x:x.lower())    
                value_dict = {"n/a": "0", "inf": "1000000"}
                for target, value in value_dict.items():
                    df.loc[:, "result_value"] = df.result_value.map(lambda x: x.replace(target, value))
                trim_marks = ["cd/m²", ",", "%", "°", "k", "ms", "hz", "db", ": 1", "w"]
                for trim_mark in trim_marks:
                    try:
                        df.loc[:, "result_value"] = retrim(df["result_value"], trim_mark)
                    except Exception as e:
                        print(e)
                        pass
                df = brightness_label(df)
                return df
            def drop_nouse_col(df):
                df.loc[:, 'result_value'] = df['result_value'].astype(float)
                df = df.drop(['size','model', 'product','grade','header'], axis=1).drop_duplicates()
                return df         
                
            data_type = list(data.keys())[0]
            if data_type == 'measurement':
                df = data.get('measurement')
                df = label_cleaning(df)
                df = drop_nouse_col(df)

            elif data_type == 'scores':
                df = data.get('scores')
                df = df.drop(['size','model', 'product','grade'], axis=1).drop_duplicates().replace("", np.nan).dropna()
            else:
                raise ValueError
            
            df['year'] = df['year'].astype(int).astype(str)
            
            if maker_filter:
                if isinstance(maker_filter, str): maker_filter = [maker_filter]
                filtered_mask = df['maker'].isin(maker_filter)
                df = df[filtered_mask]
                
            heatmap_df = df.copy()
            heatmap_df = heatmap_df[~heatmap_df["score"].isin([""])] 
            heatmap_df.loc[:, "score"] = heatmap_df["score"].astype(float)
            heatmap_df = heatmap_df[["maker", "year", "series","category",'score']].drop_duplicates()
            heatmap_df = heatmap_df.pivot(index=["maker","year", "series"], columns=["category"], values='score')
            heatmap_df = heatmap_df.T
            heatmap_df = heatmap_df.sort_index(axis='columns', level=[0, 1, 2], ascending=[True, False, False])       
            dataset = {'normal': df,
                        "heatmap": heatmap_df}           
            return dataset
        
        
        super().__init__(output_folder_path=output_folder_path)
        pio.templates.default='ggplot2'
        self.dataset = initialize_data(data, maker_filter, Rvisualizer.get_measurement_selection())
        self.font='Arial, sans-serif'
        self.fontsize= 10
        self.data_detail_dict: dict = {}

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
            "Viewing Angle": "°",
            "Misc": "W"
        } 
        pass
        
    @staticmethod
    def get_measurement_selection():
        measurement_selection = [ 'HDR Brightness',
                                    'SDR Brightness',
                                    'Contrast',
                                    'Black Uniformity',
                                    'Color Gamut',
                                    'Color Volume',
                                    'Viewing Angle',
                                    'Reflections',
                                    'Gray Uniformity',
                                    'Response Time',
                                    'Variable Refresh Rate',
                                    'Misc']
        return measurement_selection

    def plot_facet_bar(self, select_label, return_fig:bool=False):
        df = self.dataset.get('normal').copy()
        df = df[df['category'].isin([select_label])]
        if 'Brightness' in select_label:
            df = df[df['label'].isin(self.brightness_label)]
        df = df.sort_values(by=['year', 'series'], ascending=[False, False])    
        categories = df['label'].unique()
        div_group = 2
        first_group = categories[:2]
        second_group = categories[2:]
        plot_unit = self.title_units_dict.get(select_label, "")
        colors = px.colors.qualitative.Plotly  # Plotly 기본 팔레트

        # 서브플롯 생성
        if len(categories) <= div_group:
            rows_num = 1
            cols_num = len(categories)
        else:
            rows_num = 2
            cols_num = max(div_group, len(categories) - div_group)

        fig = make_subplots(
            rows=rows_num,
            cols=cols_num,
            subplot_titles=list(first_group) + [''] * (cols_num - len(first_group)) + list(second_group),
            shared_yaxes=True,  # y축 공유 설정
            vertical_spacing=0.4)

        # Bar 차트 추가
        for i, category in enumerate(categories, start=1):
            df_cat = df[df['label'] == category]
            
            row = 1 if i <= div_group else 2
            col = i if i <= div_group else i - div_group
            
            df_cat.loc[:, 'series'] = df_cat['series'].apply(lambda x: x.upper())
            for year in df_cat['year'].unique():
                year_data = df_cat[df_cat['year'] == year]
                fig.add_trace(
                    go.Bar(
                        x=year_data['series'] + ' (' + year_data['year'].astype(str) + ')',
                        y=year_data['result_value'],
                        name=f"{category} ({year})", 
                        marker=dict(color=colors[i % len(colors)]),
                        hovertemplate='%{y}' + plot_unit + '<br>%{x}<extra></extra>'
                    ),
                    row=row, col=col 
                )

        # y축 범위 설정
        if select_label == "Color Volume":
            for col in range(min(3, len(categories))): 
                fig.update_yaxes(range=[0, 100], row=1, col=col)

            for col in range(2, len(categories) + 1): 
                fig.update_yaxes(matches=None, row=1, col=col)

        # 연도 드롭다운 버튼 생성
        years = sorted(df_cat['year'].unique(), reverse=True)
        
        initial_year = years[0]
        
        for trace in fig.data:
            trace.visible = (initial_year in trace.name)

        year_dropdown = {
            'active': 0,  # 첫 번째 연도가 기본으로 선택되도록 0으로 설정
            'buttons': [
                dict(
                    label=str(year),
                    method='update',
                    args=[{
                        'visible': [year in trace.name for trace in fig.data]
                    }]
                ) for year in years
            ] + [
                dict(
                    label='All',  
                    method='update',
                    args=[{
                        'visible': [True] * len(fig.data)
                    }]
                )
            ]
        }

        fig.update_layout(
            updatemenus=[{
                'buttons': year_dropdown['buttons'],
                'direction': 'down',
                'showactive': True,
                'x': 0,  
                'y': 1.1,  
                'yanchor': 'bottom'  
            }],
            height=800,
            width=800,
            showlegend=False,
            margin=dict(b=100)
        )
        
        if return_fig:
            return fig
        else:
            fig.show()  # 그래프 보여주기

    def radar_scores(self, return_fig: bool = False):
        
        def rgba_with_opacity(color, opacity=0.3):
            hex_color = color.lstrip('#')
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            return f'rgba({r}, {g}, {b}, {opacity})'

        data_df = self.dataset.get('heatmap').copy()
        fig = go.Figure()

        years = data_df.columns.get_level_values(1).unique()
        years = sorted(years, reverse=True)
        series_group = data_df.columns.get_level_values(2).unique()
        color_map = px.colors.qualitative.Plotly  # Plotly 색상 맵 사용
        
        for idx, series in enumerate(series_group):
            data_series = data_df.xs((series), level=(2), axis=1)
            year = data_series.columns.get_level_values(1).unique().item()
            
            maker = data_series.columns.get_level_values(0).unique().item()
            

            
            try:
                suffix = f": {data_series.loc['Mixed Usage'].item()}"
            except:
                suffix = ""
                        

            values = data_series.mean(axis=1).values.flatten()
            values = np.concatenate((values, [values[0]]))
            theta = data_df.index.tolist() + [data_df.index[0]]
            
            # 불연속 색상 맵에서 색상 선택
            line_color = color_map[idx % len(color_map)]  # 색상 맵의 색상 순환
            fill_color = rgba_with_opacity(line_color,opacity=0.1)
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=theta,
                fill='toself',
                fillcolor=fill_color,
                name=f"{maker.upper()} {series.upper()}({year}){suffix}",  # Series 이름에 연도 포함
                mode='lines',
                line=dict(color=line_color, width=2), 
                visible=(year == years[0])
            ))


        year_dropdown = dict( 
            buttons=[
                dict(
                    label=year,
                    method='update',
                    args=[
                        {'visible': [year in trace.name for trace in fig.data]}
                    ]
                ) for year in years
            ]
            +
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
                'x': 0,  
                'y': 1.1,  
                'yanchor': 'bottom'  
            }]
        )
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=False,
                    showline=False,
                    range=[0, 10],
                ),
                angularaxis=dict(
                    visible=True,
                    showline=True,
                    linecolor='gray',
                    linewidth=0.5,
                )
            ),
            showlegend=True,
            legend=dict(
                x=1.3,
                y=0.5,
                traceorder='normal',
                font=dict(size=self.fontsize, family=self.font),
            ),
            width=1000,
            height=800,
            font=dict(size=self.fontsize, family=self.font, weight='bold'),
            margin=dict(l=80, r=100, t=10, b=10),
        )

        fig.write_html(self.output_folder / "radar_plot.html")
        if return_fig:
            return fig
        else:
            fig.show()  

    def heatmap_scores(self, colorscale="cividis", return_fig:bool=False):
        data_df = self.dataset.get('heatmap').copy()
        
        # 첫 번째로 보여줄 연도 (여기서는 첫 번째 연도를 보여주도록 설정)
        initial_year = sorted(data_df.columns.get_level_values(1).unique(), reverse=True)[0]
        initial_df = data_df.xs(initial_year, level=1, axis=1)

        # x_labels 설정
        x_labels = [f"{str(idx[0]).upper()}-{str(idx[1]).upper()}" for idx in initial_df.columns]
        
        # Heatmap 생성 (처음에는 initial_year에 해당하는 데이터만 표시)
        fig = go.Figure(go.Heatmap(
            z=initial_df.values,
            x=x_labels,
            y=initial_df.index,
            colorscale=colorscale,
            showscale=False,
            zmin=0,
            zmax=10,
            text=initial_df.values,
            texttemplate="%{text:.1f}",
            hoverinfo='none',
        ))
        
        years = sorted(data_df.columns.get_level_values(1).unique(), reverse=True)
        
        # 연도 선택 드롭다운 생성
        year_dropdown = {
            'active': 1,  # 두 번째 연도를 기본으로 선택
            'buttons': [
                dict(
                    label=str(year),
                    method='update',
                    args=[{
                        'z': [data_df.xs(year, level=1, axis=1).values],
                        'x': [[f"{str(idx[0]).upper()}-{str(idx[1]).upper()}" for idx in data_df.xs(year, level=1, axis=1).columns]],
                        'y': [data_df.index],
                        'text': [data_df.xs(year, level=1, axis=1).values]
                    }]
                ) for year in years
            ] + [
                dict(
                    label='All',
                    method='update',
                    args=[{
                        'z': [data_df.values],
                        'x': [[f"{str(idx[0]).upper()}-{str(idx[2]).upper()} ({str(idx[1]).upper()})" for idx in data_df.columns]],
                        'y': [data_df.index],
                        'text': [data_df.values]
                    }]
                )
            ]
        }

        # 레이아웃 업데이트
        fig.update_layout(
            updatemenus=[dict(
                type="dropdown",
                buttons=year_dropdown['buttons'],
                direction="down",
                showactive=True,
                x=0,
                y=1.02,
                yanchor='bottom',
            )],
            xaxis_showgrid=False,
            xaxis=dict(tickangle=90),
            yaxis=dict(tickangle=0),
            width=1000,
            height=1000,
            font=dict(size=self.fontsize, family=self.font),
            margin=dict(l=100, r=20, t=40, b=100),
        )

        # HTML 파일로 저장
        fig.write_html(self.output_folder/f"heatmap.html")
        
        # 그래프 반환
        if return_fig:
            return fig
        else:
            fig.show()  # 그래프 보여주기

    def plot_pca(self, palette="RdYlBu", return_fig:bool = False):

        df = self.dataset.get('normal').copy()
        df_pivot = df.pivot_table(index=['maker', 'series'], 
                                columns=['category', 'label'],
                                values='result_value',
                                aggfunc='first')

        scaler = StandardScaler()
        X_numeric_scaled = scaler.fit_transform(df_pivot)

        pca = PCA(n_components=2)  # Set explained variance threshold to 0.8
        pca.fit_transform(X_numeric_scaled)

        label_pc = [f"PC{i + 1}: {var*100:.2f}%" for i, var in enumerate(pca.explained_variance_ratio_)]

        pca_result_df = (
            pd.DataFrame(np.round(pca.components_.T * np.sqrt(pca.explained_variance_), 4),
                        columns=label_pc, index=df_pivot.columns)
            .reset_index()
        )

        pca_result_by_header_df = pca_result_df.groupby(["category"])[label_pc].mean().reset_index()
        pca_result_by_header_df = pca_result_by_header_df.sort_values(by=label_pc[0], ascending=False)
        pca_result_long_df = pd.melt(pca_result_by_header_df, id_vars=["category"], var_name="Principal Component",
                                    value_name="loading")

        palette = colors.qualitative.Plotly
        fig = go.Figure()

        # 각 주성분에 대해 바 추가
        for i, principal_component in enumerate(pca_result_long_df['Principal Component'].unique()):
            df_component = pca_result_long_df[pca_result_long_df['Principal Component'] == principal_component]
            fig.add_trace(go.Bar(
                x=df_component['loading'].round(1),
                y=df_component['category'],
                name=principal_component,
                orientation='h',  
                hoverinfo='x',  
                textposition='auto',  
                marker=dict(color=palette[i])  
            ))

        fig.update_xaxes(title='', range=[-1, 1])
        fig.update_yaxes(title='')
        fig.update_layout(
            barmode='group',  
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.0,
                xanchor="center",
                x=0
            ),
            width=800,
            height=500,
            margin=dict(l=20, r=20, t=20, b=50), 
        )
        fig.write_html(self.output_folder/f"plot_pca.html")
                        
        if return_fig:
            return fig
        else:
            fig.show()  # 그래프 보여주기
    