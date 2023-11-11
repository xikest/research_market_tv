from selenium.webdriver.common.by import By
from modelspec.tools.webdriver import WebDriver
import time

class TVscore():
    def __init__(self, executable_wd_path=""):
        self.dictUrlModel = {"sony":"https://www.rtings.com/tv/reviews/sony/",
                             "lge":"",
                             "panasonic":"",
                             "hisense":"",
                             "tpv":"",
                             "sharp":""}
        self.wd = WebDriver(executable_path=executable_wd_path)
        pass

    def getRthinsScore(self, prefix:str="https://www.rtings.com/tv/reviews/sony/",
                           series:str="x85k", product_tpye="oled", maker=None, trackingLog=False) -> dict:

        # Chrome WebDriver 생성
        driver = self.wd.get_chrome()

        if maker != None:
            try:
                prefix = self.dictUrlModel.get(maker)
            except:
                pass

        url = prefix + series+ "-" +product_tpye
        url = url.lower()
        if trackingLog == True:
            print(f"TV score info: {url}")
        # 웹 페이지 로드
        driver.get(url)
        time.sleep(1)

        # scorecard-row-content 클래스를 가진 요소들을 선택
        elements = driver.find_elements(By.CLASS_NAME, "scorecard-row-content")

        # 결과를 저장할 딕셔너리 초기화
        dictScores = {}

        try:
            for element in elements:
                label = element.find_element(By.CLASS_NAME, 'scorecard-row-name').text.strip()
                score = element.find_element(By.CLASS_NAME, 'e-score_box-value ').text.strip()
                dictScores[label] = score

            # WebDriver 종료
            driver.quit()
            return dictScores

        except Exception as e:
            print(f"get specification error: {e}")
            # WebDriver 종료
            driver.quit()

            return dictScores

