import time
import re
import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ..tools.webdriver import WebDriver



class GetSONY:
    def __init__(self):
        pass

    def getModels(self) -> pd.DataFrame:

        ## 메인 페이지에서 시리즈를 추출
        seriesUrls = self.getPage1st(url= 'https://electronics.sony.com/tv-video/televisions/c/all-tvs')

        ## 서브 시리즈 페이지에서 모델을 추출
        dict_allSeries = {}
        for url in seriesUrls:
            dictSeries = self.getPage2nd(url=url)
            print(dictSeries)
            dict_allSeries.update(dictSeries)
        print("Number of all Series:", len(dict_allSeries))


        ## 모든 모델 리스트를 추출
        dictModels = {}
        for model_url in dict_allSeries.values():
            print(model_url)
            try:
                dictModels.update(self.getPage3rd(model_url))
            except:
                print("page error:",model_url)
            print("dictModels",dictModels)
        dfModels = pd.DataFrame.from_dict(dictModels, orient="index")
        return dfModels


    ###=====================get info main page====================================##
    def getPage1st(self, url:str) -> set:
        set_mainSeries = set()
        scrolling_cnt: int = 10
        # pageWaiting:int = 5

        wd =  WebDriver.get_crome()
        wd.get(url=url)
        # wait = WebDriverWait(wd, pageWaiting)

        for i in range(scrolling_cnt):
            time.sleep(1)
            # elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'custom-product-grid-item__product-name')))
            elements = wd.find_elements(By.CLASS_NAME, value='custom-product-grid-item__product-name')  ## 모든 인치 모델 가져 옴
            for element in elements:
                try: set_mainSeries.add(element.get_attribute('href')) #URL만 저장 함
                except:
                    print('main_page_error')
                    pass
            wd.find_element(By.TAG_NAME,'body').send_keys(Keys.PAGE_DOWN)
        wd.quit()
        print("Number of SONY Main Series:", len(set_mainSeries))
        return set_mainSeries
    ###=====================get info Sub page====================================##
    def getPage2nd(self, url:str) -> dict:
        dictSeries = {}
        pageWaiting:int = 10

        wd = WebDriver.get_crome()
        wd.get(url=url)
        wait = WebDriverWait(wd, pageWaiting)

        seriesName = self.getNamefromURL(url)
        # time.sleep(5)
        elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'custom-variant-selector__item')))  ## 시리즈의 모든 인치 모델 가져 옴
        # elements = wd.find_elements(By.CLASS_NAME, 'custom-variant-selector__item')  ## 시리즈의 모든 인치 모델 가져 옴
        for element in elements:
            try:
                element_url = element.get_attribute('href')
                label = self.getNamefromURL(element_url)
                dictSeries[label]=element_url # url 만 저장 함
            except:
                print('sub_page_error')
                pass
        wd.quit()
        print(f"Number of SONY {seriesName[4:]} series:", len(dictSeries))
        return dictSeries

    ###======================final stage===============================##
    def getPage3rd(self, url:str) -> pd.DataFrame:
        dictModel = {}
        pageWaiting:int = 10

        wd = WebDriver.get_crome()
        wd.get(url=url)
        wait = WebDriverWait(wd, pageWaiting)

        #모델 정보 확인
        model = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'product-intro__code'))).text.replace("Model: ", "")
        descr = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'product-intro__title'))).text.strip()
        # print(descr)
        dictModel["Year"] = re.findall(r"\((\d{4})\)", descr)
        dictModel["Size"] = re.findall(r"(\d+\")", descr)
        dictModel["Descr"] = descr

        #가격 정보 확인
        dictModel["price"] = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'custom-product-summary__price'))).text

        #이미지 정보 및 url 저장
        dictModel["src_url"] = url
        dictModel["Img_url"] = wait.until(EC.presence_of_element_located((By.XPATH, '//app-custom-cx-media//img'))).get_attribute('src')

        # spec 열기
        wd.find_elements(By.CSS_SELECTOR, ".cx-icon.black_plus")[0].click()
        time.sleep(1)

        # 클래스에 매칭되는 see_more 요소 모두 가져오기
        wd.find_elements(By.CSS_SELECTOR, '.cx-icon.see-more-features.atom-icon-arrow-down-blue')[1].click()  # 두 번째 요소 클릭
        time.sleep(1)

        #스펙 팝업 창의 스크롤 선택 후 클릭: 팝업 창으로 이동
        wd.find_element(By.CLASS_NAME, "ps__rail-y").click()

        #스펙 팝업 창의 스펙 가져오기
        for i in range(10):
            elements = wd.find_elements(By.CLASS_NAME, "full-specifications__specifications-single-card__sub-list")
            for element in elements:
                dictModel.update(self.parseTextToDict(element.text.split('\n')))
                # print(element.text)
            wd.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        # print({model:dictModel})


        wd.quit()
        return {model:dictModel}

    def getNamefromURL(self, url):
        """
        마지막 / 이후 문자만 가져 옴
        """
        return url.rsplit('/', 1)[-1]

    def parseTextToDict(self, text):
        return {text[i].strip(): text[i + 1].strip() for i in range(0, len(text) - 1, 2)}

