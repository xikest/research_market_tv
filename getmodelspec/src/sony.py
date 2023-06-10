
import pandas as pd
from bs4 import BeautifulSoup
from datetime import date
import requests
from tqdm import tqdm
import traceback

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from ..tools.functions import *
from ..tools.WebDriver import WebDriver
from ..src.tv_spepcifications import Specifications
from ..src.tv_score import Score

class GetSONY:
    def __init__(self, fastMode=True, srcfromOfficial=True, toExcel=True):
        self.waitTime = 10
        self.fastMode = fastMode
        self.srcfromOfficial = srcfromOfficial
        self.toExcel = toExcel
        self.dir_3rd = "sony/log/models"
        makeDir(self.dir_3rd)
        pass

    def getModels(self, toExcel:bool = True) -> pd.DataFrame:
        # 메인 페이지에서 시리즈를 추출
        setUrlSeries = self.__getSeriesModeHybrid__(url= 'https://electronics.sony.com/tv-video/televisions/c/all-tvs')
        # print(urlStream)
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

        # # ==========================================================================
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
                print(dictInfo)
                dictModels[key] = dictInfo
                model = dictInfo.get('model')

                if self.fastMode == False:
                    if self.srcfromOfficial == True:
                        dictSpec = self.__getSpecOfficial__(url=urlModel)
                        dictModels[key].update(dictSpec)
                    else:
                        dictSpec = self.__getSpec__(maker="sony", model=model)
                        dictModels[key].update(dictSpec)

                time.sleep(1)
                # print(dictSpec)
                series = model.split("-")[1][2:]
                dictScore = score.getRthinsScore(maker="sony", series=series)
                dictModels[key].update(dictScore)

                # print(dictModels)
                # latest_key = list(dictModels.keys())[-1]
                # print(dictModels.get(latest_key))
            except Exception as e:
                print(f"fail to get info from {key}")
                print(e)
                pass

    # ======export====================================================================
        dfModels = pd.DataFrame.from_dict(dictModels, orient="index")
        # dfModels = dfModels.rename_axis('model').reset_index()


        if self.toExcel == True:
            fileName = f"sony_TV_series_{date.today().strftime('%Y-%m-%d')}.xlsx"
            dfModels.to_excel(fileName, index=False)  # 엑셀 파일로 저장

        return dfModels

    ###=====================get info main page====================================##
    def __getSeriesModeHybrid__(self, url:str="https://electronics.sony.com/tv-video/televisions/c/all-tvs/",
                      className:str='custom-product-grid-item__product-name',
                      prefix = "https://electronics.sony.com/") -> set:
        """
        스크롤 다운이 되어야 전체 웹페이지가 로딩되어, 스크롤은 selenium, page parcing은 BS4로 진행
        """

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

            elements = soup.find_all('a', class_=className)
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
                print(f"stage 2nd try: {cntTry}/{cntTryTotal}")

    def __getModelsModeDynamic__(self, url: str,
                      prefix = "https://electronics.sony.com/") -> dict:
        cntTryTotal = 5
        for cntTry in range(cntTryTotal):
            try:
                dictUrlModels = {}
                wd = WebDriver.getChrome()
                wd.get(url=url)
                print("connect to", url)

                waitingPage(self.waitTime)

                page_source = wd.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                elements = soup.find_all('a', class_='custom-variant-selector__item')

                for element in elements:
                    try:
                        element_url = prefix + element['href']
                        label = getNamefromURL(element_url)

                        dictUrlModels[label] = element_url.strip()
                    except Exception as e:
                        print(f"getPage2nd error ({e})")
                        pass
                wd.save_screenshot(f"./{self.dir_2nd}/{getNamefromURL(url)}_Sub_Series_{get_today()}.png")
                wd.quit()
                if len(dictUrlModels) == 0:
                    raise Exception

                waitingPage(self.waitTime)
                print(f"Number of SONY {getNamefromURL(url)[4:]} series:", len(dictUrlModels))
                return dictUrlModels
            except Exception as e:
                wd.quit()
                waitingPage(self.waitTime)
                print(f"stage 2nd try: {cntTry}/{cntTryTotal}")

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

    ###======================final stage===============================##
    def __getSpec__(self, maker:str ='sony', model='XR-65A80L') -> dict:
        specs = Specifications()
        dictSpec = specs.getSpec(maker=maker, model=model)
        return dictSpec

    ###======================final stage===============================##
    def __getSpecOfficial__(self, url: str) -> dict:

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
                        dictSpec.update(soupToDict(soup))
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

    def __getData4th__(self, dfModels):
        new_columns = dfModels['model'].apply(self.__extractInfo__)
        df_combined = pd.concat([new_columns, dfModels], axis=1).set_index('model')
        return df_combined


# ===============================

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


def soupToDict(soup):
    try:
        h4_tag = soup.find('h4').text.strip()
        p_tag = soup.find('p').text.strip()
    except Exception as e:
        print("parser err", e)
        h4_tag = soup.find('h4').text.strip()
        p_tag =  ""
        pass
    return {h4_tag: p_tag}


