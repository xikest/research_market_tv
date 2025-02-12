import streamlit as st
import pandas as pd
import plotly.io as pio
from io import BytesIO
import requests
from market_research.scraper import DataVisualizer
from market_research.scraper import Rvisualizer
from market_research.scraper import ERPvisualizer
from market_research.ir import Calendar
from market_research.ir import SONY_IR
from market_research.ir import MACRO
from datetime import datetime



st.set_page_config(layout="wide")  

ONLINE = True
pio.templates.default='ggplot2'
st.session_state["category"] = None





def get_recent_data_from_git(file_name):
    file_urls = []
    url  = "https://raw.githubusercontent.com/xikest/research_market_tv/main/json/stream_data_list.json"
    response = requests.get(url)
    data = response.json()
    file_list = list(data.values())
    for file_url in file_list:
        if file_name in file_url:
            file_urls.append(file_url)  
    file_urls.sort()  
    # st.write(file_urls) 
    return file_urls[-1]



@st.cache_data
def loading_webdata_version(selected_maker:str):
    if ONLINE:
        web_data = {
                "sony_tv": f'{get_recent_data_from_git("s_scrape_model_data")}',
                "lg_tv": f'{get_recent_data_from_git("l_scrape_model_data")}',
                "samsung_tv": f'{get_recent_data_from_git("se_scrape_model_data")}',
                "panasonic_tv": f'{get_recent_data_from_git("p_scrape_model_data")}',
                "tcl_tv": f'{get_recent_data_from_git("t_scrape_model_data")}',
                "sony_gaming": f'{get_recent_data_from_git("s_g_scrape_model_data")}',
                "lg_gaming": f'{get_recent_data_from_git("l_g_scrape_model_data")}',
                "samsung_gaming": f'{get_recent_data_from_git("se_g_scrape_model_data")}'
                }
    
    else:
        web_data = {
                "sony_tv": './json/s_scrape_model_data_250106.json',
                "lg_tv": './json/l_scrape_model_data_250111.json',
                "samsung_tv": './json/se_scrape_model_data_241116.json',
                "panasonic_tv": './json/p_scrape_model_data_250109.json',
                "tcl_tv": './json/t_scrape_model_data_250111.json',
                "sony_gaming": './json/s_g_scrape_model_data_250110.json',
                "lg_gaming": './json/l_g_scrape_model_data_250111.json',
                "samsung_gaming": './json/se_g_scrape_model_data_250112.json'
                }
    version_info = web_data.get(selected_maker.lower()).split('_')[-1].replace('.json','')  
    version_info = datetime.strptime(version_info, "%y%m%d").strftime("%y-%m-%d")
    return version_info


@st.cache_data
def loading_webdata(selected_maker:str):
    # st.write("loading_webdata")
    # st.write(selected_maker)
    if ONLINE:
        web_data = {
                "sony_tv": f'{get_recent_data_from_git("s_scrape_model_data")}',
                "lg_tv": f'{get_recent_data_from_git("l_scrape_model_data")}',
                "samsung_tv": f'{get_recent_data_from_git("se_scrape_model_data")}',
                "panasonic_tv": f'{get_recent_data_from_git("p_scrape_model_data")}',
                "tcl_tv": f'{get_recent_data_from_git("t_scrape_model_data")}',
                "sony_gaming": f'{get_recent_data_from_git("s_g_scrape_model_data")}',
                "lg_gaming": f'{get_recent_data_from_git("l_g_scrape_model_data")}',
                "samsung_gaming": f'{get_recent_data_from_git("se_g_scrape_model_data")}'
                }

    else:
        web_data = {
                "sony_tv": './json/s_scrape_model_data_241001.json',
                "lg_tv": './json/l_scrape_model_data_250111.json',
                "samsung_tv": './json/se_scrape_model_data_241001.json',
                "panasonic_tv": './json/p_scrape_model_data_250109.json',
                "tcl_tv": './json/t_scrape_model_data_250111.json',
                "sony_gaming": './json/s_g_scrape_model_data_250110.json',
                "lg_gaming": './json/l_g_scrape_model_data_250111.json',
                "samsung_gaming": './json/se_g_scrape_model_data_250112.json'
                }
        
    data_all = pd.DataFrame()
    if isinstance(selected_maker, list):
        
        if len(selected_maker) == 1:
            selected_maker = selected_maker[0] 
        else:   
            for maker in selected_maker:
                try: 
                    selected_json = web_data.get(maker.lower())
                    selected_data = pd.read_json(selected_json, orient='records', lines=True)
                    selected_data.columns = selected_data.columns.str.lower().str.strip()
                    selected_data.loc[:, 'series'] = f"[{maker}] " + selected_data['series']
                    selected_data = selected_data.dropna(subset=['price'])
                    data_all = pd.concat([data_all, selected_data[["year", "size", "series", "price", "price_original", "price_gap", "description"]]], axis=0)
                except:
                    continue
            
    if isinstance(selected_maker, str):
        selected_json = web_data.get(selected_maker.lower())
        selected_data = pd.read_json(selected_json, orient='records', lines=True)
        selected_data.columns = selected_data.columns.str.lower().str.strip()
        selected_data = selected_data.dropna(subset=['price'])
        data_all = selected_data
    return data_all
     
     
      
     
