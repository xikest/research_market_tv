from selenium.webdriver.common.by import By
from ..tools.webdriver import WebDriver
from ..tools.functions import *
import time

class GetScore():
    def __init__(self):
        pass

    def getRthinsScore(prefix:str="https://www.rtings.com/tv/reviews/sony/",
                           model:str="x85k"):

        # Chrome WebDriver 생성
        wd = WebDriver.get_crome()
        url = prefix + model

        # 웹 페이지 로드
        wd.get(url)
        time.sleep(generate_random_number())

        # scorecard-row-content 클래스를 가진 요소들을 선택
        elements = wd.find_elements(By.CLASS_NAME, "scorecard-row-content")

        # 결과를 저장할 딕셔너리 초기화
        scores = {}

        try:
            for element in elements:
                label = element.find_element(By.CLASS_NAME, 'scorecard-row-name').text.strip()
                score = element.find_element(By.CLASS_NAME, 'e-score_box-value ').text.strip()
                scores[label] = score

            # WebDriver 종료
            wd.quit()
            return {model: scores}

        except Exception as e:
            # WebDriver 종료
            wd.quit()

            return {model: ""}

