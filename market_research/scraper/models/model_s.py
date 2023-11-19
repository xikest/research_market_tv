from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
from tqdm import tqdm
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from market_research.tools import WebDriver, FileManager
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler

class ModelScraper_s:
    def __init__(self, webdriver_path: str, browser_path: str=None, enable_headless=True, verbose=False):
        self.wait_time = 1
        self.web_driver = WebDriver(executable_path=webdriver_path, browser_path=browser_path, headless=enable_headless)
        self.file_manager = FileManager
        self.log_dir = "logs/sony/models"
        self.tracking_log = verbose
        if self.tracking_log:
            FileManager.make_dir(self.log_dir)


    def get_models_info(self, foramt_output:str='df'):
        print("sony")
        url_series_set = self._get_url_series()
        url_series_dict = {}
        for url in url_series_set:
            url_models = self._get_models(url=url)
            url_series_dict.update(url_models)

        print("Total Model:", len(url_series_dict))
        dict_models = {}
        for key, url_model in tqdm(url_series_dict.items()):
            try:
                dict_info = self._get_model_info(url_model)
                #time.sleep(1)
                dict_models[key] = dict_info
                dict_spec = self._get_global_spec(url=url_model)
                dict_models[key].update(dict_spec)
                #time.sleep(1)
            except Exception as e:
                print(f"Failed to get info from {key}")
                # print(e)
                pass

        if foramt_output == "df":
            return pd.DataFrame.from_dict(dict_models).T
        else:
            return dict_models


    def _get_url_series(self) -> set:
        """
        Get the series URLs by scrolling down the main page.
        """
        url = "https://electronics.sony.com/tv-video/televisions/c/all-tvs/"
        prefix = "https://electronics.sony.com/"
        step = 200
        url_series = set()
        try_total = 5
        print("The website scan starts")
        for _ in range(try_total):
            driver = self.web_driver.get_chrome()
            try:
                driver.get(url=url)
                time.sleep(1)
                scroll_distance_total = self.web_driver.get_scroll_distance_total()
                scroll_distance = 0

                while scroll_distance < scroll_distance_total:
                    for _ in range(2):
                        html = driver.page_source
                        soup = BeautifulSoup(html, 'html.parser')

                        elements = soup.find_all('a', class_="custom-product-grid-item__product-name")
                        for element in elements:
                            url_series.add(prefix + element['href'].strip())

                        driver.execute_script(f"window.scrollBy(0, {step});")
                        time.sleep(1)
                        #2
                        scroll_distance += step
                driver.quit()
                break
            except Exception as e:
                driver.quit()
                print(f"Try collecting {_ + 1}/{try_total}")
                # print(e)
        print("The website scan has been completed.")
        print(f"total Series: {len(url_series)}ea")
        return url_series

    def _get_models(self, url: str, prefix="https://electronics.sony.com/", static_mode=True) -> dict:
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
                        time.sleep(1)
                        #5
                        page_content = driver.page_source

                    soup = BeautifulSoup(page_content, 'html.parser')
                    elements = soup.find_all('a', class_='custom-variant-selector__item')

                    for element in elements:
                        try:
                            element_url = prefix + element['href']
                            label = self.file_manager.get_name_from_url(element_url)
                            dict_url_models[label] = element_url.strip()
                        except Exception as e:
                            print(f"Getting series error ({e})")
                            pass

                print(f"SONY {self.file_manager.get_name_from_url(url)[4:]} series: {len(dict_url_models)}ea")
                for key, value in dict_url_models.items():
                    if self.tracking_log:
                        print(f'{key}: {value}')

                return dict_url_models
            except Exception as e:
                print(f"_get_models try: {cnt_try + 1}/{try_total}")
                # print(e)

    def _get_model_info(self, url: str) -> dict:
        """
        Extract model information (name, price, description) from a given model URL.
        """
        response = requests.get(url)
        if self.tracking_log:
            print(" Connecting to", url)

        page_content = response.text
        soup = BeautifulSoup(page_content, 'html.parser')
        dict_info = {}
        label = soup.find('h2', class_='product-intro__code').text.strip()
        dict_info["model"] = label.split()[-1]
        dict_info["price"] = soup.find('div', class_='custom-product-summary__price').text.strip()
        dict_info.update(self._extract_model_info(dict_info.get("model")))
        dict_info["description"] = soup.find('h1', class_='product-intro__title').text.strip()

        return dict_info

    def _get_global_spec(self, url: str) -> dict:
        """
        Extract global specifications from a given model URL.
        """
        try_total = 10
        model = None
        driver = None

        for cnt_try in range(try_total):
            try:
                dict_spec = {}
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

                time.sleep(1)
                #5
                element_spec = driver.find_element(By.ID, "PDPSpecificationsLink")
                self.web_driver.move_element_to_center(element_spec)

                if self.tracking_log:
                    driver.save_screenshot(f"./{dir_model}/{stamp_url}_1_move_to_spec_{stamp_today}.png")

                time.sleep(1)
                #5
                element_click_spec = driver.find_element(By.ID, 'PDPSpecificationsLink')
                element_click_spec.click()
                time.sleep(1)
                #5

                if self.tracking_log:
                    driver.save_screenshot(
                        f"./{dir_model}/{stamp_url}_2_after_click_specification_{stamp_today}.png")

                try:
                    element_see_more = driver.find_element(By.XPATH,
                                                            '//*[@id="PDPOveriewLink"]/div[1]/div/div/div[2]/div/app-product-specification/div/div[2]/div[3]/button')
                    self.web_driver.move_element_to_center(element_see_more)

                    if self.tracking_log:
                        driver.save_screenshot(
                            f"./{dir_model}/{stamp_url}_3_after_click_see_more_{stamp_today}.png")

                    element_see_more.click()
                except:
                    print("Cannot find the 'see more' button on the page; trying to search for another method.")
                    element_see_more = driver.find_element(By.XPATH,
                                                            '//*[@id="PDPOveriewLink"]/div[1]/div/div/div[2]/div/app-product-specification/div/div[2]/div[2]/button')
                    self.web_driver.move_element_to_center(element_see_more)

                    if self.tracking_log:
                        driver.save_screenshot(
                            f"./{dir_model}/{stamp_url}_3_after_click_see_more_{stamp_today}.png")

                    element_see_more.click()

                time.sleep(1)
                #10
                driver.find_element(By.ID, "ngb-nav-0-panel").click()

                for _ in range(15):
                    elements = driver.find_elements(By.CLASS_NAME,
                                                    "full-specifications__specifications-single-card__sub-list")

                    for element in elements:
                        soup = BeautifulSoup(element.get_attribute("innerHTML"), 'html.parser')
                        dict_spec.update(self._soup_to_dict(soup))

                    ActionChains(driver).key_down(Keys.PAGE_DOWN).perform()

                if self.tracking_log:
                    driver.save_screenshot(f"./{dir_model}/{stamp_url}_4_end_{stamp_today}.png")

                driver.quit()
                if self.tracking_log:
                    print(f"Received information from {url}")
                return dict_spec

            except Exception as e:
                print(f"An error occurred on page 3rd : {model} try {cnt_try + 1}/{try_total}")
                # print(e)
                driver.quit()
                pass

    def _extract_model_info(self, model):
        """
        Extract additional information from the model name.
        """
        dict_info = {}
        dict_info["year"] = model.split("-")[1][-1]
        dict_info["series"] = model.split("-")[1][2:-1]
        dict_info["size"] = model.split("-")[1][:2]
        dict_info["grade"] = model.split("-")[0]

        year_mapping = {
            "N": 2025,
            "M": 2024,
            'L': 2023,
            'K': 2022,
            'J': 2021,
            # Add additional mappings as needed
        }

        try:
            dict_info["year"] = year_mapping.get(dict_info.get("year"))
        except:
            dict_info["year"] = ""

        return dict_info

    def _soup_to_dict(self, soup):
        """
        Convert BeautifulSoup soup to dictionary.
        """
        try:
            h4_tag = soup.find('h4').text.strip()
            p_tag = soup.find('p').text.strip()
        except Exception as e:
            print("Parser error", e)
            h4_tag = soup.find('h4').text.strip()
            p_tag = ""

        return {h4_tag: p_tag}

