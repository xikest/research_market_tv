import time
import pandas as pd
from market_research.scraper._scraper_scheme import Scraper
from tools.file.github import GitMgt
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

class Erpsearcher(Scraper):
    def __init__(self, enable_headless=True, verbose=False):
        super().__init__(enable_headless=enable_headless)
        self.wait_time = 2
        self.verbose=  verbose

    def fetch_model_data(self):
        model_erp_data = [] 
        # info_models = self._get_model_info_from_mkrt()  
        info_df = self._get_model_info_from_mkrt() 

        info_models = zip(info_df['model'], info_df['maker'], info_df['price'],  info_df['size'], info_df['series'])

        for model, maker, price, size, series in info_models:
            
            brand_input = maker.split("_")[0]  
            model_erp_dict = self._search_data(model, brand_input)
            if model_erp_dict is None:
                continue
            model_erp_dict['maker'] = maker  
            model_erp_dict['query'] = model
            model_erp_dict['series'] = series
            model_erp_dict['size'] = size
            model_erp_dict['price'] = price

            model_erp_data.append(model_erp_dict)  
        
        model_erp_df = pd.DataFrame(model_erp_data)
        model_erp_df = model_erp_df.set_index("query").reset_index()
        model_erp_df.to_excel("model_erp_data.xlsx", index=False)
        model_erp_df.to_json(self.output_folder / "model_erp_data.json", orient='records', lines=True)
        return model_erp_df


        
    def _get_model_info_from_mkrt(self, path_dict:dict=None) ->dict:
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
            df = pd.DataFrame()
            df_model = pd.read_json(path_dict.get(maker), orient='records', lines=True)
            if 'gaming' in maker.lower(): 
                df["model"] = df_model["series"]
            else:
                df["model"] = df_model["size"].astype(str) + df_model["series"].astype(str)

            df["price"] = df_model["price_original"]
            df["size"] = df_model["size"]
            df["series"] = df_model["series"]
            df.loc[:, "maker"] = maker
            info_df = pd.concat([info_df, df], axis=0)
        info_df =info_df.drop_duplicates()

        return info_df



    def _search_data(self, model_input:str, brand_input:str, base_url="https://eprel.ec.europa.eu/screen/product/electronicdisplays") ->dict:
        
        result = {}
        driver = self.web_driver.get_chrome()
        if self.verbose:
            print(f"search_query: {model_input}, {brand_input}")
        try:
            driver.get(base_url)
            for _ in range(5):
                try:
                    input_model_element = driver.find_element(By.ID, "model-identifier")
                    input_model_element.send_keys(model_input)
                    
                    input_supplier_element = driver.find_element(By.ID, "supplier-name")
                    input_supplier_element.send_keys(brand_input)
                    
                    search_button = driver.find_element(By.ID, "search")
                    driver.execute_script("arguments[0].click();", search_button)
                    time.sleep(self.wait_time)
                    search_result_items = driver.find_elements(By.TAG_NAME, "app-search-result-item")
                    break
                except:
                    continue

            for idx, item in enumerate(search_result_items):
                try:
                    supplier_name = item.find_element(By.XPATH, ".//span[contains(@class, 'ecl-u-type-2xl') and contains(@class, 'ecl-u-type-bold') and contains(@class, 'ecl-u-type-color-blue') and contains(@class, 'ecl-u-type-family-alt')]")
                    model_name = item.find_element(By.XPATH, ".//span[contains(@class, 'ecl-u-type-l') and contains(@class, 'ecl-u-type-color-black') and contains(@class, 'ecl-u-type-family-alt') and contains(@class, 'ecl-u-mt-xs')]")
                    
                    supplier_name = supplier_name.text.strip()
                    model_name = model_name.text.strip()

                       
                    if model_input.lower() in model_name.lower():
                        print(f"{supplier_name}: {model_name}")
                        result['brand']=supplier_name
                        result['model']=model_name
                        details_button = item.find_element(By.CSS_SELECTOR, ".ecl-u-width-100.ecl-button.ecl-button--primary")
                        driver.execute_script("arguments[0].click();", details_button)
                        if self.verbose:
                            driver.save_screenshot(f"click_on_details_of_{model_name}_with_{model_input}.png")
                        break
                except Exception as e:
                    print(e)
                   
            if 'brand' not in result or 'model' not in result:
                if self.verbose:
                    print(f"Model '{model_input}' not found in the search results.")
                return None
            
            time.sleep(self.wait_time)

            try:
                
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                title_element = soup.find('div', class_='ecl-u-media-bg-position-center')
                if title_element and title_element.get('title'):
                    title = title_element['title']
                    label = title[:-1]
                    grade = title[-1]
                    result[label] = grade.strip()
                    print(f"{label}: {grade}")
                else:
                    print('Energy class not found.')

                elements = soup.find_all('div', class_='ecl-u-align-items-l-end')
                for element in elements:
                    # 하위 요소 검색
                    key_element = element.find('div', class_='ecl-row')  # 키가 있는 요소
                    value_element = element.find('div', class_='ecl-u-flex-grow-0')  # 값이 있는 요소

                    # 키와 값 추출
                    key = key_element.get_text(strip=True).strip() if key_element else None
                    value = value_element.get_text(strip=True).replace("\n", " ").strip() if value_element else None

                    if key and value:  # 키와 값이 모두 존재하는 경우만 저장
                        result[key] = value
                        if self.verbose:
                            print(f"{key}: {value}")
            except Exception as e:
                print(f"Detail pages: {e}")
   
        except Exception as e:
            print(f"An error occurred: {e}")
            pass

        finally:
            driver.quit()
        return result
