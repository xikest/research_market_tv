from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
from tqdm import tqdm
import re
from selenium.webdriver.common.by import By
from tools.file import FileManager
from market_research.scraper._scraper_scheme import Scraper




class ModelScraper_se(Scraper):
    def __init__(self, enable_headless=True,
                 export_prefix="sse_model_info_web", intput_folder_path="input", output_folder_path="results",
                 verbose: bool = False, wait_time=2):

        super().__init__(enable_headless=enable_headless, export_prefix=export_prefix,
                         intput_folder_path=intput_folder_path, output_folder_path=output_folder_path)

        self.tracking_log = verbose
        self.wait_time = wait_time
        self.file_manager = FileManager
        self.log_dir = "logs/sse/models"
        if self.tracking_log:
            FileManager.make_dir(self.log_dir)

    def get_models_info(self, format_df: bool = True, show_visit:bool=False):

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
            df_models = df_models.drop(['Series', 'Size'], axis=1)
            return df_models
        else:
            return dict_models

    def _get_url_series(self) -> set:
        """
        Get the series URLs by scrolling down the main page.
        """
        url = "https://www.samsung.com/us/televisions-home-theater/tvs/oled-tvs/"
        prefix = "https://www.samsung.com"
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
                            elements = soup.find_all('a', class_="ProductCard-learnMore-1030346118 isTvPf")
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
        print(url_series)
        return url_series

    def _get_models(self, url: str, prefix="https://www.samsung.com/") -> dict:
        """
        Extract all model URLs from a given series URL.
        """
        print(url)
        try_total = 5
        for cnt_try in range(try_total):
            try:
                dict_url_models = {}


                driver = self.web_driver.get_chrome()
                driver.get(url=url)
                time.sleep(self.wait_time)
                radio_btns = driver.find_elements(By.CLASS_NAME, "SizeTile_button_wrapper__rIeR3")
                
                for btn in radio_btns:
                    btn.click()
                    time.sleep(self.wait_time)
                    element_url =  driver.current_url
                    print(element_url)
                    label = self.file_manager.get_name_from_url(element_url)
                    dict_url_models[label] = element_url.strip()

                if self.tracking_log:
                    print(f"SSE {self.file_manager.get_name_from_url(url)[4:]} series: {len(dict_url_models)}")
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
        
        dict_info["description"] = ""
        descriptions = [
            ('h2', 'MuiTypography-root MuiTypography-subtitle2 css-8oa1vg'),
            ('h1', 'MuiTypography-root MuiTypography-subtitle2 css-8oa1vg'),
            ('h1', 'MuiTypography-root MuiTypography-h5 css-vnteo9')
        ]

        for tag, class_name in descriptions:
            try:
                dict_info["description"] = soup.find(tag, class_=class_name).text.strip()
                if dict_info["description"]:
                    break  # 첫 번째로 찾은 description이 있으면 종료
            except AttributeError:
                pass  # 찾지 못했을 때는 그냥 넘어감
                
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
        model = model.lower()  # 대소문자 구분 제거
        dict_info = {}

        # 연도 매핑
        year_mapping = {
            '1': "2021",
            '2': "2022",
            '3': "2023",
            '4': "2024",
            '5': "2025",
            '6': "2026",
            'p': "2021",
            'q': "2022",
            'r': "2023",
            's': "2024",
            't': "2025",
            'u': "2026",
        }
        
        # "oled"가 포함된 모델 처리
        if "oled" in model:
            model = model[:-3].replace("oled", "")
            dict_info["grade"] = "oled"
            dict_info["year"] = model[-1]
            dict_info["series"] = model[-2:-1]
            dict_info["size"] = model[:-2]
            dict_info["year"] = year_mapping.get(dict_info.get("year"), None)
        
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
            dict_info["series"] = model[:-2]
            dict_info["year"] = year_mapping.get(dict_info.get("year"), None)
            dict_info
        
        # "lx"가 포함된 모델 처리
        elif "lx" in model:
            model_split = model.split("lx")
            dict_info["grade"] = "flexble"
            dict_info["size"] = model_split[0]
            model = model_split[-1]
            dict_info["year"] = model[0]
            dict_info["series"] = model[1]
            dict_info["year"] = year_mapping.get(dict_info.get("year"), None)
        
        # "u"가 포함된 모델 처리
        elif "u" in model:
            model = model[:-3]
            model_split = model.split("u")
            dict_info["grade"] = "u"
            dict_info["size"] = model_split[0]
            model = model_split[-1]
            dict_info["year"] = model[0]
            dict_info["series"] = model[1:]
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
