import streamlit as st
import pandas as pd
import plotly.io as pio
from io import BytesIO
from market_research.scraper import DataVisualizer
from market_research.scraper import Rvisualizer
from market_research.ir import Calendar
from market_research.ir import SONY_IR

st.set_page_config(layout="wide")  
makers = ["SONY", "LG", "SAMSUNG"]
ONLINE = True
pio.templates.default='ggplot2'

@st.cache_data
def loading_webdata(selected_maker:str):
    if ONLINE:
        web_data = {
                "sony": 'https://raw.githubusercontent.com/xikest/research_market_tv/main/json/s_scrape_model_data.json',
                "lg": 'https://raw.githubusercontent.com/xikest/research_market_tv/main/json/l_scrape_model_data.json',
                "samsung": 'https://raw.githubusercontent.com/xikest/research_market_tv/main/json/se_scrape_model_data.json'}
    else:
        web_data = {
                "sony": './json/s_scrape_model_data.json',
                "lg": './json/l_scrape_model_data.json',
                "samsung": './json/se_scrape_model_data.json'}
        

    selected_maker = selected_maker.lower()
    data_all = pd.DataFrame()
    if selected_maker == 'all':
        for selected_maker in web_data.keys():
            try: 
                selected_json = web_data.get(selected_maker)
                selected_data = pd.read_json(selected_json, orient='records', lines=True)
                selected_data.columns = selected_data.columns.str.lower().str.strip()
                selected_data = selected_data.rename(columns={"rated power consumption": "maximum power consumption", "maximum power consumption": "maximum power consumption"})
                selected_data.loc[:, 'series'] = f"[{selected_maker}] " + selected_data['series']
                data_all = pd.concat([data_all, selected_data[["year", "display type", "size", "series", "model", "grade", "price", "price_original", "price_gap", "description", "maximum power consumption"]]], axis=0)
            except:
                continue
            
    else:
        selected_json = web_data.get(selected_maker)
        selected_data = pd.read_json(selected_json, orient='records', lines=True)
        selected_data.columns = selected_data.columns.str.lower().str.strip()
        data_all = selected_data.dropna(subset=['price'])
    return data_all
     
@st.cache_data
def loading_calendar(indicator_type):
    calendar_url = None
    calendar_dict = {
        "sony": f'https://calendar.google.com/calendar/embed?src=0c227a75e976c06994e8cc15eef5de98e25fe384b65d057b9edbbb37a7ed7efc%40group.calendar.google.com&ctz=Asia%2FSeoul&showTitle=0',
        "lg": None,
        "samsung": None}
    calendar_url = calendar_dict.get(indicator_type)
    return calendar_url
      
     
@st.cache_data
def loading_rtings(data_src='measurement'):
    if ONLINE:
        if data_src == 'measurement':
            json_path = 'https://raw.githubusercontent.com/xikest/research_market_tv/main/json/rtings_measurement_data.json'
        elif data_src == 'scores':
            json_path = 'https://raw.githubusercontent.com/xikest/research_market_tv/main/json/rtings_scores_data.json'
    else:
        if data_src == 'measurement':
            json_path = './json/rtings_measurement_data.json'
        elif data_src == 'scores':
            json_path = './json/rtings_scores_data.json'
    data = pd.read_json(json_path, orient='records', lines=True)
    return {data_src: data}

@st.cache_data
def loading_ir_script():
    ir_df = SONY_IR().get_ir_script()
    return ir_df
    
@st.cache_data
def loading_plot_usd_exchange():
    fig = SONY_IR().plot_usd_exchange()
    return fig
    
@st.cache_data
def loading_plot_financials_with_margin():
    fig = SONY_IR().plot_financials_with_margin(ticker='SONY')
    return fig

