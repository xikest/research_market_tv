import streamlit as st
from market_research.scraper import Specscraper_s
from market_research.scraper import Specscraper_l

# 페이지 레이아웃 설정
st.set_page_config(layout="wide")

@st.cache_data
def loading_data(indicator_type):
    indicator_class = {
        "SONY": Specscraper_s,
        "LGE": Specscraper_l,
    }
    data_class = indicator_class.get(indicator_type)(demo_mode=True)
    return data_class

def display_indicators():
    selected_maker = st.sidebar.radio("Maker", ["SONY", "LGE"])
    data_class = loading_data(selected_maker)

    col1, col2 = st.columns(2)

    with col1:
        fig = data_class.heatmap_spec(return_fig=True)   
        fig.set_size_inches(3, 2)   
        fig.axes[0].set_title('')  # 그래프 제목 삭제
        fig.axes[0].set_xlabel('')  # x축 제목 삭제
        fig.axes[0].tick_params(axis='x', labelsize=6)  # x축 폰트 사이즈
        fig.axes[0].tick_params(axis='y', labelsize=5)  # y축 폰트 사이즈
        st.pyplot(fig, use_container_width=False)

    with col2:
        st.write("여기에 추가 정보를 표시할 수 있습니다.")

    # 수평선 추가
    # st.divider()  # 행과 칼럼을 시각적으로 구분하는 수평선 추가

    with st.container(): 
        fig = data_class.price_map(return_fig=True)  # price map 그리기
        fig.update_layout(width=500, height=500, title='')
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    display_indicators()
