from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
from tqdm import tqdm
import re
from selenium.webdriver.common.by import By
from tools.file import FileManager
from market_research.scraper._scraper_scheme import Scraper, Modeler, CustomException
from market_research.scraper.models.visualizer.data_visualizer import DataVisualizer



class ModelScraper_l(Scraper, Modeler, DataVisualizer):
    def __init__(self, enable_headless=True,
                 export_prefix="lge_model_info_web", intput_folder_path="input", output_folder_path="results",
                 verbose: bool = False, wait_time=2, demo_mode:bool=False):

        Scraper.__init__(self, enable_headless=enable_headless, export_prefix=export_prefix,
                         intput_folder_path=intput_folder_path, output_folder_path=output_folder_path)

        self.tracking_log = verbose
        self.wait_time = wait_time
        self.file_manager = FileManager
        self.log_dir = "logs/lge/models"
        if self.tracking_log:
            FileManager.make_dir(self.log_dir)
            
        self._data = self._fetch_model_data(demo_mode=demo_mode)    
        DataVisualizer.__init__(self, df = self._data, maker='lge')
        pass

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
                except Exception as e:
                    if self.tracking_log:
                        print(f"fail to collect: {url}")
                        print(e)
            return dict_models
        
        def transform_format(dict_models, json_file_name: str) -> pd.DataFrame:
            df_models = pd.DataFrame.from_dict(dict_models).T
            df_models = df_models.drop(['Series', 'Size'], axis=1)
            df_models = df_models.dropna(subset=['price'])
            df_models.to_json(self.output_folder / json_file_name, orient='records', lines=True)
            return df_models
            
        if demo_mode:
            print("operating demo")
            df_models = pd.read_json('https://raw.githubusercontent.com/xikest/research_market_tv/main/json/l_scrape_model_data.json', orient='records', lines=True)
        else:
            print("collecting models")
            url_dict = find_urls()
            dict_models = extract_sepcs(url_dict)
            df_models = transform_format(dict_models, json_file_name="l_scrape_model_data.json")
            
        FileManager.df_to_excel(df_models.reset_index(), file_name=self.output_xlsx_name)
        return df_models
    
    @Scraper.try_loop(2)
    def _get_series_urls(self) -> set:

        def find_series_urls(url, prefix) -> set:
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
        
        url_series = find_series_urls( url = "https://www.lg.com/us/tvs", prefix = "https://www.lg.com/")
        print("The website scan has been completed.")
        print(f"total series: {len(url_series)}")
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
                    print(f"Getting series error ({e})")
                    pass
            return url_models_set
            
        url_models_set = set()
        CustomException(message=f"error_extract_models_from_series: {url}")
        try:
            soup = BeautifulSoup(requests.get(url).text, 'html.parser')
            elements = soup.find_all('a', class_='css-1a0ki8h')
            url_models_set = extract_model_url(elements)
        except CustomException as e:
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
                    prices_dict["price"] = float(prices[0].replace(',', ''))
                    prices_dict["price_gap"] = float(prices[1].replace(',', ''))
                    prices_dict["price_original"] = float(prices[2].replace(',', ''))
                else:
                    prices_dict["price"] = float(split_price[-1].replace(',', '')) 
            except:
                prices_dict["price"] = None
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
        

        
        dict_info = {}
        if self.tracking_log: print(" Connecting to", url)
        response = requests.get(url)
        page_content = response.text
        soup = BeautifulSoup(page_content, 'html.parser')
        
        dict_info.update(extract_model(soup))
        dict_info.update(extract_prices(soup))
        dict_info.update(extract_description(soup))
        dict_info.update(ModelScraper_l.extract_info_from_model(dict_info.get("model")))
           
        if self.tracking_log:
            self._dir_model = f"{self.log_dir}/{dict_info.get('model')}"
            self.file_manager.make_dir(self._dir_model)
        return dict_info

    @Scraper.try_loop(try_total=10)
    def _extract_global_specs(self, url: str) -> dict:
      
        def set_driver(url):
            driver = self.web_driver.get_chrome()
            driver.get(url=url)
            time.sleep(self.wait_time)
            return driver
        

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
                element_all_specs = driver.find_element(By.CLASS_NAME, "MuiTypography-root.MuiTypography-h6.MuiTypography-alignLeft.MuiLink-root.MuiLink-underlineAlways.css-kgbp8r")
                self.web_driver.move_element_to_center(element_all_specs)
                time.sleep(self.wait_time)
            return None 
        

        def extract_spec_detail(driver) -> dict:
            dict_spec = {}
            spec_elements = driver.find_elements(By.CSS_SELECTOR, '.MuiBox-root.css-1nnt9ji')
            for spec_element in spec_elements:
                label = spec_element.find_element(By.CLASS_NAME,
                                                    'MuiTypography-root.MuiTypography-body3.css-11mszpq').text.strip()
                content = spec_element.find_element(By.CLASS_NAME,
                                                    'MuiTypography-root.MuiTypography-body2.css-1yx8hz4').text.strip()
                if label != '':
                    
                    original_label = label
                    while label in dict_spec and dict_spec.get(label)!=content:
                        asterisk_count = label.count('*')
                        label = f"{original_label}{'*' * (asterisk_count + 1)}"
                    dict_spec[label] = content

            dict_spec.pop("*", None)            
            return dict_spec
       
        dict_spec = dict()
        CustomException(message=f"error_extract_global_specs: {url}")
        try:
            driver = set_driver(url)
            if self.tracking_log:
                stamp_today = self.file_manager.get_datetime_info(include_time=False)
 
                stamp_url = self.file_manager.get_name_from_url(url)
                driver.save_screenshot(f"./{self._dir_model}/{stamp_url}_0_model_{stamp_today}.png")                
            find_spec_tab(driver)   
            if self.tracking_log: driver.save_screenshot(f"./{self._dir_model}/{stamp_url}_1_element_all_specs_{stamp_today}.png")
            dict_spec = extract_spec_detail(driver)
            if self.tracking_log: print(f"Received information from {url}")
            return dict_spec
        except CustomException as e:
            pass
        finally:
            driver.quit()
            
    @staticmethod
    def extract_info_from_model(model: str)->dict:
        model = model.lower()  # 대소문자 구분 제거
        dict_info = {}

        # 연도 매핑
        year_mapping = {'oled':
                            {'1': "2021",
                            '2': "2022",
                            '3': "2023",
                            '4': "2024",
                            '5': "2025",
                            '6': "2026"},
                        'qned':
                            {'p': "2021",
                            'q': "2022",
                            'r': "2023",
                            'u': "2024"},
                        'u':{ 
                            'p': "2021",
                            'q': "2022",
                            'r': "2023",
                            't': "2024",}
                        }


        
        # "oled"가 포함된 모델 처리
        if "oled" in model:
            model = model[:-3].replace("oled", "")
            dict_info["grade"] = "oled"
            dict_info["year"] = model[-1]
            dict_info["series"] = model[-2:]
            dict_info["size"] = model[:-2]
            dict_info["year"] = year_mapping.get('oled').get(dict_info.get("year"), None)
        
        # "qned" 또는 "nano"가 포함된 모델 처리
        elif "qned" in model or "nano" in model:
            model = model[:-1] #마지막자리 삭제
            if "qned" in model:
                model_split = model.split("qned")
                dict_info["grade"] = "qned"
            else:
                model_split = model.split("nano")
                dict_info["grade"] = "nano"
            dict_info["size"] = model_split[0]
            model = model_split[-1]
            dict_info["year"] = model[-1]
            dict_info["series"] = model
            # dict_info["series"] = model[:-2]
            dict_info["year"] = year_mapping.get('qned').get(dict_info.get("year"), None)
            dict_info
        
        # "lx"가 포함된 모델 처리
        elif "lx" in model:
            model_split = model.split("lx")
            dict_info["grade"] = "flexble"
            dict_info["size"] = model_split[0]
            dict_info["series"] = model
            model = model_split[-1]
            dict_info["year"] = model[0]
            # dict_info["series"] = model[1]
            dict_info["year"] = year_mapping.get('oled').get(dict_info.get("year"), None)
        
        # "u"가 포함된 모델 처리
        elif "u" in model:
            model = model[:-3]
            model_split = model.split("u")
            dict_info["grade"] = "u"
            dict_info["size"] = model_split[0]
            model = model_split[-1]
            dict_info["year"] = model[0]
            dict_info["series"] = model[1:]
            dict_info["year"] =  year_mapping.get('u').get(dict_info.get("year"), None)

        return dict_info