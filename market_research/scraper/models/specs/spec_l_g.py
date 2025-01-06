from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
from tqdm import tqdm
import re
import logging
from selenium.webdriver.common.by import By
from tools.file import FileManager
from market_research.scraper._scraper_scheme import Scraper, Modeler



class ModelScraper_l_g(Scraper, Modeler):
    def __init__(self, enable_headless=True,
                 export_prefix="lge_model_info_web", intput_folder_path="input", output_folder_path="results",
                 wait_time=2, verbose=False):

        Scraper.__init__(self, enable_headless, export_prefix, intput_folder_path, output_folder_path)
        self.wait_time = wait_time
        self.verbose = verbose
        pass

    def fetch_model_data(self) -> pd.DataFrame:
        
        def find_urls() -> dict:
            url_set = set()
            url_series_set = self._get_series_urls()
            for url in tqdm(url_series_set):
                url_models_set = self._extract_models_from_series(url=url)
                url_set.update(url_models_set)
            url_dict = {idx: url for idx, url in enumerate(url_set)}
            print(f"Total model: {len(url_dict)}")
            return url_dict
        
        def extract_sepcs(url_dict):
            dict_models = {}
            for key, url in tqdm(url_dict.items()):
                try:
                    dict_info = self._extract_model_details(url)
                    dict_models[key] = dict_info
                    dict_spec = self._extract_global_specs(url=url)
                    dict_spec['url'] = url
                    dict_models[key].update(dict_spec)
                except Exception as e:
                    if self.verbose:
                        print(f"fail to collect: {url}")
                        print(e)
            return dict_models
        
        def transform_format(dict_models, json_file_name: str) -> pd.DataFrame:
            df_models = pd.DataFrame.from_dict(dict_models).T
            df_models = df_models.drop(['Series', 'Size'], axis=1)
            df_models = df_models.dropna(subset=['price'])
            df_models.to_json(self.output_folder / json_file_name, orient='records', lines=True)
            return df_models
            
        print("start collecting data")
        url_dict = find_urls()
        dict_models = extract_sepcs(url_dict)
        df_models = transform_format(dict_models, json_file_name="l_g_scrape_model_data.json")
            
        FileManager.df_to_excel(df_models.reset_index(), file_name=self.output_xlsx_name)
        return df_models
    
    @Scraper.try_loop(2)
    def _get_series_urls(self) -> set:
        
        def click_view_all(driver):
            clickalble = True
            while clickalble:
                try:
                    switch_element = driver.find_element(By.XPATH, '//*[@id="GlobalLayoutContainer"]/div[5]/div/div/div[2]/div/div/div[2]/div/div[1]/div/div[1]/div/div/span/span[1]/input')
                    driver.execute_script("arguments[0].click();", switch_element)
                    # self.web_driver.click_action(switch_element)
                    time.sleep(1)
                    # self.web_driver.move_element_to_center(switch_element)
                except Exception as e:
                    clickalble = False
                
        def find_series_urls(url, prefix) -> set:
            print(f"Starting to scrape series URLs from: {url}")
            url_series = set()
            url = url
            prefix = prefix
            step = 200
            
            try:
                driver = self.set_driver(url)
                click_view_all(driver)
                
                scroll_distance_total = self.web_driver.get_scroll_distance_total()
                scroll_distance = 0

                while scroll_distance < scroll_distance_total:
                    for _ in range(2):
                        html = driver.page_source
                        soup = BeautifulSoup(html, 'html.parser')
                        elements = soup.find_all('a', class_="css-11xg6yi")
                        
                        for element in elements:
                            url_series.add(prefix + element['href'].strip())
                        driver.execute_script(f"window.scrollBy(0, {step});")
                        time.sleep(self.wait_time)
                        scroll_distance += step
                return url_series
            except Exception as e:
                pass
            finally:
                driver.quit()
        
        url_series = find_series_urls( url = "https://www.lg.com/us/monitors", prefix = "https://www.lg.com")
        print(f"The website scan has been completed.\ntotal series: {len(url_series)}")
        for i, url in enumerate(url_series, start=1):
            print(f"Series: [{i}] {url.split('/')[-1]}")
        return url_series

    @Scraper.try_loop(try_total=5)
    def _extract_models_from_series(self, url: str, prefix="https://www.lg.com/") -> set:
      
        def extract_model_url(elements)->set:
            url_models_set= set()
            for element in elements:
                try:
                    url = prefix + element['href']
                    url_models_set.add(url.strip())
                except Exception as e:
                    if self.verbose == True:
                        print(f"Getting series error ({e})")
                    pass
            return url_models_set
            
        url_models_set = set()
        try:
            soup = BeautifulSoup(requests.get(url).text, 'html.parser')
            elements = soup.find_all('a', class_='css-1a0ki8h')
            url_models_set = extract_model_url(elements)
        except Exception as e:
            pass
        finally:
            pass
        return url_models_set
    
    @Scraper.try_loop(2)
    def _extract_model_details(self, url: str) -> dict:
        
        def extract_model(soup)->dict:
            
            label = soup.find('span', class_="MuiTypography-root MuiTypography-overline css-rrulv7").text.strip()
            model = label.split()[-1]
            return {"model": model}
        
        def extract_prices(soup)->dict:
            prices_dict = dict()
            try:
                price = soup.find('div', class_='MuiGrid-root MuiGrid-item css-8wacqv').text.strip()
                split_price = price.split('$')
                pattern = r'\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
                prices = [re.search(pattern, part).group() for part in split_price if re.search(pattern, part)]
                if len(prices) == 3:
                    price_now = float(prices[0].replace(',', ''))
                    price_gap = round(float(prices[1].replace(',', '')), 1)
                    price_original = float(prices[2].replace(',', ''))
                    
                    prices_dict["price"] = price_now
                    prices_dict["price_gap"] = price_gap
                    prices_dict["price_original"] = price_original
                else:
                    price_now = float(split_price[-1].replace(',', '')) 
                    prices_dict["price"] = price_now
                    prices_dict["price_original"] = price_now
                    prices_dict["price_gap"] = 0.0
            except:
                prices_dict["price"] = float('nan')
                prices_dict["price_original"] = float('nan')
                prices_dict["price_gap"] = float('nan')
                
            return prices_dict
       
        def extract_description(soup)->dict:
            descriptions = [
                ('h2', 'MuiTypography-root MuiTypography-subtitle2 css-8oa1vg'),
                ('h1', 'MuiTypography-root MuiTypography-subtitle2 css-8oa1vg'),
                ('h1', 'MuiTypography-root MuiTypography-h5 css-vnteo9')
            ]
            for tag, class_name in descriptions:
                try:
                    description = soup.find(tag, class_=class_name).text.strip()
                    if description: break  
                except AttributeError:     
                    description =""
                
            return {"description": description}
        
        def extract_info_from_model(model: str)->dict:
            model = model.lower()  # 대소문자 구분 제거
            dict_info = {}

            # 연도 매핑
            year_mapping =  {'k': "2018",
                            'l': "2019",
                            'n': "2022",
                            'p': "2021",
                            'q': "2022",
                            'r': "2023",
                            's': "2024"}
                        
            dict_info["size"] = model[:2]
            dict_info["grade"] = model[2]
            dict_info["series"] = model.split("-")[0]
            dict_info["year"] = model[3]
            dict_info["year"] = year_mapping.get(dict_info.get("year"), None)
            return dict_info

        
        dict_info = {}
        if self.verbose:
            print(f"Connecting to {url.split('/')[-1]}: {url}")
        logging.info(f"Connecting to {url.split('/')[-1]}: {url}")
        try:
            response = requests.get(url)
            page_content = response.text
            soup = BeautifulSoup(page_content, 'html.parser')
            
            dict_info.update(extract_model(soup))
            dict_info.update(extract_prices(soup))
            dict_info.update(extract_description(soup))
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
            return dict_info
    
    
    

    @Scraper.try_loop(try_total=10)
    def _extract_global_specs(self, url: str) -> dict:
      
        def find_spec_tab(driver):
            try: 
                for id in range(5):
                    element_all_specs = driver.find_element(By.ID, f"simple-tab-{id}")
                    if element_all_specs.text.lower() == "all specs":
                        break
                self.web_driver.move_element_to_center(element_all_specs)
                time.sleep(self.wait_time)
                element_all_specs.click()
                time.sleep(self.wait_time)
            except:
                try: 
                    element_all_specs = driver.find_element(By.CLASS_NAME, "MuiTypography-root.MuiTypography-h6.MuiTypography-alignLeft.MuiLink-root.MuiLink-underlineAlways.css-kgbp8r")
                    self.web_driver.move_element_to_center(element_all_specs)
                    time.sleep(self.wait_time)
                except:
                    element_all_specs = driver.find_element(By.CLASS_NAME, 'MuiTypography-root.MuiTypography-h5.css-14uiqdv')
                    self.web_driver.move_element_to_center(element_all_specs)
                    time.sleep(self.wait_time)
                
                
            return None 
        

        def extract_spec_detail(driver) -> dict:
            dict_spec = {}
            spec_elements = driver.find_elements(By.CSS_SELECTOR, '.MuiBox-root.css-1nnt9ji')
            for spec_element in spec_elements:
                try: 
                    label = spec_element.find_element(By.CLASS_NAME,
                                                        'MuiTypography-root.MuiTypography-body3.css-11mszpq').text.strip()
                    content = spec_element.find_element(By.CLASS_NAME,
                                                        'MuiTypography-root.MuiTypography-body2.css-1yx8hz4').text.strip()
                except:
 
                    label = spec_element.find_element(By.CLASS_NAME,
                                                    'MuiTypography-root.MuiTypography-body3.css-byc8c0').text.strip()
                    content = spec_element.find_element(By.CLASS_NAME,
                                                    'MuiTypography-root.MuiTypography-body2.css-1yx8hz4').text.strip()
                if label != '':
                    
                    original_label = label
                    while label in dict_spec and dict_spec.get(label)!=content:
                        asterisk_count = label.count('*')
                        label = f"{original_label}{'*' * (asterisk_count + 1)}"
                    dict_spec[label] = content
                    if self.verbose: 
                        if label == "" and content == "":
                            print(f"[{label}] {content}")

            dict_spec.pop("*", None)            
            return dict_spec
       
        dict_spec = dict()
        try:
            driver = self.set_driver(url)           
            find_spec_tab(driver)   
            dict_spec = extract_spec_detail(driver)
            if self.verbose:
                print(f"Received information from {url}")
            logging.info(f"Received information from {url}")
        except Exception as e:
            print(f"error extract_specs_detail from {url}")
            pass
        finally:
            if driver:  
                driver.quit()    
        return dict_spec
            

            
            
    def set_driver(self, url):
        driver = self.web_driver.get_chrome()
        driver.get(url=url)
        time.sleep(self.wait_time)
        return driver