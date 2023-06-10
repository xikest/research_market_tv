from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import time
class WebDriver:
    def __init__(self):

        pass

    @classmethod
    def getChrome(cls):
        """
        설명:
            헤드리스 모드로 실행되는 Chrome 웹 드라이버 객체를 반환합니다.
        반환값:
            - driver (WebDriver): Chrome 웹 드라이버 객체
        """
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')  # 헤드리스 모드로 실행
        chrome_options.add_argument('--no-sandbox')  # 헤드리스 크롬 브라우저를 "사용자 네임스페이스" 옵션 없이 실행하도록 설정
        chrome_options.add_argument('--disable-dev-shm-usage')  # 헤드리스
        chrome_options.add_argument('user-agent={0}'.format(user_agent))  # 에이전트 우회
        # chrome_options.add_argument('lang=ko_kr')  # 브라우저 언어
        service = ChromeService(executable_path='chromedriver')
        driver = webdriver.Chrome(service=service , options=chrome_options)
        return driver

    @staticmethod
    def move_element_to_center(driver, element):
        """
        설명:
            주어진 웹 요소(element)를 뷰포트의 중앙으로 이동시킵니다.
        매개변수:
            - driver (WebDriver): Selenium 웹 드라이버 객체
            - element: 움직일 웹 요소
        반환값:
            - driver (WebDriver): 이동된 웹 드라이버 객체
        """
        # 객체로 이동
        ActionChains(driver).move_to_element(element).perform()

        # 뷰포트 크기 얻기
        viewport_width = driver.execute_script("return window.innerWidth;")
        viewport_height = driver.execute_script("return window.innerHeight;")

        # 객체의 위치 얻기
        object_x = element.location['x']
        object_y = element.location['y']
        object_width = element.size['width']
        object_height = element.size['height']

        # 화면 중앙으로 이동
        target_x = object_x + object_width / 2 - viewport_width / 2
        target_y = object_y + object_height / 2 - viewport_height / 2
        driver.execute_script(f"window.scrollTo({target_x}, {target_y});")
        return driver

    @staticmethod
    def getDistanceScrollToBtm(driver):
        # 스크롤을 페이지 아래로 내리기
        driver.find_element_by_tag_name('body').send_keys(Keys.END)
        time.sleep(1)  # 스크롤이 내려가는 동안 대기

        # 스크롤이 이동한 거리 계산
        scrollDistance = driver.execute_script("return window.pageYOffset;")

        # 계산한 거리를 500씩 이동하며 스크롤 내리기
        # 스크롤이 이동한 거리 계산
        scrollDistance = driver.execute_script("return window.pageYOffset;")

        # Home 키를 눌러 시작 위치로 복귀
        driver.find_element_by_tag_name('body').send_keys(Keys.HOME)
        time.sleep(1)  # 스크롤이 위로 올라가는 동안 대기
        return scrollDistance



    @staticmethod
    def getScrollDistanceTotal(driver):
        total_scroll_distance = 0
        prev_scroll_distance = -1

        while True:
            scroll_distance = get_scroll_distance(driver)
            total_scroll_distance += scroll_distance

            # 새로운 스크롤 위치와 이전 스크롤 위치가 같다면 스크롤이 더 이상 되지 않았으므로 종료합니다.
            if scroll_distance == 0 or scroll_distance == prev_scroll_distance:
                break

            prev_scroll_distance = scroll_distance

        # 초기 위치로 복귀하기 위해 페이지 맨 위로 스크롤합니다.
        driver.execute_script("window.scrollTo(0, 0)")
        time.sleep(1)

        # 총 이동한 거리를 출력합니다.
        # print("Total scroll distance:", total_scroll_distance)
        return total_scroll_distance

def get_scroll_distance(driver):
    # 현재 페이지의 스크롤 위치를 가져옵니다.
    current_scroll_position = driver.execute_script("return window.pageYOffset")
    # 스크롤 이벤트를 발생시킵니다.
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(1)
    # 새로운 스크롤 위치를 가져옵니다.
    new_scroll_position = driver.execute_script("return window.pageYOffset")
    # 페이지 이동 거리를 계산합니다.
    scroll_distance = new_scroll_position - current_scroll_position
    # print(f"scroll_distance: {scroll_distance}")
    return scroll_distance