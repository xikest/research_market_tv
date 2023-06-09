from selenium.webdriver.common.by import By
from ..tools.wdriver import Wdriver
from ..tools.functions import *
import time

class Score():
    def __init__(self):
        pass

    def getRthinsScore(self, prefix:str="https://www.rtings.com/tv/reviews/sony/",
                           series:str="x85k") -> dict:
        print(f"TV score info: {prefix}{series}")
        # Chrome WebDriver 생성
        wd = Wdriver.get_crome()
        url = prefix + series

        # 웹 페이지 로드
        wd.get(url)
        time.sleep(generate_random_number())

        # scorecard-row-content 클래스를 가진 요소들을 선택
        elements = wd.find_elements(By.CLASS_NAME, "scorecard-row-content")

        # 결과를 저장할 딕셔너리 초기화
        dictScores = {}

        try:
            for element in elements:
                label = element.find_element(By.CLASS_NAME, 'scorecard-row-name').text.strip()
                score = element.find_element(By.CLASS_NAME, 'e-score_box-value ').text.strip()
                dictScores[label] = score

            # WebDriver 종료
            wd.quit()
            return dictScores

        except Exception as e:
            # WebDriver 종료
            wd.quit()

            return dictScores

