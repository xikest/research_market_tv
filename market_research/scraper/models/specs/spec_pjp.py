import time
from tools.file import FileManager
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
from collections import OrderedDict
import pandas as pd
from market_research.scraper._scraper_scheme import Scraper
import pickle
class ModelScraper_pjp(Scraper):

    def __init__(self, enable_headless=True,
                 export_prefix="pana_model_info_web_jp", intput_folder_path="input", output_folder_path="results",
                 verbose: bool = False, wait_time=1):
        super().__init__(enable_headless=enable_headless, export_prefix=export_prefix,
                         intput_folder_path=intput_folder_path, output_folder_path=output_folder_path)

        self.tracking_log = verbose
        self.wait_time = wait_time
        self.file_manager = FileManager


    def fetch_model_data(self, format_df: bool = True, show_visit:bool=False):
        models_dict = {}
        specs_dict = {}
        url_model_dict = self._get_series_urls(step=1000)
        print("collecting models")
        for model, url in tqdm(url_model_dict.items()):
            specs_dict.update(self._extract_models_from_series(url=url,step=3000))
        print("collecting spec")
        visit_url_dict = {}
        cnt_loop=2
        for cnt in range(cnt_loop):#main try
            for model, url in tqdm(specs_dict.items()):
                try:
                    visit_url_dict[model] = url
                    modelspec = self._extract_model_details(model = model, url=url)
                    models_dict[model] = modelspec
                except Exception as e:
                    if cnt == cnt_loop - 1 :
                        print(f"\nFailed to get info from {model}")
                        print(e)
                    pass
            break
        if show_visit:
            print("\n")
            for model, url in visit_url_dict.items(): print(f"{model}: {url}")

        if format_df:
            df_models = pd.DataFrame.from_dict(models_dict).T
            FileManager.df_to_excel(df_models.reset_index(), file_name=self.output_xlsx_name, sheet_name="raw_jp", mode='w')
            return df_models
        else:
            return models_dict

    def _get_series_urls(self, url: str = "https://panasonic.jp/viera/products.html#4k_oled", step: int=200) -> dict:
        """
        스크롤 다운이 되어야 전체 웹페이지가 로딩되어, 스크롤은 selenium, page parcing은 BS4로 진행
        """
        step = step
        model_dict = {}
        trytotal = 3
        for trycnt in range(trytotal):
            driver = self.web_driver.get_chrome()
            driver.get(url=url)
            time.sleep(self.wait_time)
            scroll_distance_total = self.web_driver.get_scroll_distance_total()
            scroll_distance = 0
            while scroll_distance < scroll_distance_total:
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                try:
                    button_containers = soup.find_all('div', class_='image-content imagespart Intention_trial_click')
                    for container in button_containers:
                        link = container.find('a')['href']
                        if "products" in link:
                            model = link.split("products/")[-1].split(".")[0].replace('/',"")
                            link = "https://panasonic.jp/viera/products/" + model + ".html"
                            # print(link)
                            model_dict[model]=link
                    # 한 step씩 스크롤 내리기
                    driver.execute_script(f"window.scrollBy(0, {step});")
                    time.sleep(self.wait_time)  # 스크롤이 내려가는 동안 대기
                    scroll_distance += step
                except:
                    if self.tracking_log:
                        print(f"get_model_series error, re-try {trycnt}/{trytotal}")
                    driver.quit()
            driver.quit()
            break
        # print(f"number of total Modl: {len(model_dict)}")
        return model_dict


    def _extract_models_from_series(self, url: str = "https://panasonic.jp/viera/products/mz2500.html", step: int=200) -> dict:
        """
        스크롤 다운이 되어야 전체 웹페이지가 로딩되어, 스크롤은 selenium, page parcing은 BS4로 진행
        """
        step = step
        series_dict = {}
        trytotal = 3
        for trycnt in range(trytotal):
            driver = self.web_driver.get_chrome()
            driver.get(url=url)
            time.sleep(self.wait_time)
            scroll_distance_total = self.web_driver.get_scroll_distance_total()
            scroll_distance = 0
            while scroll_distance < scroll_distance_total:
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                try:
                    button_containers = soup.find_all('div', class_='button-area Intention_trial_click')
                    for container in button_containers:
                        link = container.find('a')['href']
                        if "spec" in link:
                            model = link.split('/')[-1].split("_")[0]
                            series_dict[model]=link
                    # 한 step씩 스크롤 내리기
                    driver.execute_script(f"window.scrollBy(0, {step});")
                    time.sleep(self.wait_time)  # 스크롤이 내려가는 동안 대기
                    scroll_distance += step
                except:
                    if self.tracking_log:
                        print(f"get_spec_series error, re-try {trycnt}/{trytotal}")
                    driver.quit()
            driver.quit()
            break
        # print(f"number of total Series: {len(series_dict)}")
        return series_dict

    def _extract_model_details(self, model='model', url: str = "https://panasonic.jp/viera/p-db/TH-65MZ2500_spec.html") -> list:
        spec_dict = OrderedDict()

        dictNote = {}
        TotalCnt = 5
        # spec_dict['model'] = model
        #=============================
        for tryCnt in range(TotalCnt):
            step: int = 200
            driver = self.web_driver.get_chrome()
            driver.get(url=url)
            time.sleep(self.wait_time)
            try:
                if self.tracking_log:
                    print("Trying with Selenium...")
                scroll_distance_total = self.web_driver.get_scroll_distance_total()
                scroll_distance = 0  # 현재까지 스크롤한 거리

                while scroll_distance < scroll_distance_total:
                    html = driver.page_source
                    soup = BeautifulSoup(html, 'html.parser')
                    table = soup.find('div', class_='table-container')

                    # if table is not None:  # 테이블이 있는 경우에만 데이터 추출
                    for row in table.find_all('tr'):
                        cells = row.find_all('td')
                        if len(cells) >= 1:
                            key = row.get_text(strip=True)
                            value = cells[0].get_text(strip=True)
                            key = key.replace(value, "")

                            key = self._parse_model_name(key)
                            value = self._parse_model_name(value)
                            # value = self._extract_global_specs(value)
                            spec_dict[key] = value
                    # print(spec_dict)
                    # ## 노트 추출
                    # notes = soup.select('.s5-specTableNote li')
                    # for note in notes:
                    #     bullet = note.select_one('.s5-specTableNote__bullet').text.strip()
                    #     text = note.select_one('.s5-specTableNote__text').text.strip()
                    #     dictNote[bullet] = " @" + text
                    # 한 step씩 스크롤 내리기
                    driver.execute_script(f"window.scrollBy(0, {step});")
                    time.sleep(self.wait_time)  # 스크롤이 내려가는 동안 대기
                    scroll_distance += step
                driver.quit()
                break  # 셀레니움으로 성공적으로 스크래핑했을 경우 반복문 탈출
            except Exception as e:
                driver.quit()
                if self.tracking_log:
                    print(f"Failed to scrape using Selenium. Trying with BS4...")

                response = requests.get(url)
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')
                table = soup.find('tbody', class_='SpecificationsTableSingle__Tbody')
                if table:
                    rows = table.find_all('tr')
                    key = None
                    for row in rows:
                        subhead_element = row.find('th', class_='SpecificationsTable__TableSubhead')
                        value_element = row.find('td', class_='SpecificationsTable__TableValue -isSelected')
                        if subhead_element:
                            key = subhead_element.get_text(strip=True)
                            key = self._parse_model_name(key)
                        if value_element and key:
                            value = value_element.get_text(strip=True)
                            # value = self._parse_model_name(value)
                            spec_dict[key] = self._extract_global_specs(value)
                    break  # BS4로 성공적으로 스크래핑했을 경우 반복문 탈출
                else:
                    raise Exception("Table not found")

        # ## 풋노트 끌어오기
        # for kNote in dictNote.keys():
        #     for k, v in dictSpec.items():
        #         if kNote in k:
        #             dictSpec[k] = k.replace(kNote, dictNote.get(kNote))
        #         if kNote in v:
        #             dictSpec[k] = v.replace(kNote, dictNote.get(kNote))

        spec_dict['url'] = url

        # print(spec_dict)
        # print(pd.DataFrame.from_dict(spec_dict,orient='index', columns=['Value']))
        # spec_dict = self._split_models(spec_dict)
        # for k in spec_dict.keys():
        #     spec_dict[k].update(self._extract_info(k))
        # print(spec_dict)
        return spec_dict

    def _extract_global_specs(self, text):
        if "【" in text:
            listText = text.split("【")
            listText = [text.split("】") for text in listText]
            dictText = OrderedDict((term[0].strip(), term[1].strip()) for term in listText if len(term) > 1)
            return dictText
        else:
            return text

    def _parse_model_name(self, text):
        footMarks = ["※" + str(i) for i in reversed(range(1, 30))]
        for footMark in footMarks:
            text = text.replace(footMark, "")
        return text
