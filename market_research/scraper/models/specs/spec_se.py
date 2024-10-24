from bs4 import BeautifulSoup
import time
import pandas as pd
from tqdm import tqdm
import re
from selenium.webdriver.common.by import By
from tools.file import FileManager
from market_research.scraper._scraper_scheme import Scraper, Modeler, CustomException
from market_research.scraper.models.visualizer.data_visualizer import DataVisualizer

class ModelScraper_se(Scraper, Modeler, DataVisualizer):
    def __init__(self, enable_headless=True,
                 export_prefix="sse_model_info_web", intput_folder_path="input", output_folder_path="results",
                 verbose: bool = False, wait_time=2, demo_mode:bool=False):
        
        Scraper.__init__(self, enable_headless, export_prefix, intput_folder_path, output_folder_path)
    
        self.tracking_log = verbose
        self.wait_time = wait_time
        self.file_manager = FileManager
        self.log_dir = "logs/sse/models"
        if self.tracking_log:
            self.file_manager.delete_dir(self.log_dir)
            self.file_manager.make_dir(self.log_dir)
            
        self._data = self._fetch_model_data(demo_mode=demo_mode)    
        DataVisualizer.__init__(self, df = self._data, maker='sse')
        pass
    
    @property
    def data(self):
        return self._data
    
    def _fetch_model_data(self, demo_mode:bool=False) -> pd.DataFrame:
    
        
        def find_urls() -> dict:
            url_set = set()
            url_series_set = self._get_series_urls()
            for url in tqdm(url_series_set):
                url_models_set = self._extract_models_from_series(url=url)
                url_set.update(url_models_set)
            url_dict = {idx: url for idx, url in enumerate(url_set)}
            print("total model:", len(url_dict))
            return url_dict
        
        def extract_sepcs(url_dict):
            dict_models = {}
            for key, url in tqdm(url_dict.items()):
                try:
                    dict_info = self._extract_model_details(url)
                    dict_models[key] = dict_info
                    dict_spec = self._extract_global_specs(url=url)
                    dict_models[key].update(dict_spec)
                    dict_models['url'] = url
                except Exception as e:
                    if self.tracking_log:
                        print(f"fail to collect: {url}")
                        print(e)
                    pass
            return dict_models
        
        def transform_format(dict_models, json_file_name: str) -> pd.DataFrame:
            df_models = pd.DataFrame.from_dict(dict_models).T
            df_models = df_models.drop(['','Series'], axis=1)
            df_models = df_models.rename(columns={'Type':'display type'})
            df_models = df_models.dropna(subset=['price'])
            valid_indices = df_models['Color*'].dropna().index
            df_models.loc[valid_indices, 'Color'] = df_models.loc[valid_indices, 'Color*']

            
            df_models.to_json(self.output_folder / json_file_name, orient='records', lines=True)
            return df_models
            
        if demo_mode:
            print("operating demo")
            # Load existing JSON data
            df_models = pd.read_json('https://raw.githubusercontent.com/xikest/research_market_tv/main/json/se_scrape_model_data.json', orient='records', lines=True)
            
        else:
            print("collecting models")
            url_dict = find_urls()
            dict_models = extract_sepcs(url_dict)
            df_models = transform_format(dict_models, json_file_name="se_scrape_model_data.json")
            
        self.file_manager.df_to_excel(df_models.reset_index(), file_name=self.output_xlsx_name)
        return df_models
    
    @Scraper.try_loop(2)
    def _get_series_urls(self) -> set:

        def extract_urls_from_segments():
            seg_urls = {
                "neo_qled": "https://www.samsung.com/us/televisions-home-theater/tvs/all-tvs/?technology=Samsung+Neo+QLED+8K,Samsung+Neo+QLED+4K",
                "oled": "https://www.samsung.com/us/televisions-home-theater/tvs/oled-tvs/",
                "lifestyle": "https://www.samsung.com/us/televisions-home-theater/tvs/all-tvs/?technology=The+Frame,The+Sero,Portable+Projector,The+Terrace,The+Serif,4K+Laser+Projectors",
                "qled": "https://www.samsung.com/us/televisions-home-theater/tvs/qled-4k-tvs/"
            }
            url_series = set()
            
            for seg, seg_url in seg_urls.items():
                urls=find_series_urls(seg_url, prefix = "https://www.samsung.com")
                url_series.update(urls)
            return url_series   
        
        def find_series_urls(url:str, prefix:str) -> set:
            prefix = "https://www.samsung.com"
            url_series = set()
            url = url
            prefix = prefix
            step = 200

            try:
                driver = self.web_driver.get_chrome()
                driver.get(url=url)
                time.sleep(self.wait_time)
                scroll_distance_total = self.web_driver.get_scroll_distance_total()
                scroll_distance = 0

                while scroll_distance < scroll_distance_total:
                    for _ in range(2):
                        html = driver.page_source
                        soup = BeautifulSoup(html, 'html.parser')
                        elements = soup.find_all('a', class_="ProductCard-learnMore-1030346118 isTvPf")
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
               
        url_series = extract_urls_from_segments()
        
        print("The website scan has been completed.")
        print(f"total series: {len(url_series)}")
        return url_series
    
    @Scraper.try_loop(2)
    def _extract_models_from_series(self, url: str) -> set:
        
        def extract_model_url(driver)->set:
            url_models_set= set()
            radio_btns = driver.find_elements(By.CSS_SELECTOR, '.SizeTile_button_wrapper__rIeR3')
            for btn in radio_btns:
                self.web_driver.move_element_to_center(btn)
                btn.click()
                time.sleep(self.wait_time)
                url =  driver.current_url
                url_models_set.add(url.strip())
            return url_models_set
        
        url_models_set = set()
        CustomException(message=f"error_extract_models_from_series: {url}")
        try: 
            driver = self.web_driver.get_chrome()
            driver.get(url=url)
            time.sleep(self.wait_time)
            url_models_set =  extract_model_url(driver)  
        except CustomException as e:
            print(e)
        return url_models_set
            
    @Scraper.try_loop(2)
    def _extract_model_details(self, url: str='') -> dict:
    
        def extract_model(driver):
            label_element = driver.find_element(By.CLASS_NAME,"Header_sku__PBGyN")
            label = label_element.text
            model = label.split()[-1]
            return {"model": model}
            
        def extract_description(driver)->dict: 
            descriptionn = driver.find_element(By.CLASS_NAME,'Header_productTitle__48wOA').text        
            return {"description": descriptionn}
             
        def extract_prices(driver)->dict:
            prices_dict = dict()
            try:
                price = driver.find_element(By.CLASS_NAME,'Header_newdesc__NRnRP')          
                split_price = price.text.split('$')
                prices = split_price
                if len(prices) > 2:
                    
                    price_now = float(prices[-2].replace(',', ''))
                    price_original = float(prices[-1].replace(',', ''))
                    price_gap = price_original - price_now
                    dict_info["price"] = price_now
                    dict_info["price_original"] = price_original
                    dict_info["price_gap"] = round(price_gap, 1)
                else:
                    price_now = float(prices[-1].replace(',', ''))
                    dict_info["price"] = price_now
                    prices_dict['price_original'] = price_now
                    prices_dict['price_gap'] = 0.0
            except:
                prices_dict['price'] = float('nan')
                prices_dict['price_original'] = float('nan')
                prices_dict['price_gap'] = float('nan')
            return prices_dict
            

        
        dict_info = {}
        CustomException(message=f"error_extract_model_details: {url}")
        if self.tracking_log: print(" Connecting to", url)
        try: 
            driver = self.web_driver.get_chrome()
            driver.get(url=url)
            time.sleep(self.wait_time)
            
            # Extract model
            dict_info.update(extract_model(driver))
            dict_info.update(extract_description(driver))
            dict_info.update(extract_prices(driver))
            dict_info.update(ModelScraper_se.extract_info_from_model(dict_info.get("model")))
                
            if self.tracking_log:
                self._dir_model = f"{self.log_dir}/{dict_info['model']}"
                self.file_manager.make_dir(self._dir_model)
            return dict_info
        except CustomException as e:
            pass
        finally:
            driver.quit()

    @Scraper.try_loop(5)
    def _extract_global_specs(self, url: str) -> dict:
       
        def set_driver(url):
            driver = self.web_driver.get_chrome()
            driver.get(url=url)
            time.sleep(self.wait_time)
            return driver
        
        def find_spec_tab(driver) -> None:
            try: 
                element_specs = driver.find_element(By.CLASS_NAME, f"tl-btn-expand")
                self.web_driver.move_element_to_center(element_specs)
                time.sleep(self.wait_time)
                
                element_specs.click()
                time.sleep(self.wait_time)
            except:
                pass
                time.sleep(self.wait_time)
            return None 
            
        def extract_spec_detail(driver) -> dict:  
            dict_spec = {}
            try:
                table_elements= driver.find_elements(By.CLASS_NAME, "subSpecsItem.Specs_subSpecsItem__acKTN")
            except:                
                try:
                    table_elements= driver.find_elements(By.CLASS_NAME, "Specs_specRow__e9Ife.Specs_specDetailList__StjuR")
                except:
                    table_elements= driver.find_elements(By.CLASS_NAME, "spec-highlight__container")
                    
                
                
            for element in table_elements:
                try:
                    item_name = element.find_element(By.CLASS_NAME, 'Specs_subSpecItemName__IUPV4').text
                    item_value = element.find_element(By.CLASS_NAME, 'Specs_subSpecsItemValue__oWnMq').text
                except:
                    try:
                        item_name = element.find_element(By.CLASS_NAME, 'Specs_subSpecItemName__IUPV4.Specs_type-p2__s07Sd').text
                        item_value = element.find_element(By.CLASS_NAME, 'Specs_type-p2__s07Sd.Specs_subSpecsItemValue__oWnMq').text 
                    except:
                        item_name = element.find_element(By.CLASS_NAME, "spec-highlight__title").text
                        item_value = element.find_element(By.CLASS_NAME, "spec-highlight__value").text 

                     
                label = re.sub(r'[\n?]', '', item_name)
                content = re.sub(r'[\n?]', '', item_value)
                original_label = label
                while label in dict_spec and dict_spec.get(label)!=content:
                    asterisk_count = label.count('*')
                    label = f"{original_label}{'*' * (asterisk_count + 1)}"

                dict_spec[label] = content
            return dict_spec
    
        dict_spec = {}
        CustomException(message=f"error_extract_global_specs: {url}")
        try:
            driver = set_driver(url)
            if self.tracking_log:
                stamp_today = self.file_manager.get_datetime_info(include_time=False)
                stamp_url = self.file_manager.get_name_from_url(url)
                driver.save_screenshot(f"./{self._dir_model}/{stamp_url}_0_model_{stamp_today}.png")
     
            find_spec_tab(driver)
            
            if self.tracking_log:
                driver.save_screenshot( f"./{self._dir_model}/{stamp_url}_1_element_all_specs_{stamp_today}.png")
                
            dict_spec = extract_spec_detail(driver)
            
            if self.tracking_log:
                print(f"Received information from {url}")
            return dict_spec
        except CustomException as e:
            pass
        finally:
            driver.quit()
                
    @staticmethod       
    def extract_info_from_model(model: str)->dict:
    
        def extract_grade_and_model(model: str):
            grade = model[:2] 
            model=  model[2:]    
            return grade, model
            
        def extract_size_and_model(model: str):
            match = re.match(r'\d+', model)
            if match:
                leading_number = match.group()  # 앞의 숫자 부분
                rest = re.sub(r'^\d+', '', model)   # 숫자 제거 후 나머지 부분
                return leading_number, rest
            else:
                return None, model  # 숫자가 없으면 None과 원래 문자열을 반환

        def extract_year_and_model(model: str):
        
            match = re.search(r'([A-Za-z]+\d+)([A-Za-z]+)', model)
            if match:
                year = match.group(2) if len(match.group(2)) <= 1 else match.group(2)[0]
                model = match.group(1)  
                return year, model+year
            else:
                return None, model    


        dict_info = {}
        model = model.lower()  # 대소문자 구분 제거
        model = model[:-4]
        dict_info = {}
        year_mapping = {'qn':
                            {
                            't': "2021",    
                            'b': "2022",
                            'c': "2023",
                            'd': "2024",
                            'd': "2024",
                            'e': "2025",
                            'f': "2026"},
                        'un':{ 
                            'c': "2023",
                            'd': "2024",
                            'e': "2025",
                            'f': "2026",
                            }
                        }
        dict_info["grade"], model = extract_grade_and_model(model) 
        dict_info["size"], model = extract_size_and_model(model)
        dict_info["year"], model = extract_year_and_model(model)
        dict_info["series"] = model
        
        if "qn" in dict_info["grade"] or "kq" in dict_info["grade"]:         
            dict_info["year"] = year_mapping.get('qn').get(dict_info["year"], None)
        elif "un" in dict_info["grade"] :
            dict_info["year"] = year_mapping.get('un').get(dict_info["year"], None)
        else:
            dict_info["year"] = None
        return dict_info