import time
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
from market_research.scraper._scaper_scheme import SCAPER




class Rurlsearcher(SCAPER):
    def __init__(self, enable_headless=True):
        super().__init__(enable_headless=enable_headless)
        self.wait_time=2

    def get_urls_web(self, keywords:list[str,] = None)->list:
        return [self._search_and_extract_url(search_query=keyword) for keyword in tqdm(keywords)]

    def get_urls_inputpath(self, intput_folder_path:str)->list:
        self.set_data_path(intput_folder_path=intput_folder_path)

        urls = []
        file_list = self.intput_folder.glob('*')
        excel_files = [file for file in file_list if file.suffix in {'.xlsx', '.xls'}]
        for excel_file in excel_files:
            df = pd.read_excel(excel_file)
            urls.extend(df["urls"])
        return urls


    def _search_and_extract_url(self, search_query:str, base_url = "https://www.rtings.com"):
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
                        return base_url+url  # 첫번째 결과만 반환 됨
        finally:
            # 브라우저 종료
            driver.quit()
        return None