@st.cache_data
def loading_rtings(data_src='measurement', maker:str=None):
    if ONLINE:
        if data_src == 'measurement':
            json_path = get_recent_data_from_git("rtings_measurement_data")
        elif data_src == 'scores':
            json_path = get_recent_data_from_git("rtings_scores_data")
    else:
        if data_src == 'measurement':
            json_path = './json/rtings_measurement_data_250112.json'
        elif data_src == 'scores':
            json_path = './json/rtings_scores_data_250112.json'
    data = pd.read_json(json_path, orient='records', lines=True)
    if maker:
        data = data[data['maker'] == maker]
    return {data_src: data}

@st.cache_data
def loading_erp_class(maker:str=None):
    if ONLINE:
        json_path = get_recent_data_from_git("erp_data")

    else:
        json_path = './json/erp_data_250117.json'

    data = pd.read_json(json_path, orient='records', lines=True)
    if maker:
        data = data[data['maker'] == maker]
    return data


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
        df = df[['Description', 'URL']]
        df.loc[:,'URL'] = df.loc[:,'URL'].apply(lambda x: f'<a href="{x}" target="_blank">link</a>')  # HTML 링크로 변환
        st.subheader(title)
        st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)  # HTML로 표 표시
    else:
        st.write("No material.")

     
def download_data(makers):
    def to_excel(df_dict):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl', mode='w') as writer:
            for sheet_name, df in df_dict.items():
                df.to_excel(writer, index=False, sheet_name=sheet_name)  # 시트 이름은 딕셔너리의 키
        processed_data = output.getvalue()
        return processed_data
    
    df_dict = {f"web {maker.lower()}": loading_webdata(maker.lower()) for maker in makers}  
    for data_category in ['measurement', 'scores']:
        df_dict.update({f"rtings {data_category}": pd.concat([loading_rtings(data_category, maker.lower()).get(data_category) for maker in makers], axis=0)})
        
    df_dict.update({f"ErP Class": pd.concat([loading_erp_class(maker.lower()) for maker in makers], axis=0)})
    excel_data = to_excel(df_dict)
    return excel_data


def select_caregory_at_side():
    category = {
        "TV": "tv",
        "GAMING": "gaming"
    }

    selected_key = st.sidebar.radio("", list(category.keys()))
    return category.get(selected_key,"tv")



