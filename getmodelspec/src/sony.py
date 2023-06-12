
from bs4 import BeautifulSoup
from datetime import date
import requests
from tqdm import tqdm
import traceback
from collections import OrderedDict

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from getmodelspec.src.tv_spepcifications import Specifications
from getmodelspec.src.tv_score import Score
from getmodelspec.tools.functions import *
from getmodelspec.tools.webdriver import WebDriver



class GetSONY:
    def __init__(self, fastMode=True, srcfromGlobal=True, toExcel=True):
        self.waitTime = 10
        self.fastMode = fastMode
        self.srcfromGlobal = srcfromGlobal
        self.toExcel = toExcel
        self.dir_3rd = "sony/log/models"
        makeDir(self.dir_3rd)
        pass

    def getModels(self, toExcel:bool = True) -> dict:
        # 메인 페이지에서 시리즈를 추출
        setUrlSeries = self.__getUrlSeries__()
        print(setUrlSeries)
        # ==========================================================================
        # backUp(setUrlSeries, "setUrlSeries")
        # with open(f"setUrlSeries.pickle", "rb") as file:
        #     setUrlSeries = pickle.load(file)
        # # ==========================================================================

        ## 웹페이지의 모든 모델 url을 추출
        dictUrlSeries = {}
        for url in setUrlSeries:
            urlModels = self.__getModels__(url=url)
            print(urlModels)
            dictUrlSeries.update(urlModels)
        print("Number of all Series:", len(dictUrlSeries))

        # # # ==========================================================================
        # backUp(dictUrlSeries, "dictUrlSeries")
        # with open(f"dictUrlSeries.pickle", "rb") as file:
        #     dictUrlSeries = pickle.load(file)
        # ==========================================================================
    #     # 모델 정보 추출, 모델명/url/가격
        dictModels = {}
        score = Score()
        for key, urlModel in tqdm(dictUrlSeries.items()):
            try:
                dictInfo = self.__getModelInfo__(urlModel)
                time.sleep(1)
                dictModels[key] = dictInfo
                model = dictInfo.get('model')

                if self.fastMode == False:
                    if self.srcfromGlobal == True:
                        dictSpec = self.__getSpecGlobal__(url=urlModel)
                        dictModels[key].update(dictSpec)
                    else:
                        print("global")
                        dictSpec = self.__getSpec__(maker="sony", model=model)
                        dictModels[key].update(dictSpec)

                time.sleep(1)
                series = model.split("-")[1][2:]
                dictScore = score.getRthinsScore(maker="sony", series=series)
                print(series,"score:", dictScore)
                dictModels[key].update(dictScore)
            except Exception as e:
                print(f"fail to get info from {key}")
                print(e)
                pass

    # ======export====================================================================
        if self.toExcel == True:
            fileName = f"sony_LineUpGlobal_{date.today().strftime('%Y-%m-%d')}"
            dictToexcel(dictModels, fileName=fileName,sheetName="Global")  # 엑셀 파일로 저장

        return dictModels

    ###=====================get info main page====================================##
    def __getUrlSeries__(self)-> set:
        """
        스크롤 다운이 되어야 전체 웹페이지가 로딩되어, 스크롤은 selenium, page parcing은 BS4로 진행
        """
        url: str = "https://electronics.sony.com/tv-video/televisions/c/all-tvs/"
        prefix:str = "https://electronics.sony.com/"
        step: int = 200
        setUrlSeries=set()

        wd = WebDriver.getChrome()
        wd.get(url=url)
        time.sleep(1)

        scrollDistanceTotal = WebDriver.getScrollDistanceTotal(wd)
        scrollDistance = 0  # 현재까지 스크롤한 거리

        while scrollDistance < scrollDistanceTotal:
            html = wd.page_source
            soup = BeautifulSoup(html, 'html.parser')

            elements = soup.find_all('a', class_="custom-product-grid-item__product-name")
            for element in elements:
                urlSeries = prefix + element['href']
                # label = element.text
                # print(f"{label} {urlSeries}")
                setUrlSeries.add(urlSeries.strip())

            # 한 step씩 스크롤 내리기
            wd.execute_script(f"window.scrollBy(0, {step});")
            time.sleep(1)  # 스크롤이 내려가는 동안 대기
            scrollDistance += step

        wd.quit()
        print(f"number of total Series: {len(setUrlSeries)}")
        return setUrlSeries

    def __getModels__(self, url: str,
                      prefix="https://electronics.sony.com/",
                      modeStatic=True) -> dict:
        cntTryTotal = 5
        for cntTry in range(cntTryTotal):
            try:
                dictUrlModels = {}
                if modeStatic == True:
                    response = requests.get(url)
                    # print("connect to", url)
                    # time.sleep(1)
                    page_content = response.text

                    soup = BeautifulSoup(page_content, 'html.parser')
                    elements = soup.find_all('a', class_='custom-variant-selector__item')
                else:
                    wd = WebDriver.getChrome()
                    wd.get(url=url)
                    # print("connect to", url)
                    waitingPage(self.waitTime)
                    page_source = wd.page_source
                    soup = BeautifulSoup(page_source, 'html.parser')
                    elements = soup.find_all('a', class_='custom-variant-selector__item')

                for element in elements:
                    try:
                        element_url = prefix + element['href']
                        label = getNamefromURL(element_url)
                        # print(f"{label} {element_url}")

                        dictUrlModels[label] = element_url.strip()
                    except Exception as e:
                        print(f"getSeries error ({e})")
                        pass

                    # waitingPage(self.waitTime)
                print(f"Number of SONY {getNamefromURL(url)[4:]} series:", len(dictUrlModels))
                return dictUrlModels
            except Exception as e:
                print(f"__getModels__ try: {cntTry}/{cntTryTotal}")

    ###====================================================================================##
    def __getModelInfo__(self,url: str) -> dict:
        response = requests.get(url)
        print("connect to", url)
        page_content = response.text
        soup = BeautifulSoup(page_content, 'html.parser')
        dictInfo = {}
        label = soup.find('h2', class_='product-intro__code').text.strip()
        dictInfo["model"] = label.split()[-1]
        dictInfo["price"] = soup.find('div', class_='custom-product-summary__price').text.strip()
        dictInfo.update(self.__extractInfo__(dictInfo.get("model")))
        dictInfo["descr"] = soup.find('h1', class_='product-intro__title').text.strip()
        return dictInfo

    ###======================get spec===============================##
    def __getSpec__(self, maker:str ='sony', model='XR-65A80L') -> dict:
        specs = Specifications()
        dictSpec = specs.getSpec(maker=maker, model=model)
        return dictSpec

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

                wd.save_screenshot(f"./{dir_model}/{getNamefromURL(url)}_0_model_{get_today()}.png")  # 스크린 샷

                elementSpec = wd.find_element(By.ID, "PDPSpecificationsLink")
                wd = WebDriver.move_element_to_center(wd, elementSpec)
                wd.save_screenshot(f"./{dir_model}/{getNamefromURL(url)}_1_move_to_spec_{get_today()}.png")  # 스크린 샷

                waitingPage(self.waitTime)  # 페이지 로딩 대기 -
                elementClickSpec = wd.find_element(By.ID, 'PDPSpecificationsLink')
                elementClickSpec.click()
                waitingPage(self.waitTime)  # 페이지 로딩 대기 -
                wd.save_screenshot(
                    f"./{dir_model}/{getNamefromURL(url)}_2_after_click_specification_{get_today()}.png")  # 스크린 샷

                try:
                    element_seeMore = wd.find_element(By.XPATH,
                                                      '//*[@id="PDPOveriewLink"]/div[1]/div/div/div[2]/div/app-product-specification/div/div[2]/div[3]/button')
                    wd = WebDriver.move_element_to_center(wd, element_seeMore)
                    wd.save_screenshot(
                        f"./{dir_model}/{getNamefromURL(url)}_3_after_click_see_more_{get_today()}.png")  # 스크린 샷
                    element_seeMore.click()
                except:
                    element_seeMore = wd.find_element(By.XPATH,
                                                      '//*[@id="PDPOveriewLink"]/div[1]/div/div/div[2]/div/app-product-specification/div/div[2]/div[2]/button')
                    wd = WebDriver.move_element_to_center(wd, element_seeMore)
                    wd.save_screenshot(
                        f"./{dir_model}/{getNamefromURL(url)}_3_after_click_see_more_{get_today()}.png")  # 스크린 샷
                    element_seeMore.click()

                # 스펙 팝업 창의 스크롤 선택 후 클릭: 팝업 창으로 이동
                time.sleep(self.waitTime)  # 페이지 로딩 대기 -
                wd.find_element(By.ID, "ngb-nav-0-panel").click()
                # 스펙 팝업 창의 스펙 가져오기
                for cnt in range(15):
                    elements = wd.find_elements(By.CLASS_NAME,
                                                "full-specifications__specifications-single-card__sub-list")
                    for element in elements:
                        soup = BeautifulSoup(element.get_attribute("innerHTML"), 'html.parser')
                        dictSpec.update(self.__soupToDict__(soup))
                    ActionChains(wd).key_down(Keys.PAGE_DOWN).perform()
                wd.save_screenshot(f"./{dir_model}/{getNamefromURL(url)}_4_end_{get_today()}.png")  # 스크린 샷

                wd.quit()
                print(f"{model}\n", dictSpec)
                return dictSpec

            except Exception as e:
                print(f"getPage3rd error: {model} try {cntTry + 1}/{cntTryTotal}")
                with open("official spec error_log.txt", "a") as file:
                    traceback.print_exc(file=file)  # Traceback 정보를 파일에 저장
                wd.quit()
                pass

    ###===================help func============================##
    def __extractInfo__(self, model):
        dictInfo = {}
        dictInfo["year"] = model.split("-")[1][-1]
        dictInfo["series"] = model.split("-")[1][2:-1]
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
        try: dictInfo["year"] = year_mapping.get(dictInfo.get("year"))
        except:year = ""
        return dictInfo

    def __soupToDict__(self,soup):
        try:
            h4_tag = soup.find('h4').text.strip()
            p_tag = soup.find('p').text.strip()
        except Exception as e:
            print("parser err", e)
            h4_tag = soup.find('h4').text.strip()
            p_tag =  ""
            pass
        return {h4_tag: p_tag}

