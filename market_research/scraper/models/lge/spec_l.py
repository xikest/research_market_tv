from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
from tqdm import tqdm
import re
from selenium.webdriver.common.by import By
from tools.file import FileManager
from market_research.scraper._scraper_scheme import Scraper




class ModelScraper_l(Scraper):
    def __init__(self, enable_headless=True,
                 export_prefix="lge_model_info_web", intput_folder_path="input", output_folder_path="results",
                 verbose: bool = False, wait_time=2):

        super().__init__(enable_headless=enable_headless, export_prefix=export_prefix,
                         intput_folder_path=intput_folder_path, output_folder_path=output_folder_path)

        self.tracking_log = verbose
        self.wait_time = wait_time
        self.file_manager = FileManager
        self.log_dir = "logs/lge/models"
        if self.tracking_log:
            FileManager.make_dir(self.log_dir)

    def get_models_info(self, format_df: bool = True, show_visit:bool=False):
        # dict_models = {}
        # dict_info = self._get_model_info()
        # dict_models["key"] = dict_info
        # dict_spec = self._get_global_spec()
        # dict_models["key"].update(dict_spec)
        # df_models = pd.DataFrame.from_dict(dict_models).T
        # return df_models
        
        print("collecting models")
        url_series_set = self._get_url_series()
        url_series_dict = {}
        for url in url_series_set:
            url_models = self._get_models(url=url)
            url_series_dict.update(url_models)
        print("number of total model:", len(url_series_dict))
        print("collecting spec")
        visit_url_dict = {}
        dict_models = {}
        cnt_loop=2
        
        for cnt in range(cnt_loop):#main try
            for key, url_model in tqdm(url_series_dict.items()):
                try:
                    dict_info = self._get_model_info(url_model)
                    dict_models[key] = dict_info
                    dict_spec = self._get_global_spec(url=url_model)
                    dict_models[key].update(dict_spec)
                    visit_url_dict[key] = url_model
                except Exception as e:
                    if cnt == cnt_loop - 1 :
                        print(f"\nFailed to get info from {key}")
                        print(e)
                    pass
            break
        if show_visit:
            print("\n")
            for model, url in visit_url_dict.items():  print(f"{model}: {url}")

        if format_df:
            df_models = pd.DataFrame.from_dict(dict_models).T
            FileManager.df_to_excel(df_models.reset_index(), file_name=self.output_xlsx_name, sheet_name="raw_na",
                                    mode='w')
            return df_models
        else:
            return dict_models

    def _get_url_series(self) -> set:
        """
        Get the series URLs by scrolling down the main page.
        """
        url = "https://www.lg.com/us/tvs"
        prefix = "https://www.lg.com/"
        step = 200
        url_series = set()
        try_total = 5
        for _ in range(2): #page_checker
            for _ in range(try_total):
                driver = self.web_driver.get_chrome()
                try:
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
                    driver.quit()
                    break
                except Exception as e:
                    driver.quit()
                    if self.tracking_log:
                        print(f"Try collecting {_ + 1}/{try_total}")
                        print(e)
        print("The website scan has been completed.")
        print(f"number of total series: {len(url_series)}")
        return url_series

    def _get_models(self, url: str, prefix="https://www.lg.com/", static_mode=True) -> dict:
        """
        Extract all model URLs from a given series URL.
        """
        try_total = 5
        for cnt_try in range(try_total):
            try:
                dict_url_models = {}
                for _ in range(3):
                    if static_mode:
                        response = requests.get(url)
                        page_content = response.text
                    else:
                        driver = self.web_driver.get_chrome()
                        driver.get(url=url)
                        time.sleep(self.wait_time)
                        page_content = driver.page_source
                    soup = BeautifulSoup(page_content, 'html.parser')
                    elements = soup.find_all('a', class_='css-1a0ki8h')

                    for element in elements:
                        try:
                            element_url = prefix + element['href']
                            label = self.file_manager.get_name_from_url(element_url)
                            dict_url_models[label] = element_url.strip()
                        except Exception as e:
                            print(f"Getting series error ({e})")
                            pass
                if self.tracking_log:
                    print(f"LGE {self.file_manager.get_name_from_url(url)[4:]} series: {len(dict_url_models)}")
                for key, value in dict_url_models.items():
                    if self.tracking_log:
                        print(f'{key}: {value}')
                return dict_url_models
            except Exception as e:
                if self.tracking_log:
                    print(f"_get_models try: {cnt_try + 1}/{try_total}")

    def _get_model_info(self, url: str='https://www.lg.com/us/tvs/lg-oled77g4wua-oled-4k-tv-b') -> dict:
        """
        Extract model information (name, price, description) from a given model URL.
        """
        response = requests.get(url)
        if self.tracking_log:
            print(" Connecting to", url)
        page_content = response.text
        soup = BeautifulSoup(page_content, 'html.parser')
        dict_info = {}
        label = soup.find('span', class_="MuiTypography-root MuiTypography-overline css-rrulv7").text.strip()
        dict_info["model"] = label.split()[-1]
        try:
            price = soup.find('div', class_='MuiGrid-root MuiGrid-item css-8wacqv').text.strip()
            split_price = price.split('$')
            pattern = r'\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
            prices = [re.search(pattern, part).group() for part in split_price if re.search(pattern, part)]

            if len(prices) == 3:
                dict_info["price"] = float(prices[0].replace(',', ''))
                dict_info["price_gap"] = float(prices[1].replace(',', ''))
                dict_info["price_original"] = float(prices[2].replace(',', ''))
            else:
                dict_info["price"] = price
        except:
            dict_info["price"] = None
        dict_info.update(self._extract_model_info(dict_info.get("model")))
        try:
            dict_info["description"] = soup.find('h2',
                                                 class_='MuiTypography-root MuiTypography-subtitle2 css-8oa1vg').text.strip()
        except:
            try:
                dict_info["description"] = soup.find('h1',
                                                     class_='MuiTypography-root MuiTypography-subtitle2 css-8oa1vg').text.strip()
            except:
                dict_info["description"] = ""
        if self.tracking_log:
            print(dict_info)
        return dict_info

    def _get_global_spec(self, url: str='https://www.lg.com/us/tvs/lg-oled77g4wua-oled-4k-tv-b') -> dict:
        """
        Extract global specifications from a given model URL.
        """
        try_total = 1
        model = None
        driver = None
        case = 0
        for cnt_try in range(try_total):
            try:
                driver = self.web_driver.get_chrome()
                driver.get(url=url)
                model = self.file_manager.get_name_from_url(url)
                dir_model = f"{self.log_dir}/{model}"
                stamp_today = self.file_manager.get_datetime_info(include_time=False)
                stamp_url = self.file_manager.get_name_from_url(url)
                if self.tracking_log:
                    self.file_manager.make_dir(dir_model)
                if self.tracking_log:
                    driver.save_screenshot(f"./{dir_model}/{stamp_url}_0_model_{stamp_today}.png")
                time.sleep(self.wait_time)
                
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
                

                if self.tracking_log:
                    driver.save_screenshot(
                        f"./{dir_model}/{stamp_url}_1_element_all_specs_{stamp_today}.png")
                dict_spec = dict()
                spec_elements = driver.find_elements(By.CSS_SELECTOR, '.MuiBox-root.css-1nnt9ji')
                for spec_element in spec_elements:
                    label = spec_element.find_element(By.CLASS_NAME,
                                                      'MuiTypography-root.MuiTypography-body3.css-11mszpq').text.strip()
                    content = spec_element.find_element(By.CLASS_NAME,
                                                        'MuiTypography-root.MuiTypography-body2.css-1yx8hz4').text.strip()
                    if label != '':
                        # if self.tracking_log:
                        #     print(f"{label}: {content}")
                        dict_spec[label] = content

                dict_spec.pop("*", None)

                driver.quit()
                if self.tracking_log:
                    print(f"Received information from {url}")
                return dict_spec
            except Exception as e:
                if self.tracking_log:
                    print(f"An error occurred on page 3rd : {model} try {cnt_try + 1}/{try_total}")
                    print(e)
                driver.quit()
                pass

    def _extract_model_info(self, model: str):
        dict_info = {}
        # 시리즈와 연도, 등급을 분리하는 정규식
        pattern = r'(?P<product_type>[A-Za-z]+)(?P<size>\d+)(?P<series>[A-Za-z]+)(?P<year>\d)(?P<grade>[A-Za-z]+)'
        match = re.search(pattern, model.lower())
        
        if match:
            # 그룹화된 각 부분을 추출
            dict_info["type"] = match.group("product_type")  # 예: 'oled'
            dict_info["size"] = match.group("size")          # 예: '77'
            dict_info["series"] = match.group("series")      # 예: 'g'
            dict_info["year"] = match.group("year")          # 예: '4'
            dict_info["grade"] = match.group("grade")        # 예: 'wua'

        year_mapping = {
            '1': "2021",
            '2': "2022",
            '3': "2023",
            '4': "2024",
            '5': "2025",
            '6': "2026",
            # Add additional mappings as needed
        }

        # 연도 매핑
        dict_info["year"] = year_mapping.get(dict_info.get("year"), None)
        
        return dict_info

    def _soup_to_dict(self, soup):
        """
        Convert BeautifulSoup soup to dictionary.
        """
        try:
            h4_tag = soup.find('h4').text.strip()
            p_tag = soup.find('p').text.strip()
        except:
            try:
                h4_tag = soup.find('h4').text.strip()
                p_tag = ""
            except Exception as e:
                print("Parser error", e)
                h4_tag = "Parser error"
                p_tag = "Parser error"
        return {h4_tag: p_tag}
