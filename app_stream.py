import streamlit as st
import pandas as pd
from market_research.scraper import Specscraper_s
from market_research.scraper import Specscraper_l
from market_research.scraper import Specscraper_se
from market_research.scraper import Rvisualizer



st.set_page_config(layout="wide")
maker_class = {
        "sony": Specscraper_s,
        "lg": Specscraper_l,
        "samsung": Specscraper_se,
    }
makers = ["SONY", "LG", "SAMSUNG"]

@st.cache_data
def loading_heatmap(selected_maker):
    selected_class = maker_class.get(selected_maker)
    fig = selected_class(demo_mode=True).heatmap_spec(return_fig=True)   
    return fig

@st.cache_data
def loading_pricemap(selected_maker):
    selected_class = maker_class.get(selected_maker)
    fig = selected_class(demo_mode=True).price_map(return_fig=True)  
    return fig


@st.cache_data
def loading_calendar(indicator_type):
    calendar_url = None
    calendar_dict = {
        "sony": f'https://calendar.google.com/calendar/embed?src=0c227a75e976c06994e8cc15eef5de98e25fe384b65d057b9edbbb37a7ed7efc%40group.calendar.google.com&ctz=Asia%2FSeoul&showTitle=0',
        "lg": None,
        "samsung": None,
    }
    
    calendar_url = calendar_dict.get(indicator_type)
    return calendar_url
    
# @st.cache_data
def loading_rtings(selected_multi_makers, data_src='measurement'):
    if data_src == 'measurement':
        json_path = 'https://raw.githubusercontent.com/xikest/research_market_tv/main/json/rtings_measurement_data.json'
    elif data_src == 'scores':
        json_path = 'https://raw.githubusercontent.com/xikest/research_market_tv/main/json/rtings_scores_data.json'
    data = pd.read_json(json_path, orient='records', lines=True)
    try:
        fig = Rvisualizer(df = data,  maker_filter=selected_multi_makers).radar_scores(return_fig=True)   
    except:
        fig = None
    return fig

def display_indicators():
    st.sidebar.subheader("Like this project? Buy me a coffee!☕️")
    st.sidebar.write("updated: 1st Oct.")
    selected_maker = st.sidebar.selectbox("", makers).lower()
    for _ in range(30):
        st.sidebar.write("")
    # 달력 URL 로드
    calendar_url = loading_calendar(selected_maker)
    if calendar_url is not None:
        st.sidebar.markdown(f'<iframe src="{calendar_url}" width="300" height="300" frameborder="0"></iframe>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown("<h3 style='text-align: center;'>No information</h3>", unsafe_allow_html=True)

        
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown(f"<h2 style='text-align: center;'>{selected_maker.upper()}</h2>", unsafe_allow_html=True)
        fig = loading_heatmap(selected_maker)
        fig.update_layout(width=500, height=500, title='heat map for spec', margin=dict(t=40, l=30, r=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        selected_multi_makers = st.multiselect("", makers, placeholder='Radar Scores', 
                                                key='key_for_scores', label_visibility='hidden')
        if not selected_multi_makers: 
            selected_multi_makers =  selected_maker
        else:
            selected_multi_makers = list(map(str.lower, selected_multi_makers))
            
        tab1, tab2 = st.tabs(["Total", "Detail"])
        with tab1:
            fig = loading_rtings(selected_multi_makers=selected_multi_makers, data_src = 'scores')
            if fig != None:
                fig.update_layout(width=600, height=500, margin=dict(t=0, r=0, b=20))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("No information")
        with tab2:
           
            fig = loading_rtings(selected_multi_makers=selected_multi_makers, data_src = 'measurement')
            if fig != None:
                fig.update_layout(width=600, height=500, margin=dict(t=0, r=0, b=20))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("No information")

            
    with col3:
            st.write("..")
            
            
    with st.container():   
        fig = loading_pricemap(selected_maker)
        fig.update_layout(
            width=500,
            height=380,
            title='price map',
             margin=dict(t=20, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    display_indicators()