class GetSONYjp:
    def __init__(self, fastMode=True,  toExcel=True):
        self.waitTime = 10
        self.fastMode = fastMode
        self.toExcel = toExcel
        pass

    def getModels(self, toExcel:bool = True) -> dict:
        self.toExcel=toExcel
        # 메인 페이지에서 시리즈를 추출
        setUrlSeries = self.__getSpecSeries__()
        print(setUrlSeries)
        # ==========================================================================
        # backUp(setUrlSeries, "setUrlSeries")
        # with open(f"setUrlSeries.pickle", "rb") as file:
        #     setUrlSeries = pickle.load(file)
        # ==========================================================================

        ## 웹페이지의 모든 모델 url을 추출
        dictModels = {}
        for model, url in tqdm(setUrlSeries.items()):
            print(model,":", url)
            modelspec = self.__getSpec__(url=url)
            dictModels.update(modelspec)
            # backUp(dictModels, "dictModels_b")
        print("Number of all Series:", len(dictModels))
        print(dictModels)
        # backUp(dictModels, "dictModels")
    # ======export====================================================================
        if self.toExcel == True:
            fileName = f"sonyJp_LineUp_{date.today().strftime('%Y-%m-%d')}"
            dictToexcel(dictModels, fileName=fileName,sheetName="Jp")  # 엑셀 파일로 저장

        return dictModels


    ###=====================get info main page====================================##
    def __getSpecSeries__(self, url: str = "https://www.sony.jp/bravia/gallery/") -> dict:
        """
        스크롤 다운이 되어야 전체 웹페이지가 로딩되어, 스크롤은 selenium, page parcing은 BS4로 진행
        """
        step: int = 200
        dictSeries = {}

        wd = WebDriver.getChrome()
        wd.get(url=url)
        time.sleep(1)

        scrollDistanceTotal = WebDriver.getScrollDistanceTotal(wd)
        scrollDistance = 0  # 현재까지 스크롤한 거리

        while scrollDistance < scrollDistanceTotal:
            html = wd.page_source
            soup = BeautifulSoup(html, 'html.parser')
            button_containers = soup.find_all('div', class_='GalleryListItem__ButtonContainer')
            for container in button_containers:
                link = container.find('a')['href']
                model = link.split("products/")[-1].split(".")[0].replace('/',"")
                link = "https://www.sony.jp/bravia/products/" + model + "/spec.html"
                dictSeries[model]=link


            # 한 step씩 스크롤 내리기
            wd.execute_script(f"window.scrollBy(0, {step});")
            time.sleep(1)  # 스크롤이 내려가는 동안 대기
            scrollDistance += step

        wd.quit()
        print(f"number of total Series: {len(dictSeries)}")
        return dictSeries

    def __getSpec__(self, url:str="https://www.sony.jp/bravia/products/XRJ-A80J/spec.html") -> list:

        dictSpec = OrderedDict()
        dictNote = {}

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
                    key = self.__extractFoot__(key)
                if value_element and key:
                    value = value_element.get_text(strip=True)
                    value = self.__extractFoot__(value)
                    dictSpec[key] = self.__extractProductInfo__(value)
        else:
            step: int = 200
            wd = WebDriver.getChrome()
            wd.get(url=url)
            time.sleep(1)

            scrollDistanceTotal = WebDriver.getScrollDistanceTotal(wd)
            scrollDistance = 0  # 현재까지 스크롤한 거리
            try:
                while scrollDistance < scrollDistanceTotal:
                    html = wd.page_source
                    soup = BeautifulSoup(html, 'html.parser')
                    table = soup.find('div', class_='s5-specTable')

                    # if table is not None:  # 테이블이 있는 경우에만 데이터 추출
                    for row in table.find_all('tr'):
                        cells = row.find_all('td')
                        if len(cells) >= 1:
                            key = row.get_text(strip=True)
                            value = cells[0].get_text(strip=True)
                            key = key.replace(value, "")

                            key = self.__extractFoot__(key)
                            value = self.__extractFoot__(value)
                            value = self.__extractProductInfo__(value)
                            dictSpec[key] = value

                    # ## 노트 추출
                    # notes = soup.select('.s5-specTableNote li')
                    # for note in notes:
                    #     bullet = note.select_one('.s5-specTableNote__bullet').text.strip()
                    #     text = note.select_one('.s5-specTableNote__text').text.strip()
                    #     dictNote[bullet] = " @" + text
                    # 한 step씩 스크롤 내리기
                    wd.execute_script(f"window.scrollBy(0, {step});")
                    time.sleep(1)  # 스크롤이 내려가는 동안 대기
                    scrollDistance += step
                wd.quit()
            except Exception as e:
                print("An error occurred:", e)
                # 웹페이지가 동적이 아닌 경우
                wd.quit()

        # ## 풋노트 끌어오기
        # for kNote in dictNote.keys():
        #     for k, v in dictSpec.items():
        #         if kNote in k:
        #             dictSpec[k] = k.replace(kNote, dictNote.get(kNote))
        #         if kNote in v:
        #             dictSpec[k] = v.replace(kNote, dictNote.get(kNote))
        dictSpec['url'] = url
        dictSpec = self.__splitModels__(dictSpec)
        for k in dictSpec.keys(): dictSpec[k].update(self.__extractInfo__(k))

        return dictSpec

    def __splitModels__(self, dictModels):
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

    # def __splitModels__(self, dictModels):
    #     dictNewModels = {}
    #     dictNewModel = {}
    #
    #     dictModelsSplited = dictModels.get('型')
    #     if isinstance(dictModelsSplited, dict):
    #         for model in dictModelsSplited.keys():
    #             for k, v in dictModels.items():
    #                 try:
    #                     # print(k, v.get(model))
    #                     dictNewModel[k] = v.get(model)
    #                 except:
    #                     dictNewModel[k] = v
    #             dictNewModels[model] = dictNewModel
    #     else:
    #         # 수정 해야 함 딕셔너리가 아닐 경우?
    #         url = dictModels.get('url')
    #         model = url.split("/products/")[1].split("/")[0]
    #         dictNewModels[model] = dictModels
    #     return dictNewModels


    def __extractProductInfo__(self, text):
        if "【" in text:
            listText = text.split("【")
            listText = [text.split("】") for text in listText]
            dictText = OrderedDict((term[0].strip(), term[1].strip()) for term in listText if len(term) > 1)
            return dictText
        else:
            return text



    def __extractFoot__(self, text):
        footMarks = ["*" + str(i) for i in reversed(range(1, 30))]
        for footMark in footMarks:
            text = text.replace(footMark, "")
        return text

    def __extractInfo__(self, model):
        dictInfo = {}
        dictInfo["year"] = model.split("-")[1][-1]
        dictInfo["series"] = model.split("-")[1][2:-1]
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
        try: dictInfo["year"] = year_mapping.get(dictInfo.get("year"))
        except:year = ""
        return dictInfo