class DataCleanup_s:
    """
    cleanup = DataCleanup(df)
    df = cleanup.get_df_cleaned()
    df_prices = cleanup.get_price_df()
    """

    def __init__(self, df, stop_words=None):
        self.df = df
        self.df_prices = None
        if stop_words is None:
            stop_words = self._call_stop_words()
        self.stop_words = [stop_word.lower() for stop_word in stop_words]
        self._preprocess_df()
        self._create_price_df()
        self._cleanup_columns()

    def _call_stop_words(self):
        stop_words_list = ["price", "model", "description",
                           "weight", "dimension", "size", "stand", "W x H", "W x H x D", "Wi-Fi", "atore", "audio",
                           "frame", "length", "qty",
                           "power", "usb", "channels", "language", "timer", "apple", "TALKBACK", "voice", "sensor",
                           "system", "channel", "storage", "cable",
                           "style", "protection", "hdmi", "energy", "sound", "camera", "subwoofer", "satellite",
                           "input", "output", "caption", "headphone", "radio", "text", "internet", "dsee", "speaker",
                           "bluetooth", "accessories", "mercury", "remote", "smart", "acoustic", "support",
                           "wallmount", "mic", "network", "android", "ios", "miracast",
                           "operating", "store", "clock", "rs-232c", "menu", "mute", "4:3", "hdcp", "wide",
                           "built", "tuners", "demo", "presence", "switch", "reader", "face", "surround", "phase",
                           "batteries", "info", "Parental", "setup", "aspect", "dashboard", "formats", "accessibility",
                           "ci+",
                           "bass", "master", "shut", "sorplas", "volume", "wireless", "china",
                           "hole", "program", "manual", "latency"]
        return stop_words_list

    def _preprocess_df(self):
        self.df = self.df.sort_values(["year", "series", "size", "grade"], axis=0, ascending=False)
        self.df = (self.df.map(lambda x: x.replace("  ", " ") if isinstance(x, str) else x)  # 공백 2개는 하나로 변경
                   .map(lambda x: x.replace("™", "") if isinstance(x, str) else x)  # ™ 제거
                   .map(lambda x: x.replace("®", "") if isinstance(x, str) else x)  # ® 제거
                   .map(lambda x: x.replace("\n\n", "\n ") if isinstance(x, str) else x)
                   .map(lambda x: x.replace(" \n", "\n ") if isinstance(x, str) else x)
                   .map(lambda x: x.strip() if isinstance(x, str) else x)  # 문장 끝 공백 제거
                   .map(lambda x: x.lower() if isinstance(x, str) else x))

        self.df.columns = [x.replace("  ", " ").replace("™", "").replace("®", "").strip() if isinstance(x, str) else x
                           for x in self.df.columns]
        self.df.columns = self.df.columns.map(lambda x: x.lower())

    def _create_price_df(self):
        ds_prices = (self.df.loc[:, ["price"]]
                     .map(lambda x: x.split(" ") if isinstance(x, str) & len(x) > 0 else np.nan).dropna()
                     .map(lambda x: [x[0], x[0]] if len(x) < 2 else x))  # idx 정보 보관 및 스플릿

        list_prices = [[idx, prices[0], prices[1], float(prices[1].replace(',', '').replace('$', '')) - float(
            prices[0].replace(',', '').replace('$', ''))]
                       for idx, prices in zip(ds_prices.index, ds_prices.price)]
        df_prices = pd.DataFrame(list_prices, columns=["idx", "price_now", "price_release", "price_discount"])
        df_prices = df_prices.set_index("idx")
        self.df = pd.merge(df_prices, self.df, left_index=True, right_index=True).drop(["price"], axis=1)
        self.df_prices = self.df[
            ["year", "display type", 'size', "series", 'model', 'price_release', 'price_now', "price_discount",
             'description']]

    def get_price_df(self):
        if self.df_prices is not None:
            return self.df_prices.sort_values(["price_discount", "year", "display type", "series", "size", ],
                                              ascending=False)

    def _cleanup_columns(self):
        col_remove = []
        for column in self.df.columns:
            for stop_word in self.stop_words:
                if stop_word in column:
                    col_remove.append(column)
        self.df = self.df.drop(col_remove, axis=1)
        self.df = self.df.drop_duplicates()
        self.df = pd.merge(self.df_prices[['model', 'size']], self.df, left_index=True, right_index=True)

    def get_df_cleaned(self):
        if self.df is not None:
            df = self.df.set_index(["year", "display type", "series"]).drop(
                ["model", "size", "grade"], axis=1)
            df = df.fillna("-")
            return df


