import streamlit as st
import pandas as pd
import plotly.io as pio
from io import BytesIO
import requests
from market_research.scraper import DataVisualizer
from market_research.scraper import Rvisualizer
from market_research.ir import Calendar
from market_research.ir import SONY_IR
from market_research.ir import MACRO
from datetime import datetime



st.set_page_config(layout="wide")  

ONLINE = True
pio.templates.default='ggplot2'
st.session_state["category"] = None



def modify_maker(func):
    def wrapper(*args, **kwargs):
        # args에 값이 있을 때
        if args:
            # st.write(args)  
            selected_maker = args[0]  

            if isinstance(selected_maker, str):
                if selected_maker:
                    args = (f"{selected_maker}_{st.session_state.get('category', 'default')}",) + args[1:]
            
            elif isinstance(selected_maker, list):
                new_makers = [f"{maker}_{st.session_state.get('category', 'default')}" for maker in selected_maker]
                args = (new_makers,) + args[1:]
        # st.write("deco")          
        # st.write(args)  
        return func(*args, **kwargs)  
    return wrapper

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
    return file_urls[-1]


@modify_maker
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

@modify_maker
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
def loading_calendar(indicator_type):
    calendar_url = None
    calendar_dict = {
        "sony": f'"https://calendar.google.com/calendar/embed?height=600&wkst=1&ctz=Asia%2FSeoul&showPrint=0&showTabs=0&showCalendars=0&showTz=0&showTitle=0&src=MGMyMjdhNzVlOTc2YzA2OTk0ZThjYzE1ZWVmNWRlOThlMjVmZTM4NGI2NWQwNTdiOWVkYmJiMzdhN2VkN2VmY0Bncm91cC5jYWxlbmRhci5nb29nbGUuY29t&src=a28uamFwYW5lc2Uub2ZmaWNpYWwjaG9saWRheUBncm91cC52LmNhbGVuZGFyLmdvb2dsZS5jb20&color=%23D50000&color=%234285F4" style="border-width:0" width="800" height="600" frameborder="0" scrolling="no"',
        "lg": None,
        "samsung": None,
        "panasonic": None}
    calendar_url = calendar_dict.get(indicator_type)
    return calendar_url
      
     
