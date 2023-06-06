
import pandas as pd
from bs4 import BeautifulSoup

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from ..tools.functions import *
from ..tools.webdriver import WebDriver



class GetSONY:
    def __init__(self, env:str=None):
        self.dir_1st = "sony/log/MainSeries"
        self.dir_2nd = "sony/log/SubSeries"
        self.dir_3rd = "sony/log/models"
        makeDir(self.dir_1st)
        makeDir(self.dir_2nd)
        makeDir(self.dir_3rd)

        self.env = env
        pass
    #
    def getModels(self) -> pd.DataFrame:

        # # 메인 페이지에서 시리즈를 추출
        # seriesUrls = self.getPage1st(url= 'https://electronics.sony.com/tv-video/televisions/c/all-tvs')
        #
        # # ==========================================================================
        # backUp(seriesUrls, "seriesUrls")
        # # ==========================================================================
        #
        # ## 서브 시리즈 페이지에서 모델을 추출
        # dictAllSeries = {}
        # for url in seriesUrls:
        #     dictSeries = self.getPage2nd(url=url)
        #     print(dictSeries)
        #     dictAllSeries.update(dictSeries)
        # print("Number of all Series:", len(dictAllSeries))
        #
        # #
        # # ==========================================================================
        # backUp(dictAllSeries, "dictAllSeries")


        with open(f"dictAllSeries.pickle", "rb") as file:
            dictAllSeries = pickle.load(file)
        # ==========================================================================

        # 모든 모델 리스트를 추출
        dictModels = {}
        for model_url in dictAllSeries.values():
            print(model_url)
            dictModels.update(self.getPage3rd(model_url))

        dfModels = pd.DataFrame.from_dict(dictModels, orient="index")
        return dfModels

    ###=====================get info main page====================================##
    def getPage1st(self, url:str) -> set:
        set_mainSeries = set()
        scrolling_cnt: int = 10

        wd =  WebDriver.get_crome()
        wd.get(url=url)
        wait = WebDriverWait(wd, 10)

        for cnt in range(scrolling_cnt):
            elements = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'custom-product-grid-item__product-name')))  ## 모든 인치 모델 가져 옴
            for element in elements:
                try: set_mainSeries.add(element.get_attribute('href')) #URL만 저장 함
                except Exception as e:
                    print(f"getPage1st error ({e})")
                    pass
            wd.find_element(By.TAG_NAME,'body').send_keys(Keys.PAGE_DOWN)
            wd.save_screenshot(f"./{self.dir_1st}/Main_Series_{cnt}_{get_today()}.png")  # 스크린 샷
            waitingPage(1)
        wd.quit()
        print("Number of SONY Main Series:", len(set_mainSeries))
        return set_mainSeries

    ###=====================get info Sub page====================================##
    def getPage2nd(self, url:str) -> dict:

        for cntTry in range(5):
            try:
                dictSeries = {}
                wd = WebDriver.get_crome()
                wd.get(url=url)
                print("connect to",url)

                wd.execute_script("window.scrollTo(0, 200);")
                wait = WebDriverWait(wd, 10)
                elements = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'custom-variant-selector__item')))  ## 시리즈의 모든 인치 모델 가져 옴
                for element in elements:
                    try:
                        element_url = element.get_attribute('href')
                        label = getNamefromURL(element_url)
                        dictSeries[label]=element_url # url 만 저장 함
                    except Exception as e:
                        print(f"getPage2nd error ({e})")
                        pass
                wd.save_screenshot(f"./{self.dir_2nd}/{getNamefromURL(url)}_Sub_Series_{get_today()}.png")  # 스크린 샷
                wd.quit()

                if len(dictSeries) == 0:  # url을 가져오지 못하면 에러 발생
                    raise Exception

                waitingPage(1)
                print(f"Number of SONY {getNamefromURL(url)[4:]} series:", len(dictSeries))

                return dictSeries
            except Exception as e:
                wd.quit()
                waitingPage(1)
                print(f"stage 2nd try: {cntTry}/5")

    ###======================final stage===============================##
    def getPage3rd(self, url:str) -> dict:

        cntTryTotal = 10
        for cntTry in range(cntTryTotal):
            try:
                dictSpec = {}
                wd = WebDriver.get_crome()
                wd.get(url=url)
                wait = WebDriverWait(wd, 10)
                waitingPage()

                #모델 정보 확인
                wd.execute_script("window.scrollTo(0, 200);")
                elementModel = wd.find_element(By.CLASS_NAME, 'product-intro__code')
                model = elementModel.text.replace("Model: ", "")

                dictSpec["Descr"] = wd.find_element(By.CLASS_NAME, 'product-intro__title').text.strip()

                dir_model = f"{self.dir_3rd}/{model}"
                makeDir(dir_model)

                wd.save_screenshot(f"./{dir_model}/{getNamefromURL(url)}_0_model_{get_today()}.png") # 스크린 샷

                #가격 정보 확인
                try: dictSpec["price"] = wd.find_element(By.CLASS_NAME, 'custom-product-summary__price').text
                except Exception as e:
                    print("price error")
                    dictSpec["price"] = ""


                #이미지 정보 및 url 저장
                dictSpec["src_url"] = url
                dictSpec["Img_url"] = wd.find_element(By.XPATH, '//app-custom-cx-media//img').get_attribute('src')



                elementSpec = wd.find_element(By.ID,"PDPSpecificationsLink")
                wd = WebDriver.move_element_to_center(wd,elementSpec)
                # ActionChains(wd).move_to_element(elementSpec).perform()
                # wd.execute_script("window.scrollTo(0, 1000);")
                wd.save_screenshot(f"./{dir_model}/{getNamefromURL(url)}_1_move_to_spec_{get_today()}.png")  # 스크린 샷

                if self.env == "colab":
                    waitingPage(60)

                # wait.until(EC.visibility_of_element_located((By.ID, 'PDPSpecificationsLink')))
                elementClickSpec = wait.until(EC.element_to_be_clickable((By.ID, 'PDPSpecificationsLink')))
                elementClickSpec.click()

                # waitingPage(5)  # 페이지 로딩 대기 -
                wd.save_screenshot(f"./{dir_model}/{getNamefromURL(url)}_2_after_click_specification_{get_today()}.png")  # 스크린 샷
                try:
                    element_seeMore=wd.find_element(By.XPATH, '//*[@id="PDPOveriewLink"]/div[1]/div/div/div[2]/div/app-product-specification/div/div[2]/div[3]/button')
                    wd = WebDriver.move_element_to_center(wd, element_seeMore)
                    # ActionChains(wd).move_to_element(element_seeMore).perform()
                    wd.save_screenshot(f"./{dir_model}/{getNamefromURL(url)}_3_after_click_see_more_{get_today()}.png")  # 스크린 샷
                    element_seeMore.click()
                except:
                    element_seeMore=wd.find_element(By.XPATH, '//*[@id="PDPOveriewLink"]/div[1]/div/div/div[2]/div/app-product-specification/div/div[2]/div[2]/button')
                    wd = WebDriver.move_element_to_center(wd, element_seeMore)
                    # ActionChains(wd).move_to_element(element_seeMore).perform()
                    wd.save_screenshot(f"./{dir_model}/{getNamefromURL(url)}_3_after_click_see_more_{get_today()}.png")  # 스크린 샷
                    element_seeMore.click()


                waitingPage(1)

                #스펙 팝업 창의 스크롤 선택 후 클릭: 팝업 창으로 이동
                wd.find_element(By.ID, "ngb-nav-0-panel").click()
                #스펙 팝업 창의 스펙 가져오기
                for cnt in range(15):
                    elements = wd.find_elements(By.CLASS_NAME, "full-specifications__specifications-single-card__sub-list")
                    for element in elements:
                        soup = BeautifulSoup(element.get_attribute("innerHTML"), 'html.parser')
                        dictSpec.update(SoupToDict(soup))
                    ActionChains(wd).key_down(Keys.PAGE_DOWN).perform()
                wd.save_screenshot(f"./{dir_model}/{getNamefromURL(url)}_4_end_{get_today()}.png")  # 스크린 샷

                wd.quit()
                dictModel = {model: dictSpec}
                print(f"{model}\n", dictModel)
                return dictModel

            except Exception as e:
                print(f"getPage3rd error: {model} try {cntTry+1}/{cntTryTotal}")
                wd.quit()
                pass




# ===============================


def SoupToDict(soup):
    try:
        h4_tag = soup.find('h4').text.strip()
        p_tag = soup.find('p').text.strip()
    except Exception as e:
        print("parser err", e)
        h4_tag = soup.find('h4').text.strip()
        p_tag =  ""
        pass
    return {h4_tag: p_tag}
