import time
import pandas as pd
from market_research.scraper._scraper_scheme import Scraper
from tools.file.github import GitMgt
from selenium.webdriver.common.by import By

class Erpsearcher(Scraper):
    def __init__(self, enable_headless=True, verbose=False):
        super().__init__(enable_headless=enable_headless)
        self.wait_time = 2
        self.verbose=  verbose

    def fetch_model_data(self):
        model_erp_data = [] 
        info_models = self._get_model_info_from_mkrt()  
        
        for model, maker in info_models.items():
            brand_input = maker.split("_")[0]  
            model_erp_dict = self._search_and_extract_url(model, brand_input)  
            model_erp_dict['model'] = model  
            model_erp_dict['maker'] = maker  
            
            model_erp_data.append(model_erp_dict)  
        
        model_erp_df = pd.DataFrame(model_erp_data)
        model_erp_df = model_erp_df.set_index("model")
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
            df = pd.read_json(path_dict.get(maker), orient='records', lines=True)
            df = df[["model"]]
            df["maker"] = maker
            info_df = pd.concat([info_df, df], axis=0)
        info_df =info_df.drop_duplicates()

        info_models = dict(zip(info_df['model'], info_df['maker']))
        return info_models



    def _search_and_extract_url(self, model_input:str, brand_input:str, base_url="https://eprel.ec.europa.eu/screen/product/electronicdisplays") ->dict:
        
        result = {}
        driver = self.web_driver.get_chrome()
        if self.verbose:
                print(f"search_query: {model_input}, {brand_input}")
        try:
            driver.get(base_url)

            input_model_element = driver.find_element(By.ID, "model-identifier")
            input_model_element.send_keys(model_input)
            
            input_supplier_element = driver.find_element(By.ID, "supplier-name")
            input_supplier_element.send_keys(brand_input)
            
            search_button = driver.find_element(By.ID, "search")
            driver.execute_script("arguments[0].click();", search_button)
            time.sleep(self.wait_time)
            search_result_items = driver.find_elements(By.TAG_NAME, "app-search-result-item")


            for index, item in enumerate(search_result_items):
                try:
                    supplier_name = item.find_element(By.XPATH, ".//span[contains(@class, 'ecl-u-type-2xl') and contains(@class, 'ecl-u-type-bold') and contains(@class, 'ecl-u-type-color-blue') and contains(@class, 'ecl-u-type-family-alt')]")
                    model_name = item.find_element(By.XPATH, ".//span[contains(@class, 'ecl-u-type-l') and contains(@class, 'ecl-u-type-color-black') and contains(@class, 'ecl-u-type-family-alt') and contains(@class, 'ecl-u-mt-xs')]")
                    
                    supplier_name = supplier_name.text.strip()
                    model_name = model_name.text.strip()

                       
                    if model_input.lower() in model_name.lower():
                        print(f"{supplier_name}: {model_name}")
                        details_button = item.find_element(By.CSS_SELECTOR, ".ecl-u-width-100.ecl-button.ecl-button--primary")
                        driver.execute_script("arguments[0].click();", details_button)
                        if self.verbose:
                            driver.save_screenshot(f"click_on_details_of_{model_name}_with_{model_input}.png")
                        
                    break
                except Exception as e:
                    print(e)

            elements = driver.find_elements(By.CLASS_NAME, "ecl-u-align-items-l-end")
            for element in elements:
                try:
                    key = element.find_element(By.CLASS_NAME, "ecl-row").text.strip()  # 첫 번째 텍스트 (키)
                    value = element.find_element(By.CLASS_NAME, "ecl-u-flex-grow-0").text.strip()  # 두 번째 텍스트 (값)
                    value = value.replace("\n", " ").strip()
                    result[key] = value
                    if self.verbose:
                        print(f"{key}: {value}")

                except Exception as e:
                    print(f"에러 발생: {e}")
            
   
        except Exception as e:
            print(f"An error occurred: {e}")
            pass

        finally:
            driver.quit()
        return result