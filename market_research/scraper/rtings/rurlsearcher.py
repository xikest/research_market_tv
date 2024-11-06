import time
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
from market_research.scraper._scraper_scheme import Scraper
from typing import Tuple
from tools.file.github import GitMgt


class Rurlsearcher(Scraper):
    def __init__(self, enable_headless=True):
        super().__init__(enable_headless=enable_headless)
        self.wait_time = 2
        

        
    def _get_model_info_from_mkrt(self, path_dict:dict=None) ->set:
        def get_recent_data_from_git(file_name):
            file_urls = []
            file_list = GitMgt.get_github_folder_files("xikest", "research_market_tv", "json")
            for file_url in file_list:
                if file_name in file_url:
                    file_urls.append(file_url)  
            file_urls.sort()          
            return file_urls[-1]
                
        if path_dict is None:
            path_dict = {
                    "sony": f'{get_recent_data_from_git("s_scrape_model_data")}',
                    "lg": f'{get_recent_data_from_git("l_scrape_model_data")}',
                    "samsung": f'{get_recent_data_from_git("se_scrape_model_data")}'
                    }
            
            info_df = pd.DataFrame()
        for maker in path_dict:
            df = pd.read_json(path_dict.get(maker), orient='records', lines=True)
            df = df[[ "year", "series"]]
            df.loc[:, 'maker'] = maker
            info_df = pd.concat([info_df, df], axis=0)
        info_df =info_df.drop_duplicates()
        return info_df


    def get_urls_with_model_info(self) -> Tuple[list, pd.DataFrame]:
        info_df = self._get_model_info_from_mkrt()
        info_df = info_df.reset_index(drop=True)
        failed_series = []
        info_dict = {}
        for _, row in tqdm(info_df.iterrows()):
            maker = row['maker']
            series = row['series']
            year = row['year']
            try:
                keywords = f"{maker} {series}"
                url = self._search_and_extract_url(search_query=keywords)
                if self._check_url_with_keywords(url, keywords) is None:
                  raise ValueError
                info_dict[url] = {"maker":maker, 
                                  "series":series, 
                                  "year":year}               
            except:
                failed_series.append(series)
                continue
        if failed_series:
            print(f"failed_series: {failed_series}")
        return info_dict


    def _check_url_with_keywords(self, url: str, keywords: list):
        driver = self.web_driver.get_chrome()
        driver.get(url)
        try:
          page_source = driver.page_source
          soup = BeautifulSoup(page_source, 'html.parser')
          if soup.title and soup.title.string:
            title = soup.title.string.lower().replace("\u200b", "")
            if all(keyword in title for keyword in keywords.split()):
              return url 
            else:
              raise ValueError
        except:
          return None
        finally:
          driver.quit()

    
    def get_urls_from_web(self, keywords: set = None) -> list:
        urls_set = set()
        for keyword in tqdm(keywords):
            url = self._search_and_extract_url(search_query=keyword)
            if url is not None:
                urls_set.add(url)
        urls_list = list(urls_set)        
        return urls_list
    


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