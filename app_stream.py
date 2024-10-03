import streamlit as st

from market_research.scraper import Specscraper_s
from market_research.scraper import Specscraper_l
from market_research.scraper import Specscraper_se
from market_research.scraper import Rvisualizer
import pandas as pd
# 페이지 레이아웃 설정
st.set_page_config(layout="wide")

@st.cache_data
def loading_data(indicator_type):
    indicator_class = {
        "SONY": Specscraper_s,
        "LGE": Specscraper_l,
        "SSE": Specscraper_se,
    }

    data_class = indicator_class.get(indicator_type)(demo_mode=True)
    return data_class

@st.cache_data
def loading_calendar(indicator_type):
    calendar_url = None
    calendar_dict = {
        "SONY": f'https://calendar.google.com/calendar/embed?src=0c227a75e976c06994e8cc15eef5de98e25fe384b65d057b9edbbb37a7ed7efc%40group.calendar.google.com&ctz=Asia%2FSeoul&showTitle=0',
        "LGE": None,
        "SSE": None,
    }
    
    calendar_url = calendar_dict.get(indicator_type)
    return calendar_url
    
@st.cache_data
def loading_rtings(indicator_type):
    measurement_data = None
    data_dict = {
        "SONY": 'sony_measurement_data.json',
        "LGE": 'lge_measurement_data.json',
        "SSE": None,
    }
    # indicator_type에 따라 URL 반환

    json_path = data_dict.get(indicator_type, None)
    if json_path is not None:
        measurement_data = pd.read_json(json_path, orient='records', lines=True)
    
    return measurement_data

def display_indicators():
    st.sidebar.subheader("Dash Board")
       
    selected_maker = st.sidebar.radio("Select Maker", ["SONY", "LGE", "SSE"])
    data_class = loading_data(selected_maker)
    calendar_url = loading_calendar(selected_maker)
    measurement_data = loading_rtings(selected_maker)
    
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        fig = data_class.heatmap_spec(return_fig=True)   
        fig.update_layout(width=700, height=700, title='heat map for spec')  
        st.plotly_chart(fig, use_container_width=False)
        
    with col2:
        if measurement_data is not None:
            fig = Rvisualizer(measurement_data).radar_scores(return_fig=True)   
            fig.update_layout(width=700, height=700, title='radar plot for score')  
            st.plotly_chart(fig, use_container_width=False)
    with col3:

        st.components.v1.iframe(calendar_url, width=400, height=400)
        

    st.divider()  # 행과 칼럼을 시각적으로 구분하는 수평선 추가

    with st.container(): 
        fig = data_class.price_map(return_fig=True)  
        fig.update_layout(width=500, height=500, title='price map')
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    display_indicators()
