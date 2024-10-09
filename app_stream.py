import streamlit as st
import pandas as pd
from market_research.scraper import DataVisualizer
from market_research.scraper import Rvisualizer
from io import BytesIO


st.set_page_config(layout="wide")

makers = ["SONY", "LG", "SAMSUNG"]



@st.cache_data
def loading_webdata(selected_maker):
    web_data = {
            "sony": 'https://raw.githubusercontent.com/xikest/research_market_tv/main/json/s_scrape_model_data.json',
            "lg": 'https://raw.githubusercontent.com/xikest/research_market_tv/main/json/l_scrape_model_data.json',
            "samsung": 'https://raw.githubusercontent.com/xikest/research_market_tv/main/json/se_scrape_model_data.json'}

    selected_json = web_data.get(selected_maker)
    selected_data = pd.read_json(selected_json, orient='records', lines=True)
    selected_data = selected_data.dropna(subset=['price']) #
    return selected_data

@st.cache_data
def load_ir_data(selected_maker=None):
    ir_class_dict = {
            "sony": SONY_IR,
            "lg": None,
            "samsung":  None}
    ir_class= ir_class_dict.get(selected_maker)
    
    if ir_class is not None:
        ir_class = ir_class()
        comments_dict, files_path_dict = ir_class.get_ir_script()
        cleaning_words = ir_class.cleaning_words
        return comments_dict, cleaning_words, files_path_dict
    else: 
        return None
    

@st.cache_data
def loading_calendar(indicator_type):
    calendar_url = None
    calendar_dict = {
        "sony": f'https://calendar.google.com/calendar/embed?src=0c227a75e976c06994e8cc15eef5de98e25fe384b65d057b9edbbb37a7ed7efc%40group.calendar.google.com&ctz=Asia%2FSeoul&showTitle=0',
        "lg": None,
        "samsung": None}
    calendar_url = calendar_dict.get(indicator_type)
    return calendar_url
    
# @st.cache_data
def loading_rtings(data_src='measurement'):
    if data_src == 'measurement':
        json_path = 'https://raw.githubusercontent.com/xikest/research_market_tv/main/json/rtings_measurement_data.json'
    elif data_src == 'scores':
        json_path = 'https://raw.githubusercontent.com/xikest/research_market_tv/main/json/rtings_scores_data.json'
    data = pd.read_json(json_path, orient='records', lines=True)
    return {data_src: data}



def download_data():
    def to_excel(df_dict):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl', mode='w') as writer:
            for sheet_name, df in df_dict.items():
                df.to_excel(writer, index=False, sheet_name=sheet_name)  # 시트 이름은 딕셔너리의 키
        processed_data = output.getvalue()
        return processed_data
       
    df_dict = {maker.lower(): loading_webdata(maker.lower()) for maker in makers}    
    df_dict.update({category: loading_rtings(category).get(category) for category in ['measurement', 'scores']})
    excel_data = to_excel(df_dict)
    return excel_data

def display_indicators():
    selected_maker = st.sidebar.selectbox("", makers).lower()
    st.sidebar.download_button(
        label="DOWNLOAD DATA",
        data=download_data(),
        file_name=f'{selected_maker}_web_sepcs_241001.xlsx',
        mime='application/vnd.ms-excel',
        use_container_width=True)
    
    st.sidebar.write("Updated: 1st Oct.")
    with st.sidebar.expander("Hi 😎", expanded=False):
        st.subheader("Like this project? ")
        st.subheader("Buy me a coffee!☕️")
             
    for _ in range(30):
        st.sidebar.write("")
        
    calendar_url = loading_calendar(selected_maker)
    if calendar_url is not None:
        st.sidebar.markdown(f'<iframe src="{calendar_url}" width="300" height="300" frameborder="0"></iframe>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown("<h3 style='text-align: center;'>No information</h3>", unsafe_allow_html=True)
        
    col1, col2 = st.columns([2, 3])
    with col1:
        st.markdown(f"<h2 style='text-align: center;'>{selected_maker.upper()}</h2>", unsafe_allow_html=True)
        data = loading_webdata(selected_maker)
        sub_tabs = st.tabs(["Specification","Header"])
        with sub_tabs[0]:
        
            with st.container(): 
                fig = DataVisualizer(data, maker=selected_maker).heatmap_spec(return_fig=True)   
                fig.update_layout(width=500, height=500, title='heat map for spec', margin=dict(t=40, l=30, r=30, b=10))
                st.plotly_chart(fig, use_container_width=True)            
                
            with st.container(): 
                fig = DataVisualizer(data, maker=selected_maker).price_map(return_fig=True)  
                fig.update_layout(
                    width=500,
                    height=400,
                    title='price map',
                    margin=dict(t=20, b=0))
                st.plotly_chart(fig, use_container_width=True)
        with sub_tabs[1]:
            with st.container():              
                fig = DataVisualizer(data, maker=selected_maker).plot_headertxt(data, return_fig=True)  
                fig.update_layout(
                    width=500,
                    height=800,
                    title='',
                    margin=dict(t=20, b=0))
                st.plotly_chart(fig, use_container_width=True)

    with col2:
        col2_plot_height = 800
        selected_multi_makers = st.multiselect("", makers, placeholder='Radar Scores', 
                                                key='key_for_scores', label_visibility='hidden')
        if not selected_multi_makers: 
            selected_multi_makers =  selected_maker
        else:
            selected_multi_makers = list(map(str.lower, selected_multi_makers))
            
        tab_name = [ "Primary ", 
                    "Secondary"]
        tabs = st.tabs(tab_name)
                
        with tabs[0]:
            sub_tabs = st.tabs(["Total", "Sub", "Heat map","PCA"])
            
            with sub_tabs[0]:
                data = loading_rtings('scores')
                fig = Rvisualizer(data, selected_multi_makers).radar_scores(return_fig=True)   
                if fig != None:
                    fig.update_layout(width=600, height=col2_plot_height, margin=dict(t=0, r=0, b=20))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.write("No information")
                    
            with sub_tabs[1]:
                data = loading_rtings( 'measurement')
                fig = Rvisualizer(data, selected_multi_makers).radar_scores(return_fig=True)   
                if fig != None:
                    fig.update_layout(width=600, height=col2_plot_height, margin=dict(t=0, r=0, b=20))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.write("No information")
                    
            with sub_tabs[2]:
                data = loading_rtings('measurement')
                fig = Rvisualizer(data, selected_multi_makers).heatmap_scores(return_fig=True)   
                if fig != None:
                    fig.update_layout(width=600, height=col2_plot_height, margin=dict(t=0, r=0, b=20))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.write("No information")
                    
            with sub_tabs[3]:
                data = loading_rtings('measurement')
                fig = Rvisualizer(data, selected_multi_makers).plot_pca(return_fig=True)   
                if fig != None:
                    fig.update_layout(width=600, height=col2_plot_height, margin=dict(t=0, r=0, b=20))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.write("No information")            
                
                
        with tabs[1]:
            sub_category = Rvisualizer.get_measurement_selection()
            sub_tabs = st.tabs(sub_category)
            
            for i, category in enumerate(sub_category):
                with sub_tabs[i]:
                    data = loading_rtings('measurement')
                    fig = Rvisualizer(data, selected_multi_makers).plot_facet_bar(category, return_fig=True)   
                    if fig != None:
                        fig.update_layout(width=600, height=col2_plot_height, margin=dict(t=0, r=0, b=20))
                        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    display_indicators()



