from bs4 import BeautifulSoup
import time
from tqdm import tqdm
import pandas as pd
import re 
from selenium.webdriver.common.by import By
from tools.file import FileManager
from market_research.scraper._scraper_scheme import Scraper, Modeler
import logging

class ModelScraper_t(Scraper, Modeler):
    def __init__(self, enable_headless=True,
                 export_prefix="tcl_model_info_web", intput_folder_path="input", output_folder_path="results",
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
        df_models = transform_format(dict_models, json_file_name="t_scrape_model_data.json")
            
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
                        html = driver.page_source
                        soup = BeautifulSoup(html, 'html.parser')
                        elements = soup.find_all('a', class_="button primary")
                        for element in elements:
                            if element.text.lower() == 'learn more':
                                url_series.add(prefix + element['href'].strip())
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
        url_series = find_series_urls(url = "https://www.tcl.com/us/en/products/home-theater", prefix = "")
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
            element = driver.find_element(By.CLASS_NAME, 'product-variants')
            url_elements = element.find_elements(By.TAG_NAME, 'a')
            for url_element in url_elements:
                model_url = url_element.get_attribute('href')
                if model_url:  
                    url_models_set.add(model_url.strip())
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
            model = driver.find_element(By.XPATH,
                                        '//*[@id="product-details"]/header/div/div[1]/p').text
            
            model = model.lower().replace("model","").strip()
            return {"model": model}
        
        def extract_description(driver)->dict:
            try:
                description = driver.find_element(By.XPATH, '//*[@id="product-details"]/header/div/div[1]/h1').text
            except:
                description = ""
            description = description.replace('"',"")
            return {"description": description}
        
        def extract_prices(driver)->dict:
            prices_dict = dict()
            try:
                price_now = driver.find_element(By.XPATH,
                                                '//*[@id="product-details"]/header/div/div[2]/h4/span').text
                price_now = float(price_now.replace('$', '').replace(',', ''))
                prices_dict['price'] = price_now
                prices_dict['price_original'] = price_now
                prices_dict['price_gap'] = 0.0
            except:
                prices_dict['price'] = float('nan')
                prices_dict['price_original'] = float('nan')
                prices_dict['price_gap'] = float('nan')
            return prices_dict
        


        def extract_info_from_model(model: str)->dict:
            model = model.lower()  # 대소문자 구분 제거
            dict_info = {}

            # 연도 매핑
            year_mapping =  {'0': "2023",
                            '1': "2024",
                            '2': "2025",
                            }

            match = re.match(r"^(\d+)([A-Za-z].*)$", model)      
            dict_info["size"] = match.group(1)
            dict_info["series"] = match.group(2)
            dict_info["year"] = match.group(2)[-2]
            dict_info["year"] = year_mapping.get(dict_info.get("year"), None)
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
            try: 
                time.sleep(self.wait_time)
                driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, '//*[@id="cmp-tabs"]/div[1]/div/ol/li[2]'))
                time.sleep(self.wait_time)
            except Exception as e :
                if self.verbose:
                    print(f"error find_spec_tab {e}")
                pass
                time.sleep(self.wait_time)
                
            return None 
            
        def extract_specs_detail(driver) -> dict:         
            dict_spec = {}
            try:
                elements = driver.find_elements(By.CLASS_NAME,"table.aem-GridColumn.aem-GridColumn--default--12")
                for element in elements:
                  
                    soup = BeautifulSoup(element.get_attribute("innerHTML"), 'html.parser')
                    table = soup.find('table')
                    rows = table.find_all('tr')
                    
                    for row in rows:
                        columns = row.find_all('td')
                        if len(columns) == 2:
                            label = columns[0].find('p').get_text(strip=True)
                            value = columns[1].get_text(strip=True)
                            if label.lower() in ['model', 'description']:
                                continue
                            dict_spec[label] = value
                return dict_spec
            except Exception as e:
                print(e)
                
        dict_specs = {}
        try:
            driver = self.set_driver(url)
            find_spec_tab(driver)   
            driver.save_screenshot(f'{url}.png')
            dict_specs.update(extract_specs_detail(driver))
            if self.verbose:
                print(f"Received information from {url}")
            logging.info(f"Received information from {url}")
        except Exception as e:
            print(f"error extract_specs_detail from {url}")
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