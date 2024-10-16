import time
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
from market_research.scraper._scraper_scheme import Scraper
from typing import Tuple
# import requests



class Rurlsearcher(Scraper):
    def __init__(self, enable_headless=True):
        super().__init__(enable_headless=enable_headless)
        self.wait_time = 2
        
    def _get_model_info_from_mkrt(self, path_dict:dict=None) ->set:
        if path_dict is None:
            path_dict={"sony": "https://raw.githubusercontent.com/xikest/research_market_tv/main/json/s_scrape_model_data.json",
                    "lg": "https://raw.githubusercontent.com/xikest/research_market_tv/main/json/l_scrape_model_data.json",
                    "samsung":"https://raw.githubusercontent.com/xikest/research_market_tv/main/json/se_scrape_model_data.json"
                    }
            info_df = pd.DataFrame()
        for maker in path_dict:
            df = pd.read_json(path_dict.get(maker), orient='records', lines=True)
            df = df[[ "year", "series"]]
            df['maker'] = maker
            info_df = pd.concat([info_df, df], axis=0)
        info_df =info_df.drop_duplicates()
        return info_df


    def get_urls_with_model_info(self) -> Tuple[list, pd.DataFrame]:
        info_df = self._get_model_info_from_mkrt()
        info_df = info_df.reset_index(drop=True)
        failed_series = []
        for idx, row in tqdm(info_df.iterrows()):
            try:
                maker = row['maker']
                series = row['series']
                keyword = f"{maker} {series}"
                url = self._search_and_extract_url(search_query=keyword)
                info_df.at[idx, 'url'] = url
                
            except:
                failed_series.append(series)
                continue
        if failed_series:
            print(f"failed_series: {failed_series}")
        return info_df['url'].to_list(), info_df

    
    def get_urls_from_web(self, keywords: set = None) -> list:
        urls_set = set()
        for keyword in tqdm(keywords):
            url = self._search_and_extract_url(search_query=keyword)
            if url is not None:
                urls_set.add(url)
        urls_list = list(urls_set)        
        return urls_list
    

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
