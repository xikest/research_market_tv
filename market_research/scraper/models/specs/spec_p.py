import time
from tqdm import tqdm
import pandas as pd
from selenium.webdriver.common.by import By
import logging
from tools.file import FileManager
from market_research.scraper._scraper_scheme import Scraper, Modeler


class ModelScraper_p(Scraper, Modeler):
    def __init__(self, enable_headless=True,
                 export_prefix="panasonic_model_info_web", intput_folder_path="input", output_folder_path="results",
                 wait_time=1 ,verbose=False):
        Scraper.__init__(self, enable_headless, export_prefix, intput_folder_path, output_folder_path)
        self.wait_time = wait_time
        self.verbose = verbose
        pass
    
    def fetch_model_data(self) -> pd.DataFrame:
        def find_urls() -> dict:
            url_set = set()
            url_series_set = self._get_series_urls()
            for url in url_series_set:
                url_models_set = self._extract_models_from_series(url=url)
                url_set.update(url_models_set)
            url_dict = {idx: url for idx, url in enumerate(url_set)}
            print(f"Total model: {len(url_dict)}")
            logging.info(f"Total model: {len(url_dict)}")
            return url_dict
        
        def extract_specs(url_dict):
            dict_models = {}
            for key, url in tqdm(url_dict.items()):
                try:
                    dict_info = self._extract_model_details(url)
                    dict_models[key] = dict_info
                    dict_spec = self._extract_global_specs(url=url)
                    dict_spec['url'] = url
                    dict_models[key].update(dict_spec)
                except Exception as e:
                    pass
            return dict_models
        
        def transform_format(dict_models, json_file_name: str) -> pd.DataFrame:
            df_models = pd.DataFrame.from_dict(dict_models).T
            df_models = df_models.dropna(subset=['price'])
            df_models.to_json(self.output_folder / json_file_name, orient='records', lines=True)
            return df_models
        
        
        print("start collecting data")
        logging.info("start collecting data")
        url_dict = find_urls()
        dict_models = extract_specs(url_dict)
        df_models = transform_format(dict_models, json_file_name="p_scrape_model_data.json")

        FileManager.df_to_excel(df_models.reset_index(), file_name=self.output_xlsx_name)
        return df_models
    
    @Scraper.try_loop(2)
    def _get_series_urls(self) -> set:
        def find_series_urls(url:str, prefix:str) -> set:
            print(f"Starting to scrape series URLs from: {url}")
            logging.info(f"Starting to scrape series URLs from: {url}")
            url_series = set()
            url = url
            prefix = prefix
            step = 200
            try:
                driver = self.set_driver(url)
                scroll_distance_total = self.web_driver.get_scroll_distance_total()
                scroll_distance = 0

                while scroll_distance < scroll_distance_total:
                    for _ in range(2):
                        elements = driver.find_elements(By.CLASS_NAME, "product-card__figure")
                        for element in elements:
                            try:
                                a_tag = element.find_element(By.TAG_NAME, 'a')  # `a` 태그를 찾음
                                link = a_tag.get_attribute('href')  # href 속성 가져오기
                                if link:  # 유효한 링크인지 확인
                                    url_series.add(link.strip())
                            except Exception as e:
                                print(f"Error extracting href: {e}")
                        driver.execute_script(f"window.scrollBy(0, {step});")
                        time.sleep(self.wait_time)
                        scroll_distance += step
                return url_series
            except Exception as e:
                if self.verbose:
                    print(f"{e}")
                logging.error(f"{e}")
                pass
            finally:
                if driver:  
                    driver.quit()                 
        url_series = find_series_urls(url = "https://shop.panasonic.com/collections/televisions", prefix = "https://shop.panasonic.com/")
        print(f"The website scan has been completed.\ntotal series: {len(url_series)}")
        logging.info(f"The website scan has been completed.\ntotal series: {len(url_series)}")
        for i, url in enumerate(url_series, start=1):
            print(f"Series: [{i}] {url.split('/')[-1]}")
            logging.info(f"Series: [{i}] {url.split('/')[-1]}")
        return url_series
    
    @Scraper.try_loop(2)
    def _extract_models_from_series(self, url: str) -> set:
        url_models_set = set()
        print(f"Trying to extract models from series: {url}")
        logging.info(f"Trying to extract models from series: {url}")
        
        driver = self.set_driver(url)        
        try: 
            elements = driver.find_elements(By.CLASS_NAME, 'block-swatch')
            
            for element in elements:
                element.click()  # 
                time.sleep(2)  #
                current_url = driver.current_url
                if current_url:  
                    url_models_set.add(current_url.strip())
            print("Extracted models from series")
            logging.info(f"Trying to extract models from series: {url}")
        except Exception as e:
            if self.verbose:
                print(f"Error extracting models from series: {e}")
            logging.error(f"Error extracting models from series: {e}")
        finally:
            if driver:  
                driver.quit()  
                
        return url_models_set
        
    
            
    @Scraper.try_loop(2)
    def _extract_model_details(self, url: str) -> dict:
        
        def extract_model(driver):
            model = driver.find_element(By.CSS_SELECTOR, ".product-info__sku.text-16.text-subdued")
            model = model.text.split(":")[-1].strip()
            return {"model": model}
        
        def extract_description(driver)->dict:
            try:
                description= driver.find_element(By.CSS_SELECTOR, "h1.product-info__title").text
            except:
                description = ""
            return {"description": description}
        
        def extract_prices(driver)->dict:
            prices_dict = dict()

            try:
                price_now = driver.find_element(By.CSS_SELECTOR, "price-list .text-lg").text
                price_now = price_now.split("$")[-1]
                price_now = float(price_now.replace('$', '').replace(',', ''))
                prices_dict['price'] = price_now
                prices_dict['price_original'] = price_now
                prices_dict['price_gap'] = 0.0
            except Exception as e:
                print(e)
                prices_dict['price'] = float('nan')
                prices_dict['price_original'] = float('nan')
                prices_dict['price_gap'] = float('nan')
            return prices_dict
        
        def extract_info_from_model(model: str)->dict:
            dict_info = {}
            model = model.lower()
            dict_info["model"] = model
            dict_info["year"] = model.split("-")[-1]
            dict_info["series"] = model.split("-")[1][2:]
            dict_info["size"] = model.split("-")[1][:2]
            dict_info["display type"] = dict_info["series"][:1]
                
            year_mapping = {
                't': "2024",
            }
            display_mapping = {
                'z':'oled',
                'w':'mini-LED'
            }
            dict_info["year"] = year_mapping.get(dict_info.get("year"), "2025")
            dict_info["display type"] = display_mapping.get(dict_info.get("display type"), "")
            return dict_info
        
        dict_info = {}
        if self.verbose:
            print(f"Connecting to {url.split('/')[-1]}: {url}")
        logging.info(f"Connecting to {url.split('/')[-1]}: {url}")
        try:
            driver = self.set_driver(url)
            
            # Extract model
            dict_info.update(extract_model(driver))
            dict_info.update(extract_description(driver))
            dict_info.update(extract_prices(driver))
            dict_info.update(extract_info_from_model(dict_info.get("model")))
            if self.verbose: 
                print(dict_info)
            logging.info(dict_info)
        except Exception as e:
            print(e)
            if self.verbose:
                print(f"error_extract_model_details: {url}")
            logging.error(f"error_extract_model_details: {url}")
            pass
        finally:
            if driver:  
                driver.quit()  
        return dict_info
    
    @Scraper.try_loop(5)
    def _extract_global_specs(self, url: str) -> dict:
        
        
        def find_spec_tab(driver) -> None:
            def act_click_see_more(driver):
                try: 
                    element = driver.find_element(By.CLASS_NAME,'feature-chart__toggle')
                    element_see_more = element.find_element(By.CLASS_NAME, 'text-with-icon.group')
                    # self.web_driver.move_element_to_center(element_see_more)
                    element_see_more.click()
                    logging.debug("Clicked the 'see more' button from the first locator.")
                    driver.save_screenshot("41act_click_see_more.png")                
                except Exception as e:
                    if self.verbose:
                        print(f"Cannot find the 'see more' button from the second locator: {e}")
                        logging.error(f"Cannot find the 'see more' button from the second locator: {e}")
                time.sleep(self.wait_time)
                return None
            
            act_click_see_more(driver)       
            return None
            
        def extract_specs_detail(driver) -> dict:
            dict_spec = {}
            table = driver.find_element(By.CLASS_NAME, 'section-stack.section-stack--horizontal ')
            rows = table.find_elements(By.CLASS_NAME, 'feature-chart__table-row')
            for row in rows:
                text = row.text.split('\n')
                label = text[0]
                value = text[-1] 
                dict_spec[label] = value        
            return dict_spec
        
        dict_specs = {}
            
        try:
            driver = self.set_driver(url)
            find_spec_tab(driver)   
            dict_specs.update(extract_specs_detail(driver))
            if self.verbose:
                print(f"Received information from {url}")
            logging.info(f"Received information from {url}")
        except Exception as e:
            print(f"error extract_specs_detail from {url}")
            print(e)
            pass
        finally:
            if driver:  
                driver.quit()  
        return dict_specs
        
        
    def set_driver(self, url):
        driver = self.web_driver.get_chrome()
        driver.get(url=url)
        time.sleep(self.wait_time)
        return driver
