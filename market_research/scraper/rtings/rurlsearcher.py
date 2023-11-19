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
        self.model_dictionary = {"sony":{
                                        "oled": [
                                            'XR-77A95L', 'XR-65A75L', 'XR-65A95K', 'XR-65A90J', 'XR-65A80CL',
                                            'XR-77A80CL', 'XR-77A80K', 'XR-65A80CK', 'XR-42A90K', 'XR-55A80CL',
                                            'XR-83A80CL', 'XR-55A80CK', 'XR-65A80K', 'XR-83A90J', 'XR-48A90K',
                                            'XR-77A80L', 'XR-55A95K', 'XR-77A80CK', 'XR-55A80L', 'XR-55A80K',
                                            'XR-55A95L', 'XR-65A95L', 'XR-55A75L', 'XR-65A80L', 'XR-83A80L',
                                            'XR-55A90J'
                                        ],
                                        "mini_led": [
                                            'XR-65X93CL', 'XR-75X93CL', 'XR-75X93L', 'XR-85X93L', 'XR-85X95L',
                                            'XR-65X93L'
                                        ],
                                        "lcd": [
                                            'XR-85X95K', 'KD-75X77L', 'XR-85X90CL', 'KD-75X80CK', 'XR-55X90CL',
                                            'KD-55X85K', 'KD-55X77CL', 'XR-75Z9K', 'KD-32W830K', 'KD-85X80K',
                                            'KD-75X85K', 'XR-85X90K', 'XR-75X95K', 'XR-55X90CK', 'KD-43X80K',
                                            'XR-65X90CK', 'KD-43X85K', 'XR-55X90L', 'KD-65X77L', 'KD-85X77L',
                                            'XR-65X90L', 'XR-65X90CL', 'KD-55X80CK', 'XR-75X90CK', 'XR-85Z9K',
                                            'KD-43X77L', 'KD-85X77CL', 'KD-85X85K', 'KD-50X77L', 'XR-75X90L',
                                            'XR-85X90CK', 'KD-65X77CL', 'XR-65X95K', 'KD-50X80K', 'KD-50X85K',
                                            'XR-55X90K', 'XR-85X90L', 'XR-75X90K', 'KD-85X80CK', 'KD-55X77L',
                                            'KD-75X77CL', 'KD-55X80K', 'XR-98X90L', 'KD-65X80CK', 'KD-65X80K',
                                            'XR-65X90K', 'KD-75X80K', 'KD-65X85K', 'XR-75X90CL'
                                        ]
                                    }
        }

    def get_model_dictionary(self, maker:str="sony", key_mode=False):
        if key_mode:
            return self.model_dictionary.keys()
        return self.model_dictionary.get(maker.lower())

    def get_urls_web(self, keywords:list[str,] = None)->list:
        urls_set = set()  
        for keyword in tqdm(keywords):
            urls_set.add(self._search_and_extract_url(search_query=keyword))
        return list(urls_set)

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
