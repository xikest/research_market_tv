import time
from bs4 import BeautifulSoup
from tqdm import tqdm
from collections import OrderedDict
import pandas as pd
from tools.file import FileManager
from market_research.scraper._scraper_scheme import Scraper, Modeler, CustomException
from market_research.scraper.models.visualizer.data_visualizer import DataVisualizer

class ModelScraper_p(Scraper, Modeler, DataVisualizer):

    def __init__(self, enable_headless=True,
                 export_prefix="pana_model_info_web", intput_folder_path="input", output_folder_path="results",
                 verbose: bool = False, wait_time=1):
        super().__init__(enable_headless=enable_headless, export_prefix=export_prefix,
                         intput_folder_path=intput_folder_path, output_folder_path=output_folder_path)
        self.tracking_log = verbose
        self.wait_time = wait_time


    def get_models_info(self, format_df: bool = True, show_visit:bool=False):
        print("collecting models")
        setUrlSeries = self._get_spec_series()
        ## 웹페이지의 모든 모델 url을 추출
        print("collecting spec")
        visit_url_dict = {}
        dictModels = OrderedDict()
        cnt_loop=2
        for cnt in range(cnt_loop):#main try
            for model, url in tqdm(setUrlSeries.items()):
                try:
                    # print(model,":", url)
                    modelspec = self._get_spec_global(url=url)
                    modelspec["url"] = url
                    dictModels[model] = modelspec

                    visit_url_dict[model] = url
                except Exception as e:
                    if cnt == cnt_loop - 1 :
                        print(f"\nFailed to get info from {model}")
                        print(e)
                    pass
            break
        if show_visit:
            print("\n")
            for model, url in visit_url_dict.items():  print(f"{model}: {url}")
            # print("Number of all Series:", len(dictModels))

        if format_df:
            df_models = pd.DataFrame.from_dict(dictModels).T
            FileManager.df_to_excel(df_models.reset_index(), file_name=self.output_xlsx_name, sheet_name="raw_na", mode='w')
            return df_models
        else:
            return dictModels

    ###=====================get info main page====================================##
    def _get_spec_series(self, url: str = "https://www.panasonic.com/uk/consumer/televisions/4K-OLED-TV.html") -> dict:
        step: int = 200
        series_dict = OrderedDict()
        driver = self.web_driver.get_chrome()
        driver.get(url=url)
        time.sleep(self.wait_time)
        scroll_distance_total = self.web_driver.get_scroll_distance_total()
        scroll_distance = 0  # 현재까지 스크롤한 거리

        while scroll_distance < scroll_distance_total:
            html = driver.page_source
            series_dict.update(self._get_spec_series_extact(html))
            # 한 step씩 스크롤 내리기
            driver.execute_script(f"window.scrollBy(0, {step});")
            time.sleep(self.wait_time)  # 스크롤이 내려가는 동안 대기
            scroll_distance += step
        driver.quit()
        # print(f"number of total Series: {len(series_dict)}")
        return series_dict


    def _get_spec_series_extact(self, html) -> dict:
        soup = BeautifulSoup(html, 'html.parser')
        results = {}
        prefix = "https://www.panasonic.com"
        items = soup.find_all('div', class_='categorybrowse-results-items__col')
        for item in items:
            link = item.find('a', class_='linkarea')
            title = item.find('div', class_='common-productbox-product__title')
            if link and title:
                link_url = link['href']
                title_text = title.text.strip()
                results[title_text] = prefix + link_url
        return results

    def _get_spec_global(self, url: str) -> dict:
        cntTryTotal = 20
        driver = None
        for cntTry in range(cntTryTotal):
            model = url.rsplit('/', 1)[-1]

            try:
                driver = self.web_driver.get_chrome()
                driver.get(url=url)
                # Selenium을 사용하여 페이지 소스 가져오기
                page_source = driver.page_source
                # BeautifulSoup를 사용하여 페이지 소스 파싱
                soup = BeautifulSoup(page_source, 'html.parser')
                dictSpec = self._extract_data_from_page(soup)
                return dictSpec

            except Exception as e:
                if self.tracking_log:
                    print(f"getPage3rd error: {model} try {cntTry + 1}/{cntTryTotal}")
                    print(e)
                driver.quit()
                pass

    def _extract_data_from_page(self, soup):
        # <li class="speclist__item lv2"> 요소 찾기
        # items = soup.find_all('li', class_=className)

        # 딕셔너리 초기화
        result_dict = {}
        hierarchy = self._extract_hierarchy(soup, [['speclist__item lv1'], ['speclist__item lv2'], ['speclist__item lv3'],['speclist__item lv4']])
        return hierarchy

    def _extract_hierarchy(self, element, classNames=['speclist__item lv1'], cnt=0):
        hierarchy = {}
        lv1_elements = element.find_all('li', class_=classNames[cnt])  # 최상위
        cnt += 1
        for lv1_element in lv1_elements:
            key_element = lv1_element.find('div', class_='speclist__item__ttl')
            if key_element is not None:
                key = key_element.get_text(strip=True)
                try:
                    lv2_element = lv1_element.find('ul', class_='speclist__item')
                    hierarchy[key] = self._extract_hierarchy(lv2_element, classNames=classNames, cnt=cnt)
                except:
                    data_element = lv1_element.find('div', class_='speclist__item__data')
                    hierarchy[key] = data_element.get_text(strip=True)

            siblings = lv1_element.find_next_siblings(['ul', 'li'], class_=['speclist__item', classNames[cnt]])
            for sibling in siblings:
                sibling_key_element = sibling.find('div', class_='speclist__item__ttl')
                if sibling_key_element is not None:
                    sibling_key = sibling_key_element.get_text(strip=True)
                    try:
                        sibling_lv2_element = sibling.find('ul', class_='speclist__item')
                        hierarchy[sibling_key] = self._extract_hierarchy(sibling_lv2_element, classNames=classNames,
                                                                           cnt=cnt)
                    except:
                        sibling_data_element = sibling.find('div', class_='speclist__item__data')
                        hierarchy[sibling_key] = sibling_data_element.get_text(strip=True)
        return hierarchy