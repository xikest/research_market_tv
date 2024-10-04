import time
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
from market_research.scraper._scraper_scheme import Scraper
import requests

class Rurlsearcher(Scraper):
    def __init__(self, enable_headless=True):
        super().__init__(enable_headless=enable_headless)
        self.wait_time = 2
        

    def _get_search_src(self):
        file_path = "https://raw.githubusercontent.com/xikest/research_market_tv/main/json/rtings_keywords.json"
        response = requests.get(file_path)
        data = response.json()
        return data
        

    def get_keywords_for_search(self, maker: str = None, category: str = None):
        src_dict = self._get_search_src()['keywords']
        keywords_list = []

        for maker_key, category_dict in src_dict.items():
            if maker is None or maker_key == maker:
                for category_key, keyword_list in category_dict.items():
                    if category is None or category_key == category:
                        keywords_list.extend([f"{maker_key} {keyword}" for keyword in keyword_list])
        
        return keywords_list
    
    
    
    def get_urls_for_search(self, maker: str = None, category: str = None):
        src = self._get_search_src()
        src_dict = src['urls']
        urls_list = []
        for maker_key, category_dict in src_dict.items():
            if maker is None or maker_key == maker:
                for category_key, keyword_list in category_dict.items():
                    if category is None or category_key == category:
                        urls_list.extend([f"{maker_key} {keyword}" for keyword in keyword_list])
        
        return urls_list

    def get_urls_from_web(self, keywords: list = None) -> list:
        urls_set = set()
        for keyword in tqdm(keywords):
            url = self._search_and_extract_url(search_query=keyword)
            if url is not None:
                urls_set.add(url)
        return list(urls_set)

    def get_urls_from_inputpath(self, intput_folder_path: str) -> list:
        self.set_data_path(intput_folder_path=intput_folder_path)

        urls = []
        file_list = self.intput_folder.glob('*')
        excel_files = [file for file in file_list if file.suffix in {'.xlsx', '.xls'}]
        for excel_file in excel_files:
            df = pd.read_excel(excel_file)
            urls.extend(df["urls"])
        return urls

    def _search_and_extract_url(self, search_query: str, base_url="https://www.rtings.com"):
        driver = self.web_driver.get_chrome()
        try:
            driver.get(base_url)
            search_input = driver.find_element("class name", "searchbar-input")
            search_input.send_keys(search_query)
            search_input.send_keys(Keys.RETURN)
            time.sleep(self.wait_time)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            search_results = soup.find_all('div', class_='searchbar_results-main')
            extracted_urls = [result.find('a')['href'] for result in search_results]

            # 추출된 URL을 /로 분할하고, 검색 결과와 비교하여 일치하는 경우 반환
            for url in extracted_urls:
                if "tv/reviews" in url:
                    split_url = url.split('/')
                    if len(split_url) == 5:
                        return base_url + url
        finally:
            # 브라우저 종료
            driver.quit()
        return None
