import time
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
from market_research.scraper._scraper_scheme import Scraper
from typing import Tuple
from tools.file.github import GitMgt


class Rurlsearcher(Scraper):
    def __init__(self, enable_headless=True, verbose=False):
        super().__init__(enable_headless=enable_headless)
        self.wait_time = 2
        self.verbose=  verbose

        
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
                    "sony_tv": f'{get_recent_data_from_git("s_scrape_model_data")}',
                    "lg_tv": f'{get_recent_data_from_git("l_scrape_model_data")}',
                    "samsung_tv": f'{get_recent_data_from_git("se_scrape_model_data")}',
                    "panasonic_tv": f'{get_recent_data_from_git("p_scrape_model_data")}',
                    "tcl_tv": f'{get_recent_data_from_git("t_scrape_model_data")}',
                    "sony_gaming": f'{get_recent_data_from_git("s_g_scrape_model_data")}',
                    "lg_gaming": f'{get_recent_data_from_git("l_g_scrape_model_data")}',
                    "samsung_gaming": f'{get_recent_data_from_git("se_g_scrape_model_data")}',
                    }
            info_df = pd.DataFrame()
        for maker in path_dict:
            df = pd.read_json(path_dict.get(maker), orient='records', lines=True)
            df = df[[ "year", "series"]]
            df["maker"] = maker
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
                search_query = f"{keywords +' '+ 'review'}"
                search_query = search_query.replace("gaming", "monitor").replace("_"," ")
                url_check = search_query.split()[1] ## "tv", "monitor"
                url = self._search_and_extract_url(search_query=search_query, url_check=url_check)
  
                check_keywords = f"{maker.split('_')[0]} {series}" ## "sony", "xr90"
                if self._check_url_with_keywords(url, check_keywords) is None:
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
            if self.verbose:
                print(f"checking [{keywords}] in title[{title}]")##ss
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
    


    def _search_and_extract_url(self, search_query: str, url_check:str=None, base_url="https://www.rtings.com"):
        driver = self.web_driver.get_chrome()
        if self.verbose:
                print(f"search_query: {search_query}")
                print(f"checking [{url_check}/review] in url") 
        try:
            driver.get(base_url)
            search_input = driver.find_element("class name", "searchbar-input")
            search_input.send_keys(search_query)
            search_input.send_keys(Keys.RETURN)
            time.sleep(self.wait_time)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            search_results = soup.find_all('div', class_='searchbar_results-main')
            extracted_urls = [result.find('a')['href'] for result in search_results][:2]

            # 추출된 URL을 /로 분할하고, 검색 결과와 비교하여 일치하는 경우 반환
            if url_check:
              url_condition= f"{url_check}/reviews"
            else:
              url_condition= f"reviews"

            for url in extracted_urls:
                if url_condition in url:
                    split_url = url.split('/')
                    if len(split_url) == 5:
                        if self.verbose:
                            print(base_url + url)
                        return base_url + url
        except Exception as e:
            print(f"An error occurred: {e}")
            pass

        finally:
            # 브라우저 종료
            driver.quit()
        return None