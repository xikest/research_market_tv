import pandas as pd
from tools.file import FileManager
import plotly.graph_objs as go
from market_research.scraper._visualization_scheme import BaseVisualizer
import numpy as np
import plotly.io as pio
import plotly.express as px

class ERPvisualizer(BaseVisualizer):
    def __init__(self, df:pd.DataFrame, maker_filter:str,  output_folder_path="results"):
        
        pio.templates.default='ggplot2'
        self.colors = px.colors.qualitative.Plotly 
        self.markers = ['circle', 'x', 'square', 'star', 'diamond', 'pentagon', 'hexagon', 'cross', 'octagon', 'hexagon2']
        self.sdr = 'sdr_power'
        self.hdr = 'hdr_power'
        self.maker = maker_filter
        super().__init__(output_folder_path = output_folder_path)
        FileManager.make_dir(output_folder_path)
        
        if maker_filter:
            if isinstance(maker_filter, str): maker_filter = [maker_filter]
            filtered_mask = df['maker'].isin(maker_filter)
            df = df[filtered_mask]
        
        
        self.data= self.data_cleaning(df)
        
        
        
    def data_cleaning(self, df):
        data = df.loc[:,['Energy class', 
                         'On mode power demand in Standard Dynamic Range (SDR)', 
                         'On mode power demand in High Dynamic Range (HDR) mode',
                         'year', 'series', 'price', 'size', 'description']]
        
        data.rename(columns={'On mode power demand in Standard Dynamic Range (SDR)': self.sdr}, inplace=True)
        data.rename(columns={'On mode power demand in High Dynamic Range (HDR) mode': self.hdr}, inplace=True)
        for power_type in [self.sdr, self.hdr]:
            data[power_type] = (
                data[power_type]
                .str.replace("W", "")  
                .str.replace(",", ".")  
                .apply(lambda x: np.nan if '-' in str(x) else x)
                .astype(float)  
            )
        data['year'] = data['year'].astype(str)

        return data


    def erp_map(self, sdr:bool=True, return_data=False, return_fig=False):

        if sdr:
            power_type= self.sdr
        else:
            power_type= self.hdr
            

        data = self.data.copy()
        years = sorted(data['year'].unique(), reverse=True)
        series = data['series'].unique()
        
        color_map = {i: self.colors[i % len(self.colors)] for i in range(len(series))}
        marker_map = {year: self.markers[i] for i, year in enumerate(years)}
                 
        
        fig = go.Figure()
        for i, s in enumerate(series):
            data_series = data[data['series'] == s]
            year = data_series['year'].drop_duplicates().item()
        
            fig.add_trace(go.Scatter(
                x=data_series['size'],
                y=data_series[power_type],
                mode='markers',
                marker=dict(
                    size=12,
                    color=color_map.get(i),  
                    symbol=marker_map.get(year),
                    opacity=0.8,  
                ),
                
                text=data_series['description'],  
                hoverinfo='text',  
                name=f'{s.upper()} ({year})',
                showlegend=True,
                visible=(year == years[0])
            ))
            
        
        year_dropdown = dict(
            buttons=[
                dict(
                    label=year,
                    method='update',
                    args=[
                        {
                            'visible': [year in trace.name for trace in fig.data]
                        }
                    ]
                ) for year in years
            ] +
            [
                dict(
                    label='All',
                    method='update',
                    args=[
                        {
                            'visible': [True] * len(fig.data)
                        }
                    ]
                )
            ]
        )

        x_range_min = data['size'].min()//10*10
        # x_range_min = int(x_range_min)
        x_range_max = data['size'].max()//10*10+11
        # x_range_max = int(x_range_max)


        fig.update_layout(
            updatemenus=[{
                'buttons': year_dropdown['buttons'],
                'direction': 'down',
                'showactive': True,
                'x': 0.1,  
                'y': 1.0,  
                'yanchor': 'bottom'  
            }],
            
            title='ErP Class',
            xaxis_title='Size (Inch)',
            yaxis_title=f'On mode power demand in Standard Dynamic Range ({power_type.split("_")[0].upper()})[W]',
            legend_title='Model',
            showlegend=True,
            template='simple_white',
            # ),
            yaxis=dict(
                showgrid=True,
                tickmode='array',  
            ),
            xaxis=dict(
                range=[x_range_min, x_range_max],
                showgrid=True,
                tickmode='array',  
                tickvals=list(range(x_range_min, x_range_max, 10))
            ),
            
            width=1000,
            height= 800,
            hovermode='closest',
            legend=dict(
                traceorder='reversed' 
            )
        )
        fig.write_html(self.output_folder/f"{self.maker}_erp_class.html")
        
        if return_fig:
            return fig
        else:
            fig.show()
        if return_data:
            data['series'] = data['series'].map(lambda x: f'{self.maker}_{x}')
            return data
        
        