class Plotting_s:

    def __init__(self, df):
        self.df = df

    def group_plot_bar(self, col_group: list = ["display type", "size"], col_plot: str = "price_discount",
                       ylabel_mark: str = "$", save_plot_name=None):
        col_group_str = '&'.join(col_group)
        grouped_data = self.df.groupby(col_group)[col_plot].mean().sort_values(ascending=False)

        plt.figure(figsize=(10, 6))  # 적절한 크기로 조정

        grouped_data.plot(kind="bar")
        plt.ylabel(ylabel_mark)
        sns.despine()

        if save_plot_name is None:
            save_plot_name = f"barplot_{col_plot}_to_{col_group_str}.png"
        plt.savefig(save_plot_name, bbox_inches='tight')  # bbox_inches='tight'를 추가하여 레이블이 잘림 방지
        plt.show()


    def heatmap(self, df:pd.DataFrame, save_plot_name=None, title="SONY Spec" ,cmap="Blues",figsize=(12, 12), cbar=False, start_order_list:list=["-"]):
        """
        # YlGnBu
        # GnBu
        # Oranges
        # viridis
        # plasma
        # cividis
        # inferno
        # magma
        # coolwarm
        # Blues
 =
        """
        color_list = []
        for i, column in enumerate(df):
            color_list.extend(df.iloc[:, i])

        for i, start_order in  enumerate(start_order_list):
            if start_order in color_list:
                reorder = color_list.index(start_order)
                color_list.insert(i, color_list.pop(reorder))
        
        color_dict = {k: v for v, k in enumerate(pd.Series(color_list, name="color").drop_duplicates().to_list())}
        data_df = df.apply(lambda x:x.replace(color_dict))

        scaler = MinMaxScaler()
        data_df[data_df.columns] = scaler.fit_transform(data_df[data_df.columns])

        plt.figure(figsize=figsize)
        sns.heatmap(data_df.T, cmap=cmap, cbar=cbar)
        plt.title(title)
        if save_plot_name is None:
            save_plot_name = f"heatmap_for_{title}.png"
        plt.savefig(save_plot_name, bbox_inches='tight')  # bbox_inches='tight'를 추가하여 레이블이 잘림 방지
        plt.show()
