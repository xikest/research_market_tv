import time
from market_research.tools import WebDriver
from bs4 import BeautifulSoup
from tqdm import tqdm
from collections import OrderedDict
import pandas as pd
class ModelScraper_pjp:

    def __init__(self, webdriver_path: str, browser_path: str = None, enable_headless=True):
        self.wait_time = 1
        self.web_driver = WebDriver(executable_path=webdriver_path, browser_path=browser_path,
                                    headless=enable_headless)
        self.tracking_log = enable_headless


    def get_models_info(self, foramt_output="df"):
        print("panasonic")
        setUrlSeries = self._get_spec_series()
        ## 웹페이지의 모든 모델 url을 추출
        dictModels = OrderedDict()
        for model, url in tqdm(setUrlSeries.items()):
            print(model,":", url)
            modelspec = self._get_spec_global(url=url)
            modelspec["url"] = url
            dictModels[model] = modelspec
        print("Number of all Series:", len(dictModels))

        if foramt_output == "df":
            return pd.DataFrame.from_dict(dictModels).T
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
        print(f"number of total Series: {len(series_dict)}")
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