def display_indicators():


    category = select_caregory_at_side()
    if category == 'tv':
        makers = ["SONY", "LG", "SAMSUNG", "PANASONIC", "TCL"]
    if category == 'gaming':
        makers = ["SONY", "LG", "SAMSUNG"]      
    st.session_state["category"] = category
    
    
    selected_maker = st.sidebar.selectbox(" ", makers, label_visibility='hidden').lower()
    selected_maker_for_viz = f"{selected_maker}_{category}"
    
    st.sidebar.write("")    
    version = loading_webdata_version(selected_maker_for_viz)
    st.sidebar.write(f'Updated: {version}')
    
    st.sidebar.write("")   
    options = ["Web", "Multi", "Data"]
    selected_value = st.sidebar.select_slider(
        "Select your Focus:",
        options=options,
        value="Multi" )
    
    st.sidebar.write("")   
    today_date = datetime.now().strftime("%y%m%d")
   
    
    st.sidebar.download_button(
        label="DOWNLOAD DATA",
        data=download_data([f"{maker}_{category}" for maker in makers]),
        file_name = f'web_{category}_data_{today_date}.xlsx',
        mime='application/vnd.ms-excel',
        use_container_width=True)
    
    st.sidebar.write("")    
    with st.sidebar.expander("Hi 😎", expanded=False):
        st.subheader("Like this project? ")
        st.subheader("Buy me a coffee!☕️") 
        
    if selected_value == options[0]:
        col1 = st.columns(1)[0]
    elif selected_value == options[2]:
        col2 = st.columns(1)[0]
    else:
        col1, _, col2 = st.columns([3,0.2,6.8])
        
    if selected_value == options[1] or selected_value == options[0] :
        with col1:
            col1_plot_height = 800
            st.markdown(f"<h2 style='text-align: center;'>{selected_maker.upper()}</h2>", unsafe_allow_html=True)
            data = loading_webdata(selected_maker_for_viz)
            
            if selected_maker == 'sony':
                sub_tabs = st.tabs(["Specification","Header", "IR", "Macro"])
            else:
            
                sub_tabs = st.tabs(["Specification"])
                with sub_tabs[0]:
                    with st.container(): 
                        fig = DataVisualizer(data, maker=selected_maker_for_viz).heatmap_spec(return_fig=True)   
                        fig.update_layout(width=500, height=col1_plot_height, title='Heat map for Spec', margin=dict(t=40, l=30, r=30, b=10))
                        st.plotly_chart(fig, use_container_width=True)            
                        
                            
            if selected_maker == "sony" :
                with sub_tabs[1]:
                    with st.container():              
                        fig = DataVisualizer(data, maker=selected_maker_for_viz).plot_headertxt(return_fig=True)  
                        fig.update_layout(
                            width=500,
                            height=col1_plot_height,
                            title='',
                            margin=dict(t=20, b=0))
                        st.plotly_chart(fig, use_container_width=True)

                with sub_tabs[2]:
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
                            ir_df_year_bs = ir_df_year[ir_df_year['category'] == "Segment"]
                            with sub_tabs_irs[i]:
                                col1_ir, col2_ir, col3_ir = st.columns(3)
                                with col1_ir:
                                    display_html_table(ir_df_year_earning, "Earning")

                                with col2_ir:
                                    display_html_table(ir_df_year_strategy, "Strategy")
                                with col3_ir:
                                    display_html_table(ir_df_year_bs, "Segment")
                                    
                with sub_tabs[3]:

                        sub_tabs_height = 150
                        # st.write("fixing")
                        fig = MACRO.plot_economic_indicator('RSEAS')
                        fig.update_layout(
                            width=500,
                            height=sub_tabs_height,
                            title='Advance Retail Sales: Electronics and Appliance Stores')

                        st.plotly_chart(fig, use_container_width=True)
                        fig = MACRO.plot_economic_indicator('MRTSIR4423XUSS')
                        fig.update_layout(
                            width=500,
                            height=sub_tabs_height,
                            title='Retail Inventories/Sales Ratio: Electronics, Appliance Stores and etc')
                        st.plotly_chart(fig, use_container_width=True)
                
                        
                        fig = MACRO.plot_economic_indicator('CPIAUCSL')
                        fig.update_layout(
                            width=500,
                            height=sub_tabs_height,
                            title='CPI: for All Urban Consumers')
                        st.plotly_chart(fig, use_container_width=True)
                        
                        fig = MACRO.plot_economic_indicator('A35SNO')
                        fig.update_layout(
                            width=500,
                            height=sub_tabs_height,
                            title='New Orders: Electrical Equipment, Appliances and Components')
                        st.plotly_chart(fig, use_container_width=True)
                        
                        fig = MACRO.plot_economic_indicator('POILBREUSDM')
                        fig.update_layout(
                            width=500,
                            height=sub_tabs_height,
                            title='Global price of Brent Crude')
                        st.plotly_chart(fig, use_container_width=True)
                        
    if selected_value == options[1] or selected_value == options[2] :
                               
        with col2:
            col2_plot_height = 800
            selected_multi_makers = st.multiselect(label="maker_label", options=makers, placeholder='Select Makers', 
                                                    key='key_for_scores', label_visibility='hidden')
            if not selected_multi_makers: 
                # selected_multi_makers =  selected_maker
                selected_multi_makers_for_viz = selected_maker_for_viz

            else:
                # selected_multi_makers = list(map(str.lower, selected_multi_makers))
                selected_multi_makers_for_viz = [f"{maker.lower()}_{category.lower()}" for maker in selected_multi_makers]


            tab_name = [ "Price", 'Rtings','ErP']
            tabs = st.tabs(tab_name)

            with tabs[0]:  
                with st.container(): 
                    data_price = loading_webdata(selected_multi_makers_for_viz) 
                    fig = DataVisualizer(data_price, maker=selected_multi_makers_for_viz).price_map(return_fig=True)   
                    fig.update_layout(
                        width=500,
                        height=col2_plot_height,
                        title='',
                        margin=dict(t=20, b=0))
                    st.plotly_chart(fig, use_container_width=True)
                             
            with tabs[1]:
                tab_r_name = [ "Scores", "Data",]
                tabs_r = st.tabs(tab_r_name)
                with tabs_r[0]:

                    sub_tabs = st.tabs(["Total", "Sub", "Heat map", "PCA"])
                    
                    with sub_tabs[0]:
                        data = loading_rtings('scores')
                        fig = Rvisualizer(data, selected_multi_makers_for_viz, st.session_state["category"]).radar_scores(return_fig=True)   
                        if fig != None:
                            fig.update_layout(width=600, height=col2_plot_height, margin=dict(t=0, r=0, b=20))
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.write("No information")
                            
                    with sub_tabs[1]:
                        data = loading_rtings( 'measurement')
                        fig = Rvisualizer(data, selected_multi_makers_for_viz, st.session_state["category"]).radar_scores(return_fig=True)   
                        if fig != None:
                            fig.update_layout(width=600, height=col2_plot_height, margin=dict(t=0, r=0, b=20))
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.write("No information")
                            
                    with sub_tabs[2]:
                        data = loading_rtings('measurement')                        
                        fig = Rvisualizer(data, selected_multi_makers_for_viz, st.session_state["category"]).heatmap_scores(return_fig=True)   
                        if fig != None:
                            fig.update_layout(width=600, height=col2_plot_height, margin=dict(t=0, r=0, b=20))
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.write("No information")
                            
                    with sub_tabs[3]:
                        data = loading_rtings('measurement')
                        
                        try:
                            fig = Rvisualizer(data, selected_multi_makers_for_viz, st.session_state["category"]).plot_pca(return_fig=True)   
                            fig.update_layout(width=600, height=col2_plot_height, margin=dict(t=0, r=0, b=20))
                            st.plotly_chart(fig, use_container_width=True)
                        except:
                            st.write("No information")            
                        
                        
                with tabs_r[1]:
                    sub_category = Rvisualizer.get_measurement_selection(st.session_state["category"])
                    sub_tabs = st.tabs(sub_category)
                    
                    for i, category in enumerate(sub_category):
                        with sub_tabs[i]:
                            data = loading_rtings('measurement')
                            fig = Rvisualizer(data, selected_multi_makers_for_viz, st.session_state["category"]).plot_facet_bar(category, return_fig=True)   
                            if fig != None:
                                fig.update_layout(width=600, height=col2_plot_height, 
                                                margin=dict(t=0, r=0, b=20))
                                
                                st.plotly_chart(fig, use_container_width=True)
            with tabs[2]:
                tab_e_name = ["SDR", "HDR"]
                tabs_e = st.tabs(tab_e_name)
                data_erp = loading_erp_class()

                for tab_name, tab in zip(tab_e_name, tabs_e):
                    with tab:
                        power_type = (tab_name == "SDR")  # SDR일 때만 True
                        try:
                            fig = ERPvisualizer(data_erp, maker_filter=selected_multi_makers_for_viz).erp_map(sdr=power_type, return_fig=True)
                            fig.update_layout(
                                width=500,
                                height=col2_plot_height,
                                title='',
                                margin=dict(t=20, b=0))
                            st.plotly_chart(fig, use_container_width=True)
                        except Exception as e:
                            st.write(e)
                            st.write("no data")
                            

if __name__ == "__main__":
    display_indicators()
