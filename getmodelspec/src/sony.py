import time
import re
import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import pickle

from ..tools.webdriver import WebDriver



class GetSONY:
    def __init__(self):
        self.watingTime = 5
        pass

    def getModels(self) -> pd.DataFrame:

        # ## 메인 페이지에서 시리즈를 추출
        # seriesUrls = self.getPage1st(url= 'https://electronics.sony.com/tv-video/televisions/c/all-tvs')
        #
        # # ==========================================================================
        # self.backUp(seriesUrls, "seriesUrls")
        # # ==========================================================================
        #
        # ## 서브 시리즈 페이지에서 모델을 추출
        # dictAllSeries = {}
        # for url in seriesUrls:
        #     dictSeries = self.getPage2nd(url=url)
        #     print(dictSeries)
        #     dictAllSeries.update(dictSeries)
        # print("Number of all Series:", len(dictAllSeries))


        # ==========================================================================
        # self.backUp(dictAllSeries, "dictAllSeries")
        with open(f"dictAllSeries.pickle", "rb") as file:
            dictAllSeries = pickle.load(file)

        # dictAllSeries = {"w":"https://electronics.sony.com/tv-video/televisions/all-tvs/p/kd43x80k", "c":"https://electronics.sony.com/tv-video/televisions/all-tvs/p/xr55x90l ", "a":"https://electronics.sony.com/tv-video/televisions/all-tvs/p/xr85x90l", "b":"https://electronics.sony.com/tv-video/televisions/all-tvs/p/xr98x90l"}
        # ==========================================================================

        ## 모든 모델 리스트를 추출
        dictModels = {}
        for model_url in dictAllSeries.values():
            print(model_url)
            try:
                dictModels.update(self.getPage3rd(model_url))
            except Exception as e:
                print(model_url, f"\n getPage3rd error ({e})")
        dfModels = pd.DataFrame.from_dict(dictModels, orient="index")
        return dfModels

    ###=====================get info main page====================================##
    def getPage1st(self, url:str) -> set:
        set_mainSeries = set()
        scrolling_cnt: int = 10

        wd =  WebDriver.get_crome()
        wd.get(url=url)
        self.waitingPage(5)
        for i in range(scrolling_cnt):
            time.sleep(1)
            elements = wd.find_elements(By.CLASS_NAME, value='custom-product-grid-item__product-name')  ## 모든 인치 모델 가져 옴
            for element in elements:
                try: set_mainSeries.add(element.get_attribute('href')) #URL만 저장 함
                except Exception as e:
                    print(f"getPage1st error ({e})")
                    pass
            wd.find_element(By.TAG_NAME,'body').send_keys(Keys.PAGE_DOWN)
        wd.quit()
        print("Number of SONY Main Series:", len(set_mainSeries))
        return set_mainSeries

    ###=====================get info Sub page====================================##
    def getPage2nd(self, url:str) -> dict:
        dictSeries = {}

        wd = WebDriver.get_crome()
        wd.get(url=url)
        self.waitingPage(5)

        elements = wd.find_elements(By.CLASS_NAME, 'custom-variant-selector__item')  ## 시리즈의 모든 인치 모델 가져 옴
        for element in elements:
            try:
                element_url = element.get_attribute('href')
                label = self.getNamefromURL(element_url)
                dictSeries[label]=element_url # url 만 저장 함
            except Exception as e:
                print(f"getPage2nd error ({e})")
                pass
        wd.quit()
        print(f"Number of SONY {self.getNamefromURL(url)[4:]} series:", len(dictSeries))
        return dictSeries

    ###======================final stage===============================##
    def getPage3rd(self, url:str) -> dict:
        dictSpec = {}

        wd = WebDriver.get_crome()
        wd.get(url=url)
        wait = WebDriverWait(wd, self.watingTime)
        self.waitingPage(5)

        #모델 정보 확인
        model = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'product-intro__code'))).text.replace("Model: ", "")
        dictSpec["Descr"] = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'product-intro__title'))).text.strip()

        #가격 정보 확인
        try: dictSpec["price"] = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'custom-product-summary__price'))).text
        except Exception as e:
            print("price error", e)
            dictSpec["price"] = ""

        # print(dictSpec["price"])

        #이미지 정보 및 url 저장
        dictSpec["src_url"] = url
        dictSpec["Img_url"] = wait.until(EC.presence_of_element_located((By.XPATH, '//app-custom-cx-media//img'))).get_attribute('src')
# ====

        # 스크롤 다운
        for i in range(25):
            ActionChains(wd).key_down(Keys.DOWN).perform()
        time.sleep(1)


        # print("spec open")
        # spec 열기
        click_element = wd.find_elements(By.CSS_SELECTOR, ".cx-icon.black_plus")[0]
        ActionChains(wd).move_to_element(click_element).click().perform()
        time.sleep(1)

        # print("see more")
        # 클래스에 매칭되는 see_more 요소 모두 가져오기
        click_element = wd.find_elements(By.CSS_SELECTOR, '.cx-icon.see-more-features.atom-icon-arrow-down-blue')[1]  # 두 번째 요소 클릭
        click_element.click()
        time.sleep(1)

        # print("pop up")
        #스펙 팝업 창의 스크롤 선택 후 클릭: 팝업 창으로 이동
        scroll_element = wd.find_element(By.CLASS_NAME, "ps__rail-y")
        scroll_element.click()

        # print("get info")
        #스펙 팝업 창의 스펙 가져오기
        for i in range(15):
            elements = wd.find_elements(By.CLASS_NAME, "full-specifications__specifications-single-card__sub-list")
            for element in elements:
                soup = BeautifulSoup(element.get_attribute("innerHTML"), 'html.parser')
                dictSpec.update(self.SoupToDict(soup))

            ActionChains(wd).key_down(Keys.PAGE_DOWN).perform()
            time.sleep(1)
            # wd.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        wd.quit()

        dictModel = {model: dictSpec}
        print(f"{model}\n", dictModel)
        return dictModel

# ===============================

    def getNamefromURL(self, url):
        """
        마지막 / 이후 문자만 가져 옴
        """
        return url.rsplit('/', 1)[-1]

    def SoupToDict(self, soup):
        try:
            h4_tag = soup.find('h4').text.strip()
            p_tag = soup.find('p').text.strip()
        except Exception as e:
            print("parser err", e)
            h4_tag = soup.find('h4').text.strip()
            p_tag =  ""
            pass
        return {h4_tag: p_tag}


    def waitingPage(self, sec=5):
        time.sleep(sec) # 웹 페이지 대기
        return None

    def backUp(self, data, filename:str="backup"):
        # 데이터 저장
        with open(f"{filename}.pickle", "wb") as file:
            pickle.dump(data, file)

        # 데이터 불러오기
        with open(f"{filename}.pickle", "rb") as file:
            data = pickle.load(file)

        return data

