
from bs4 import BeautifulSoup
from datetime import date
from tqdm import tqdm
import traceback
from collections import OrderedDict

from getmodelspec.src.tv_spepcifications import Specifications
from getmodelspec.src.tv_score import Score
from getmodelspec.tools.functions import *
from getmodelspec.tools.webdriver import WebDriver

class GetPanajp:
    def __init__(self,  toExcel=True):
        self.waitTime = 10
        self.toExcel = toExcel
        self.maker= "pana"
        self.dir_3rd = f"{self.maker}/log/models"
        pass

    def getModels(self, toExcel:bool = True) -> dict:
        self.toExcel=toExcel
        # 메인 페이지에서 시리즈를 추출
        # setUrlSeries = self.__getSpecSeries__()
        # print(setUrlSeries)
        # # ==========================================================================
        # # backUp(setUrlSeries, "setUrlSeries")
        with open(f"setUrlSeries.pickle", "rb") as file:
            setUrlSeries = pickle.load(file)
        # ==========================================================================

        ## 웹페이지의 모든 모델 url을 추출
        dictModels = OrderedDict()
        for model, url in tqdm(setUrlSeries.items()):
            print(model,":", url)
            modelspec = self.__getSpecGlobal__(url=url)
            dictModels[model]=modelspec

            print(dictModels.keys())
            print({model:modelspec})
            # print(dictModels)
            # backUp(dictModels, "dictModels_b")
        print("Number of all Series:", len(dictModels))
        # print(dictModels)
        backUp(dictModels, "dictModels")

        with open(f"dictModels.pickle", "rb") as file:
            dictModels = pickle.load(file)
    # ======export====================================================================
        if self.toExcel == True:
            fileName = f"{self.maker}Jp_LineUp_{date.today().strftime('%Y-%m-%d')}"
            dictToexcel(dictModels, fileName=fileName,sheetName="Jp")  # 엑셀 파일로 저장

        return dictModels

    ###=====================get info main page====================================##
    def __getSpecSeries__(self, url: str = "https://www.panasonic.com/uk/consumer/televisions/4K-OLED-TV.html") -> dict:

        step: int = 200
        dictSeries = OrderedDict()

        wd = WebDriver.getChrome()
        wd.get(url=url)
        time.sleep(1)

        scrollDistanceTotal = WebDriver.getScrollDistanceTotal(wd)
        scrollDistance = 0  # 현재까지 스크롤한 거리

        while scrollDistance < scrollDistanceTotal:
            html = wd.page_source
            dictSeries.update(self.__getSpecSeriesExtact__(html))

            # 한 step씩 스크롤 내리기
            wd.execute_script(f"window.scrollBy(0, {step});")
            time.sleep(1)  # 스크롤이 내려가는 동안 대기
            scrollDistance += step

        wd.quit()

        print(f"number of total Series: {len(dictSeries)}")
        print(dictSeries)
    def __getSpecSeriesExtact__(self, html) -> dict:
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

    def __getSpecGlobal__(self, url: str) -> dict:
        print("get", url)
        cntTryTotal = 20
        for cntTry in range(cntTryTotal):
            try:
                dictSpec = {}
                wd = WebDriver.getChrome()
                wd.get(url=url)
                model = getNamefromURL(url)
                dir_model = f"{self.dir_3rd}/{model}"
                makeDir(dir_model)
                # wd.save_screenshot(f"./{dir_model}/{getNamefromURL(url)}_0_model_{get_today()}.png")  # 스크린 샷

                # Selenium을 사용하여 페이지 소스 가져오기
                dictSpec = OrderedDict()
                page_source = wd.page_source

                # BeautifulSoup를 사용하여 페이지 소스 파싱
                soup = BeautifulSoup(page_source, 'html.parser')
                classNames = ["speclist__item lv2", "speclist__item lv1"]

                for className in classNames:
                    dictSpec.update(self.__extractDataFromPage__(soup, className=className))
                return dictSpec

            except Exception as e:
                print(f"getPage3rd error: {model} try {cntTry + 1}/{cntTryTotal}")
                with open("official spec error_log.txt", "a") as file:
                    traceback.print_exc(file=file)  # Traceback 정보를 파일에 저장
                wd.quit()
                pass

    def __extractDataFromPage__(self, soup, className='speclist__item lv2'):
        # <li class="speclist__item lv2"> 요소 찾기
        items = soup.find_all('li', class_=className)

        # 딕셔너리 초기화
        result_dict = {}

        # 각 <li class="speclist__item lv2"> 객체에서 정보 추출
        for item in items:
            key_element = item.find('div', class_='speclist__item__ttl')
            value_element = item.find('ul', class_='speclist')

            if key_element and value_element:
                key = key_element.text.strip()
                value = value_element.text.strip()
                result_dict[key] = value

        return result_dict

    #
    #
    # def __extractProductInfo__(self, text):
    #     if "【" in text:
    #         listText = text.split("【")
    #         listText = [text.split("】") for text in listText]
    #         dictText = OrderedDict((term[0].strip(), term[1].strip()) for term in listText if len(term) > 1)
    #         return dictText
    #     else:
    #         return text
    #
    #
    #
    # def __extractFoot__(self, text):
    #     footMarks = ["*" + str(i) for i in reversed(range(1, 30))]
    #     for footMark in footMarks:
    #         text = text.replace(footMark, "")
    #     return text
    #
    # def __extractInfo__(self, model):
    #     dictInfo = {}
    #     dictInfo["year"] = model.split("-")[1][-1]
    #     dictInfo["series"] = model.split("-")[1][2:]
    #     dictInfo["size"] = model.split("-")[1][:2]
    #     dictInfo["grade"] = model.split("-")[0]
    #
    #     year_mapping = {
    #         "N": 2025,
    #         "M": 2024,
    #         'L': 2023,
    #         'K': 2022,
    #         'J': 2021,
    #         # 추가적인 알파벳과 연도 대응 관계를 추가할 수 있음
    #     }
    #
    #     # 알파벳과 대응하는 연도가 없을 경우 기본값으로 설정할 연도를 지정
    #     try:
    #         dictInfo["year"] = year_mapping.get(dictInfo.get("year"))
    #     except:
    #         dictInfo["year"] = ""
    #     return dictInfo
