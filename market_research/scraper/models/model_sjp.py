import time
from market_research.tools import WebDriver, FileManager

from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
from collections import OrderedDict
import pandas as pd
class ModelScraper_sjp:

    def __init__(self, webdriver_path: str, browser_path: str = None, enable_headless=True):
        self.wait_time = 10
        self.web_driver = WebDriver(executable_path=webdriver_path, browser_path=browser_path,
                                    headless=enable_headless)
        self.file_manager = FileManager
        self.tracking_log = enable_headless
    def get_models_info(self, foramt_output="df"):
        print("sony_jp")
        url_series_dict = self._get_spec_series()
        models_dict = {}
        for model, url in tqdm(url_series_dict.items()):
            print(f"{model}: {url}")
            modelspec = self._get_spec(url=url)
            models_dict.update(modelspec)
        print("Number of all Series:", len(models_dict))

        if foramt_output == "df":
            return pd.DataFrame.from_dict(models_dict).T
        else:
            return models_dict


    ###=====================get info main page====================================##
    def _get_spec_series(self, url: str = "https://www.sony.jp/bravia/gallery/") -> dict:
        """
        스크롤 다운이 되어야 전체 웹페이지가 로딩되어, 스크롤은 selenium, page parcing은 BS4로 진행
        """
        step: int = 200
        series_dict = {}
        trytotal = 3
        for trycnt in range(trytotal):
            driver = self.web_driver.get_chrome()
            driver.get(url=url)
            time.sleep(1)
            scroll_distance_total = self.web_driver.get_scroll_distance_total()
            scroll_distance = 0
            while scroll_distance < scroll_distance_total:
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                try:
                    button_containers = soup.find_all('div', class_='GalleryListItem__ButtonContainer')
                    for container in button_containers:
                        link = container.find('a')['href']
                        model = link.split("products/")[-1].split(".")[0].replace('/',"")
                        link = "https://www.sony.jp/bravia/products/" + model + "/spec.html"
                        series_dict[model]=link
                    # 한 step씩 스크롤 내리기
                    driver.execute_script(f"window.scrollBy(0, {step});")
                    time.sleep(1)  # 스크롤이 내려가는 동안 대기
                    scroll_distance += step
                except:
                    print(f"get_spec_series error, re-try {trycnt}/{trytotal}")
                    driver.quit()
            driver.quit()
            break
        print(f"number of total Series: {len(series_dict)}")
        return series_dict

    def _get_spec(self, url: str = "https://www.sony.jp/bravia/products/XRJ-A80J/spec.html") -> list:
        spec_dict = OrderedDict()

        dictNote = {}
        TotalCnt = 5

        #=============================
        for tryCnt in range(TotalCnt):
            step: int = 200
            driver = self.web_driver.get_chrome()
            driver.get(url=url)
            time.sleep(1)
            try:
                print("Trying with Selenium...")
                scroll_distance_total = self.web_driver.get_scroll_distance_total()
                scroll_distance = 0  # 현재까지 스크롤한 거리

                while scroll_distance < scroll_distance_total:
                    html = driver.page_source
                    soup = BeautifulSoup(html, 'html.parser')
                    table = soup.find('div', class_='s5-specTable')

                    # if table is not None:  # 테이블이 있는 경우에만 데이터 추출
                    for row in table.find_all('tr'):
                        cells = row.find_all('td')
                        if len(cells) >= 1:
                            key = row.get_text(strip=True)
                            value = cells[0].get_text(strip=True)
                            key = key.replace(value, "")

                            key = self._extract_foot(key)
                            value = self._extract_foot(value)
                            value = self._extract_product_info(value)
                            spec_dict[key] = value

                    # ## 노트 추출
                    # notes = soup.select('.s5-specTableNote li')
                    # for note in notes:
                    #     bullet = note.select_one('.s5-specTableNote__bullet').text.strip()
                    #     text = note.select_one('.s5-specTableNote__text').text.strip()
                    #     dictNote[bullet] = " @" + text
                    # 한 step씩 스크롤 내리기
                    driver.execute_script(f"window.scrollBy(0, {step});")
                    time.sleep(1)  # 스크롤이 내려가는 동안 대기
                    scroll_distance += step
                driver.quit()
                break  # 셀레니움으로 성공적으로 스크래핑했을 경우 반복문 탈출
            except Exception as e:
                driver.quit()
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
                            key = self._extract_foot(key)
                        if value_element and key:
                            value = value_element.get_text(strip=True)
                            value = self._extract_foot(value)
                            spec_dict[key] = self._extract_product_info(value)
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
        spec_dict = self._split_models(spec_dict)
        for k in spec_dict.keys():
            spec_dict[k].update(self._extract_info(k))
        # print(spec_dict)
        return spec_dict

    def _split_models(self, dictModels):
        dictNewModels = {}
        dictModelsSplited = dictModels.get('型')
        if isinstance(dictModelsSplited, dict):
            for model in dictModelsSplited.keys():
                dictNewModel = {}
                for k, v in dictModels.items():
                    try:
                        value = v.get(model)
                        dictNewModel[k] = value
                    except:
                        dictNewModel[k] = v
                dictNewModels[model] = dictNewModel
        elif isinstance(dictModelsSplited, str):
            url = dictModels.get('url')
            model = url.split("/products/")[1].split("/")[0]
            dictNewModels[model] = dictModels
        else:
            # Handle other cases if needed
            pass
        return dictNewModels


    def _extract_product_info(self, text):
        if "【" in text:
            listText = text.split("【")
            listText = [text.split("】") for text in listText]
            dictText = OrderedDict((term[0].strip(), term[1].strip()) for term in listText if len(term) > 1)
            return dictText
        else:
            return text



    def _extract_foot(self, text):
        footMarks = ["*" + str(i) for i in reversed(range(1, 30))]
        for footMark in footMarks:
            text = text.replace(footMark, "")
        return text

    def _extract_info(self, model):
        dictInfo = {}
        dictInfo["year"] = model.split("-")[1][-1]
        dictInfo["series"] = model.split("-")[1][2:]
        dictInfo["size"] = model.split("-")[1][:2]
        dictInfo["grade"] = model.split("-")[0]

        year_mapping = {
            "N": 2025,
            "M": 2024,
            'L': 2023,
            'K': 2022,
            'J': 2021,
            # 추가적인 알파벳과 연도 대응 관계를 추가할 수 있음
        }

        # 알파벳과 대응하는 연도가 없을 경우 기본값으로 설정할 연도를 지정
        try:
            dictInfo["year"] = year_mapping.get(dictInfo.get("year"))
        except:
            dictInfo["year"] = ""
        return dictInfo
