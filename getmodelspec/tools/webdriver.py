from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from typing import Union, Tuple


class WebDriver:
    def __init__(self):

        pass

    @staticmethod
    def get_crome():
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')  # 헤드리스 모드로 실행
        # chrome_options.add_argument('--no-sandbox')  # 헤드리스 크롬 브라우저를 "사용자 네임스페이스" 옵션 없이 실행하도록 설정
        # chrome_options.add_argument('--disable-dev-shm-usage')  # 헤드리스
        chrome_options.add_argument('user-agent={0}'.format(user_agent))  # 에이전트 우회
        # chrome_options.add_argument('lang=ko_kr')  # 브라우저 언어
        wd = webdriver.Chrome(executable_path = 'chromedriver', options=chrome_options)
        return wd


    @staticmethod
    def get_firefox():
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/60.0'
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.add_argument('--headless')  # 헤드리스 모드로 실행
        firefox_options.add_argument('--no-sandbox')  # 헤드리스 파이어폭스 브라우저를 "사용자 네임스페이스" 옵션 없이 실행하도록 설정
        firefox_options.add_argument('--disable-dev-shm-usage')  # 헤드리스 파이어폭스 사용시 필요한 설정
        firefox_options.add_argument('user-agent={0}'.format(user_agent))  # 에이전트 우회
        wd = webdriver.Firefox(executable_path='geckodriver', options=firefox_options)
        return wd

    @staticmethod
    def move_element_to_center(wd:webdriver, element):
        # 객체로 이동
        ActionChains(wd).move_to_element(element).perform()

        # 뷰포트 크기 얻기
        viewport_width = wd.execute_script("return window.innerWidth;")
        viewport_height = wd.execute_script("return window.innerHeight;")

        # 객체의 위치 얻기
        object_x = element.location['x']
        object_y = element.location['y']
        object_width = element.size['width']
        object_height = element.size['height']

        # 화면 중앙으로 이동
        target_x = object_x + object_width / 2 - viewport_width / 2
        target_y = object_y + object_height / 2 - viewport_height / 2
        wd.execute_script(f"window.scrollTo({target_x}, {target_y});")
        return wd
    #
    #
    #
    # @staticmethod
    # def move_and_wait_for_element(wd: webdriver, by: str, value: str, timeout: int = 10,
    #                               expected_conditions: Union[None, str, Tuple] = None) -> webdriver:
    #     """
    #     요소를 화면 중앙으로 이동한 후 해당 요소가 불러와질 때까지 대기합니다.
    #
    #     :param wd: 웹 드라이버 객체
    #     :param by: 요소를 찾기 위한 방법 (예: 'id', 'name', 'class_name' 등)
    #     :param value: 요소를 찾기 위한 값
    #     :param timeout: 대기 시간 (기본값: 10)
    #     :param expected_conditions: 요소의 상태를 확인하기 위한 조건 (기본값: None)
    #                                예: 'visibility_of_element_located', 'element_to_be_clickable' 등
    #     :return: 웹 드라이버 객체
    #     """
    #
    #     wait = WebDriverWait(wd, timeout)
    #
    #     # 요소 찾기
    #     element = wd.find_element(by, value)
    #
    #     # 객체로 이동
    #     ActionChains(wd).move_to_element(element).perform()
    #
    #     # 뷰포트 크기 얻기
    #     viewport_width = wd.execute_script("return window.innerWidth;")
    #     viewport_height = wd.execute_script("return window.innerHeight;")
    #
    #     # 객체의 위치 얻기
    #     object_x = element.location['x']
    #     object_y = element.location['y']
    #     object_width = element.size['width']
    #     object_height = element.size['height']
    #
    #     # 화면 중앙으로 이동
    #     target_x = object_x + object_width / 2 - viewport_width / 2
    #     target_y = object_y + object_height / 2 - viewport_height / 2
    #     wd.execute_script(f"window.scrollTo({target_x}, {target_y});")
    #
    #     if expected_conditions is None:
    #         element = wait.until(EC.visibility_of_element_located((by, value)))
    #     else:
    #         condition_func = getattr(EC, expected_conditions) if isinstance(expected_conditions,
    #                                                                         str) else expected_conditions
    #         element = wait.until(condition_func((by, value)))
    #     return element