@st.cache_data
def loading_rtings(data_src='measurement'):
    if ONLINE:
        if data_src == 'measurement':
            json_path = get_recent_data_from_git("rtings_measurement_data")
        elif data_src == 'scores':
            json_path = get_recent_data_from_git("rtings_scores_data")
    else:
        if data_src == 'measurement':
            json_path = './json/rtings_measurement_data_250109.json'
        elif data_src == 'scores':
            json_path = './json/rtings_scores_data_250109.json'
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
    
    df_dict = {maker.lower(): loading_webdata(maker.lower()) for maker in makers}  
    df_dict.update({category: loading_rtings(category).get(category) for category in ['measurement', 'scores']})
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
    version = loading_webdata_version(selected_maker)
    st.sidebar.write(f'Updated: {version}')
    
    st.sidebar.write("")   
    options = ["Web", "Multi", "Data"]
    selected_value = st.sidebar.select_slider(
        "Select your Focus:",
        options=options,
        value="Multi" )
    
    st.sidebar.write("")   
    today_date = datetime.now().strftime("%d_%m_%Y")
    st.sidebar.download_button(
        label="DOWNLOAD DATA",
        data=download_data(makers),
        file_name = f'{selected_maker}_web_sepcs_{today_date}.xlsx',
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
            data = loading_webdata(selected_maker)
            
            if selected_maker == "sony":
                sub_tabs = st.tabs(["Specification","Header", "News", "IR", "Macro"])
            else:
                sub_tabs = st.tabs(["Specification"])
                
            with sub_tabs[0]:
                with st.container(): 
                    fig = DataVisualizer(data, maker=selected_maker_for_viz).heatmap_spec(return_fig=True)   
                    fig.update_layout(width=500, height=col1_plot_height, title='Heat map for Spec', margin=dict(t=40, l=30, r=30, b=10))
                    st.plotly_chart(fig, use_container_width=True)            
                    
                        
            if selected_maker == "sony":
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
                    calendar_url = loading_calendar(selected_maker)
                    if calendar_url is not None:
                        st.markdown(f'<iframe src="{calendar_url}" width="100%" height="{col1_plot_height}" frameborder="0"></iframe>', unsafe_allow_html=True)

                    else:
                        st.markdown("<h3 style='text-align: center;'>No information</h3>", unsafe_allow_html=True)
                        
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
                            ir_df_year_bs = ir_df_year[ir_df_year['category'] == "Segment"]
                            with sub_tabs_irs[i]:
                                col1_ir, col2_ir, col3_ir = st.columns(3)
                                with col1_ir:
                                    display_html_table(ir_df_year_earning, "Earning")

                                with col2_ir:
                                    display_html_table(ir_df_year_strategy, "Strategy")
                                with col3_ir:
                                    display_html_table(ir_df_year_bs, "Segment")
                                    
                with sub_tabs[4]:

                        sub_tabs_height = 150
                        st.write("fixing")
                        # fig = MACRO.plot_economic_indicator('RSEAS')
                        # fig.update_layout(
                        #     width=500,
                        #     height=sub_tabs_height,
                        #     title='Advance Retail Sales: Electronics and Appliance Stores')

                        # st.plotly_chart(fig, use_container_width=True)
                        # fig = MACRO.plot_economic_indicator('MRTSIR4423XUSS')
                        # fig.update_layout(
                        #     width=500,
                        #     height=sub_tabs_height,
                        #     title='Retail Inventories/Sales Ratio: Electronics, Appliance Stores and etc')
                        # st.plotly_chart(fig, use_container_width=True)
                
                        
                        # fig = MACRO.plot_economic_indicator('CPIAUCSL')
                        # fig.update_layout(
                        #     width=500,
                        #     height=sub_tabs_height,
                        #     title='CPI: for All Urban Consumers')
                        # st.plotly_chart(fig, use_container_width=True)
                        
                        # fig = MACRO.plot_economic_indicator('A35SNO')
                        # fig.update_layout(
                        #     width=500,
                        #     height=sub_tabs_height,
                        #     title='New Orders: Electrical Equipment, Appliances and Components')
                        # st.plotly_chart(fig, use_container_width=True)
                        
                        # fig = MACRO.plot_economic_indicator('POILBREUSDM')
                        # fig.update_layout(
                        #     width=500,
                        #     height=sub_tabs_height,
                        #     title='Global price of Brent Crude')
                        # st.plotly_chart(fig, use_container_width=True)
                        
    if selected_value == options[1] or selected_value == options[2] :
                               
        with col2:
            col2_plot_height = 800
            selected_multi_makers = st.multiselect(label="maker_label", options=makers, placeholder='Select Makers', 
                                                    key='key_for_scores', label_visibility='hidden')
            if not selected_multi_makers: 
                selected_multi_makers =  selected_maker
            else:
                selected_multi_makers = list(map(str.lower, selected_multi_makers))
                
            tab_name = [ "Price", "Scores", "Data"]
            tabs = st.tabs(tab_name)

            with tabs[0]:  
                with st.container(): 
                    data_price = loading_webdata(selected_multi_makers)
                    fig = DataVisualizer(data_price, maker=selected_maker_for_viz).price_map(return_fig=True)  
                    fig.update_layout(
                        width=500,
                        height=col2_plot_height,
                        title='',
                        margin=dict(t=20, b=0))
                    st.plotly_chart(fig, use_container_width=True)
                             
            if selected_maker in ['sony_gaming', 'lg_gaming', 'samsung_gaming']: ## temp    
                with tabs[1]:
                    st.write("now preparing")
                with tabs[2]:
                    st.write("now preparing")
                    
            else:    
                with tabs[1]:

                    sub_tabs = st.tabs(["Total", "Sub", "Heat map", "PCA"])
                    
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
                        
                        try:
                            fig = Rvisualizer(data, selected_multi_makers).plot_pca(return_fig=True)   
                            fig.update_layout(width=600, height=col2_plot_height, margin=dict(t=0, r=0, b=20))
                            st.plotly_chart(fig, use_container_width=True)
                        except:
                            st.write("No information")            
                        
                        
                with tabs[2]:
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