@st.cache_data
def display_html_table(df: pd.DataFrame, title: str):
    if not df.empty:
        df = df[['quarter', 'url']]
        df['url'] = df['url'].apply(lambda x: f'<a href="{x}" target="_blank">link</a>')  # HTML 링크로 변환
        st.subheader(title)
        st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)  # HTML로 표 표시
    else:
        st.write("No material.")

                       

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
        
    for _ in range(3):
        st.sidebar.write("")
        
    calendar_url = loading_calendar(selected_maker)
    if calendar_url is not None:
        st.sidebar.markdown(f'<iframe src="{calendar_url}" width="300" height="300" frameborder="0"></iframe>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown("<h3 style='text-align: center;'>No information</h3>", unsafe_allow_html=True)
 
    col1, col2 = st.columns([2,3])
    with col1:
        st.markdown(f"<h2 style='text-align: center;'>{selected_maker.upper()}</h2>", unsafe_allow_html=True)
        data = loading_webdata(selected_maker)
        
        if selected_maker == "sony":
            sub_tabs = st.tabs(["Specification","Header", "Calendar", "IR"])
        else:
            sub_tabs = st.tabs(["Specification"])
            
        with sub_tabs[0]:
            with st.container(): 
                fig = DataVisualizer(data, maker=selected_maker).heatmap_spec(return_fig=True)   
                fig.update_layout(width=500, height=400, title='Heat map for Spec', margin=dict(t=40, l=30, r=30, b=10))
                st.plotly_chart(fig, use_container_width=True)            
                
            with st.container(): 
                if selected_maker != "lg":
                    sub_tabs_col0 = st.tabs(["price", "power consumption (Max)"])
                else:
                    sub_tabs_col0 = st.tabs(["price"])
                        
                with sub_tabs_col0[0]:
                    data_price = pd.DataFrame()
                    toggle = st.radio("price", (selected_maker.upper(), "All"), horizontal=True, label_visibility='hidden')
                    if toggle.lower() == selected_maker.lower():
                        data_price = loading_webdata(selected_maker)
                    elif toggle.lower() == "all":
                        data_price = loading_webdata(toggle)
                        
                    data_price = data_price.dropna(subset=['price'])
                    fig = DataVisualizer(data_price, maker=selected_maker).price_map(return_fig=True)  
                    fig.update_layout(
                        width=500,
                        height=300,
                        title='',
                        margin=dict(t=20, b=0))
                    st.plotly_chart(fig, use_container_width=True)
                    
                if selected_maker != "lg":
                    with sub_tabs_col0[1]:
                        data_power = pd.DataFrame()
                        toggle = st.radio("power", (selected_maker.upper(), "All"), horizontal=True, label_visibility='hidden')
                        if toggle.lower() == selected_maker.lower():
                            data_power = loading_webdata(toggle)
                        elif toggle.lower() == "all":
                            data_power = loading_webdata(toggle)

                        # st.dataframe(data_power)       
                        fig = DataVisualizer(data_power, maker=selected_maker).power_consumption(return_fig=True)  
                        fig.update_layout(
                            width=500,
                            height=300,
                            title='',
                            margin=dict(t=20, b=0))
                        st.plotly_chart(fig, use_container_width=True)
                    

        if selected_maker == "sony":
            with sub_tabs[1]:
                with st.container():              
                    fig = DataVisualizer(data, maker=selected_maker).plot_headertxt(data, return_fig=True)  
                    fig.update_layout(
                        width=500,
                        height=800,
                        title='',
                        margin=dict(t=20, b=0))
                    st.plotly_chart(fig, use_container_width=True)
            with sub_tabs[2]:
                    fig = Calendar('AIzaSyD7NPJmSa47mojWeG10llV8odoBsTSHSrA',
                                   '0c227a75e976c06994e8cc15eef5de98e25fe384b65d057b9edbbb37a7ed7efc@group.calendar.google.com').create_events_calendar(return_fig=True)
                    fig.update_layout(
                        width=500,
                        height=800,
                        title='',
                        margin=dict(t=20, b=0))
                    st.plotly_chart(fig, use_container_width=True)
                    
            with sub_tabs[3]:
                with st.container(): 
                    fig = loading_plot_financials_with_margin()
                    fig.update_layout(
                        width=500,
                        height=300,
                        title='',
                        margin=dict(t=20, b=0))
                    st.plotly_chart(fig, use_container_width=True)
                    
                    
                with st.container(): 
                    try:
                        fig = loading_plot_usd_exchange()
                        fig.update_layout(
                            width=500,
                            height=300,
                            title='',
                            margin=dict(t=20, b=0))
                        st.plotly_chart(fig, use_container_width=True)
                    except:
                        st.write("no working")
                        
                with st.container(): 
                    ir_df = loading_ir_script()
                    years = sorted(ir_df.year.unique(), reverse=True)
                    sub_tabs_irs = st.tabs(years)

                    for i, year in enumerate(years):
                        ir_df_year = ir_df[ir_df['year'] == year]  # 연도별 데이터 필터링
                        ir_df_year_earning = ir_df_year[ir_df_year['category'] == "Earning"]
                        ir_df_year_strategy = ir_df_year[ir_df_year['category'] == "Strategy"]
                        
                        with sub_tabs_irs[i]:
                            col1_ir, col2_ir = st.columns(2)
                            with col1_ir:
                                display_html_table(ir_df_year_earning, "Earning")
                                # if not ir_df_year_earning.empty:
                                #     ir_df_year_display = ir_df_year_earning[['quarter', 'url']]
                                #     ir_df_year_display.loc[:,'url'] = ir_df_year_display['url'].apply(lambda x: f'<a href="{x}" target="_blank">link </a>')  # HTML 링크로 변환
                                #     st.markdown(ir_df_year_display.to_html(escape=False, index=False), unsafe_allow_html=True)  # HTML로 표 표시
                                # else:
                                #     st.write("No material.")
                            with col2_ir:
                                display_html_table(ir_df_year_strategy, "Strategy")
                                
                                # if not ir_df_year_strategy.empty:
                                #     ir_df_year_display = ir_df_year_strategy[['quarter', 'url']]
                                #     ir_df_year_display.loc[:,'url'] = ir_df_year_display['url'].apply(lambda x: f'<a href="{x}" target="_blank">link </a>')  # HTML 링크로 변환
                                #     st.markdown(ir_df_year_display.to_html(escape=False, index=False), unsafe_allow_html=True)  # HTML로 표 표시
                                # else:
                                #     st.write("No material.")
                                                                

                    

    with col2:
        col2_plot_height = 800
        selected_multi_makers = st.multiselect(label="rtings_label", options=makers, placeholder='Radar Scores', 
                                                key='key_for_scores', label_visibility='hidden')
        if not selected_multi_makers: 
            selected_multi_makers =  selected_maker
        else:
            selected_multi_makers = list(map(str.lower, selected_multi_makers))
            
        tab_name = [ "Primary ", "Secondary"]
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
                        fig.update_layout(width=600, height=col2_plot_height, 
                                          margin=dict(t=0, r=0, b=20))
                        
                        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    display_indicators()



