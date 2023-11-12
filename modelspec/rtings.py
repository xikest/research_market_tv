import time
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd

from .tools import WebDriver
class Rtings():
    def __init__(self, webdriver_path: str, browser_path: str=None, enable_headless=True):
        self.web_driver = WebDriver(executable_path=webdriver_path, browser_path=browser_path, headless=enable_headless)
        self.wait_time = 1

    def get_score(self, url:str="https://www.rtings.com/tv/reviews/sony/a95l-oled", format_df=True) -> dict|pd.DataFrame:


        driver = self.web_driver.get_chrome()
        maker = url.split("/")[-2]
        model = url.split("/")[-1]
        url = url.lower()
        print(f"connecting to {url}")
        # 웹 페이지 로드
        driver.get(url)
        time.sleep(self.wait_time)

        # scorecard-row-content 클래스를 가진 요소들을 선택
        elements = driver.find_elements(By.CLASS_NAME, "scorecard-row-content")
        maker_dict = {}
        try:
            score_dict = {}
            for element in elements:
                label = element.find_element(By.CLASS_NAME, 'scorecard-row-name').text.strip()
                score = element.find_element(By.CLASS_NAME, 'e-score_box-value ').text.strip()
                score_dict[label] = score

            # WebDriver 종료
            driver.quit()

            model_dict = {model:score_dict}
            maker_dict = {maker:model_dict}

            rows = []
            # 딕셔너리를 순회하며 데이터프레임 행으로 추가
            for maker, models in maker_dict.items():
                for model, scores in models.items():
                    for score_type, score in scores.items():
                        rows.append({'Maker': maker, 'Model': model, 'Score Type': score_type, 'Score': score})
            scores_df = pd.DataFrame(rows)
            scores_dict = scores_df.to_dict()
            # print("df")
            # print(dict_data)
            if format_df:
                return scores_df
            else:
                return scores_dict

        except Exception as e:
            print(f"get specification error: {e}")
            # WebDriver 종료
            driver.quit()



    def get_commetns(self, url:str="https://www.rtings.com/tv/reviews/sony/a95l-oled", format_df=True) -> dict|pd.DataFrame:

        # Selenium을 사용하여 웹 드라이버 시작
        driver = self.web_driver.get_chrome()
        maker = url.split("/")[-2]
        product = url.split("/")[-1]
        url = url.lower()
        # url = url +"#page-comments"
        print(f"connecting to {url}")
        driver.get(url)
        time.sleep(self.wait_time)
        ## Load More 버튼 열기
        while True:
            try:
                button_div = driver.find_element(By.CLASS_NAME, "comment_list-footer")
                button = button_div.find_element(By.CLASS_NAME, "e-button")
                button.click()
                time.sleep(1)
            except:
                break

        ## get Comments
        try:
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            quote_contents = soup.find_all('div', class_='quote-content')
            comments_list = []
            for idx, quote_content in enumerate(quote_contents):
                comments = quote_content.find_all('p')
                combined_text = ' '.join([comment.get_text(strip=True) for comment in comments])
                comments_list.append({'idx':idx, "url":url, 'maker': maker, 'product': product, 'sentences': combined_text})
                # print("comments:", combined_text)

            comments_df = pd.DataFrame(comments_list).set_index("idx")
            comments_dict = comments_df.to_dict()
            # print(df.head(3))
            # print(comments_dict)
        finally:
            driver.quit()

        if format_df:
            return comments_df
        else:
            return comments_dict
