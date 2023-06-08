
import pandas as pd
from bs4 import BeautifulSoup
from datetime import date

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

from ..tools.functions import *
from ..tools.webdriver import WebDriver
from ..src.tv_spepcifications import Sepcifications
from ..src.tv_score import Score

## 가격 정보만 찾기


class GetSONY:
    def __init__(self, envr:str=None):
        self.weakCon = 'weak'
        self.waitTime = 5

        self.envr = envr
        self.dir_1st = "sony/log/Stream"
        self.dir_2nd = "sony/log/Series"
        self.dir_3rd = "sony/log/models"
        makeDir(self.dir_1st)
        makeDir(self.dir_2nd)
        makeDir(self.dir_3rd)
        pass

    # #
    def getModels(self, toExcel:bool = True) -> pd.DataFrame:

        # 메인 페이지에서 시리즈를 추출
        seriesUrls = self.__getStream__(url= 'https://electronics.sony.com/tv-video/televisions/c/all-tvs')

        # ==========================================================================
        backUp(seriesUrls, "seriesUrls")
        # ==========================================================================

        ## 서브 시리즈 페이지에서 모델을 추출
        dictAllSeries = {}
        for url in seriesUrls:
            dictSeries = self.__getSeries__(url=url)
            print(dictSeries)
            dictAllSeries.update(dictSeries)
        print("Number of all Series:", len(dictAllSeries))

        # ==========================================================================
        backUp(dictAllSeries, "dictAllSeries")
        # with open(f"dictAllSeries.pickle", "rb") as file:
        #     dictAllSeries = pickle.load(file)
        # ==========================================================================

        # 모든 모델 리스트를 추출
        dictModels = {}
        for cnt, model in enumerate(dictAllSeries.keys()):
            print(f"{cnt+1}/{len(dictAllSeries)} | {model}")
            try:
                dictModels.update({model:self.__getSpec__(model)})

            except:
                print(f"fail to get info from {model}")

                dictModels.update({model:self.__getSpec__(model)})
                pass

        dfModels = pd.DataFrame.from_dict(dictModels, orient="index")
        dfModels = dfModels.rename_axis('model').reset_index()

        if toExcel == True:
            fileName = f"sony_TV_series_{date.today().strftime('%Y-%m-%d')}.xlsx"
            dfModels.to_excel(fileName, index=False)  # 엑셀 파일로 저장
    #


        dfModels = self.__getData4th__(dfModels)


        return dfModels

    ###=====================get info main page====================================##
    def __getStream__(self, url:str) -> set:
        set_mainSeries = set()
        scrolling_cnt: int = 10

        wd =  WebDriver.get_crome()
        wd.get(url=url)
        wait = WebDriverWait(wd, 30)

        for cnt in range(scrolling_cnt):
            try:
                # wd = closeModalCookie(wd)  # 쿠키 모달창 닫기
                waitingPage(self.waitTime)
                elements = wait.until(
                    EC.visibility_of_all_elements_located((By.CLASS_NAME, 'custom-product-grid-item__product-name')))
                for element in elements:
                    try:
                        set_mainSeries.add(element.get_attribute('href'))  # URL만 저장
                    except Exception as e:
                        print(f"getPage1st error ({e})")
                        pass
                wd.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
                waitingPage(self.waitTime)

                wd.save_screenshot(f"./{self.dir_1st}/Main_Series_{cnt}_{get_today()}.png")  # 스크린 샷
            except TimeoutException:
                print("TimeoutException: 엘리먼트 로딩 시간 초과")
                # 대기 시간 초과에 대한 처리 코드 작성

            wd.save_screenshot(f"./{self.dir_1st}/Main_Series_{cnt}_{get_today()}.png")  # 스크린 샷
        wd.quit()
        print("Number of SONY Main Series:", len(set_mainSeries))
        return set_mainSeries

    ###=====================get info Sub page====================================##
    def __getSeries__(self, url: str) -> dict:
        cntTryTotal = 5
        for cntTry in range(cntTryTotal):
            try:
                dictSeries = {}
                wd = WebDriver.get_crome()
                wd.get(url=url)
                print("connect to", url)

                waitingPage(self.waitTime)
                # wd = closeModalCookie(wd)  # 쿠키 모달창 닫기

                wd.execute_script("window.scrollTo(0, 200);")
                wait = WebDriverWait(wd, 10)
                elements = wait.until(EC.visibility_of_all_elements_located(
                    (By.CLASS_NAME, 'custom-variant-selector__item')))  ## 시리즈의 모든 인치 모델 가져 옴

                for element in elements:
                    try:
                        element_url = element.get_attribute('href')
                        label = getNamefromURL(element_url)
                        dictSeries[label] = element_url  # url 만 저장 함
                    except Exception as e:
                        print(f"getPage2nd error ({e})")
                        pass
                wd.save_screenshot(f"./{self.dir_2nd}/{getNamefromURL(url)}_Sub_Series_{get_today()}.png")  # 스크린 샷
                wd.quit()

                if len(dictSeries) == 0:  # url을 가져오지 못하면 에러 발생
                    raise Exception

                waitingPage(self.waitTime)
                print(f"Number of SONY {getNamefromURL(url)[4:]} series:", len(dictSeries))

                return dictSeries
            except Exception as e:
                wd.quit()
                waitingPage(self.waitTime)
                print(f"stage 2nd try: {cntTry}/{cntTryTotal}")

    ###======================final stage===============================##
    def __getSpec__(self, model) -> dict:
        specs = Sepcifications()
        score = Score()
        dictSpec = specs.getSpec(maker="sony", )
        series = model.split("-")[1][2:-1]
        dictSpec.update(score.getRthinsScore(series))
        return dictSpec
        pass

    def __getData4th__(self, dfModels):
        new_columns = dfModels['model'].apply(self.__extractInfo__)
        df_combined = pd.concat([new_columns, dfModels], axis=1).set_index('model')
        return df_combined


# ===============================

    def __extractInfo__(self, model):
        grade = model.split("-")[0]
        size = model.split("-")[1][:2]
        series = model.split("-")[1][2:-1]
        year = model.split("-")[1][-1]

        year_mapping = {
            "N": 2025,
            "M": 2024,
            'L': 2023,
            'K': 2022,
            'J': 2021,
            # 추가적인 알파벳과 연도 대응 관계를 추가할 수 있음
        }

        if year in year_mapping:
            year = year_mapping[year]
        else:
            # 알파벳과 대응하는 연도가 없을 경우 기본값으로 설정할 연도를 지정
            year = ""

        return pd.Series([year, series, size, grade], index=['year', 'series', 'size', 'grade'])

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



def closeModalCookie(webdriver):
        # 모달 창 요소를 식별하여 클릭
        try:
            close_button = webdriver.find_element(By.CLASS_NAME, '//*[@id="onetrust-close-btn-container"]/button')
            webdriver = WebDriver.move_element_to_center(webdriver, close_button)
            close_button.click()
            waitingPage()
        except:
            pass
        return webdriver
