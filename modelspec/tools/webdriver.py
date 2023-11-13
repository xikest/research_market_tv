from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from typing import Optional
import subprocess
import os
import platform

class WebDriver:
    def __init__(self, executable_path:str="./chromedriver.exe", browser_path:str=None, headless=False):
        self.executable_path = executable_path
        self.browser_path = browser_path
        self.headless= headless
        self.driver = None

        pass
    def get_chrome(self):

        chrome_options = Options()
        chrome_options.binary_location=self.browser_path
        chrome_options.add_argument(
            "--user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36'")# 에이전트 우회
        # chrome_options.page_load_strategy = 'none'
        if self.headless:
            chrome_options.add_argument('--headless=chrome')  # 헤드리스 모드로 실행
            chrome_options.add_argument('--disable-gpu')  # 헤드리스 모드로 실행
        # --headless = chrome
        chrome_options.add_argument('--no-sandbox')  # 헤드리스 크롬 브라우저를 "사용자 네임스페이스" 옵션 없이 실행하도록 설정
        chrome_options.add_argument('--disable-dev-shm-usage')

        # chrome_options.add_argument('lang=ko_kr')  # 브라우저 언어
        service = Service(executable_path = self.executable_path)  # 크롬 드라이버 경로 설정
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        return self.driver
    def move_element_to_center(self, element):
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
        driver = self.driver
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
        return None
    def getDistanceScrollToBtm(self):
        # 스크롤을 페이지 아래로 내리기
        driver = self.driver
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
    def get_scroll_distance_total(self):
        total_scroll_distance = 0
        prev_scroll_distance = -1
        while True:
            scroll_distance = self.__get_scroll_distance__()
            total_scroll_distance += scroll_distance
            # print("total distance: ", total_scroll_distance)
            # 새로운 스크롤 위치와 이전 스크롤 위치가 같다면 스크롤이 더 이상 되지 않았으므로 종료합니다.
            if scroll_distance == 0 or scroll_distance == prev_scroll_distance:
                break
            prev_scroll_distance = scroll_distance
        # 초기 위치로 복귀하기 위해 페이지 맨 위로 스크롤합니다.
        self.driver.execute_script("window.scrollTo(0, 0)")
        time.sleep(1)
        # 총 이동한 거리를 출력합니다.
        # print("Total scroll distance:", total_scroll_distance)
        return total_scroll_distance
    def __get_scroll_distance__(self):
        driver = self.driver
        # 현재 페이지의 스크롤 위치를 가져옵니다.
        current_scroll_position = driver.execute_script("return window.scrollY || window.pageYOffset")
        # 스크롤 이벤트를 발생시킵니다.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)
        # 새로운 스크롤 위치를 가져옵니다.
        new_scroll_position = driver.execute_script("return window.pageYOffset")
        # 페이지 이동 거리를 계산합니다.
        scroll_distance = new_scroll_position - current_scroll_position
        # print(f"scroll_distance: {scroll_distance}")
        return scroll_distance

        @staticmethod
        def install_chrome_and_driver():
            current_os = platform.system()
            if current_os == "Linux":
                chrome_dict= DriverSetting._install_chrome_and_driver_linux()
            elif current_os == "Windows":
                print("windows")
                chrome_dict= DriverSetting._install_chrome_and_driver_win()
            else:
                print("지원하지 않는 운영체제입니다.")

        @staticmethod
        def _install_chrome_and_driver_linux() -> dict:
            # 쉘 스크립트 내용
            shell_script_content = """
            #!/bin/bash
    
            # Download and setup Chrome
            wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/linux64/chrome-linux64.zip
            unzip chrome-linux64.zip
            rm chrome-linux64.zip
            mv chrome-linux64 chrome
            rm chrome-linux64
    
            # Download and setup ChromeDriver
            wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/linux64/chromedriver-linux64.zip
            unzip chromedriver-linux64.zip
            rm chromedriver-linux64.zip
            mv chromedriver-linux64 chromedriver
            rm chromedriver-linux64
    
            # Return Chrome installation path and ChromeDriver path
            echo $(pwd)/chrome
            echo $(pwd)/chromedriver
            """

            script_file_path = "set_chrome.sh"
            with open(script_file_path, "w") as script_file:
                script_file.write(shell_script_content)

            # 쉘 스크립트 실행
            result = subprocess.run(["bash", script_file_path], capture_output=True, text=True)

            # 쉘 스크립트 파일 삭제 (선택 사항)
            os.remove(script_file_path)

            current_dir = os.path.abspath(os.getcwd())
            return {"chrome_path": os.path.join(current_dir, "chrome"),
                    "driver_path": os.path.join(current_dir, "chromedriver")}

        @staticmethod
        def _install_chrome_and_driver_win() -> dict:
            # Windows에서 사용되는 배치 파일 내용
            batch_script_content = """
            @echo off
    
            :: Download and setup Chrome
            powershell -Command "& {Invoke-WebRequest -Uri 'https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/win64/ChromeSetup.exe' -OutFile 'chrome_installer.exe'}"
            Start-Process -Wait -FilePath 'chrome_installer.exe' -ArgumentList '/silent /install'
            del 'chrome_installer.exe'
    
            :: Download and setup ChromeDriver
            powershell -Command "& {Invoke-WebRequest -Uri 'https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/win64/chromedriver_win64.zip' -OutFile 'chromedriver.zip'}"
            Expand-Archive -Path 'chromedriver.zip' -DestinationPath 'chromedriver'
            del 'chromedriver.zip'
    
            :: Return Chrome installation path and ChromeDriver path
            echo %cd%\chrome
            echo %cd%\chromedriver
            """

            # 배치 파일에 내용 쓰기
            script_file_path = "set_chrome.bat"
            with open(script_file_path, "w") as script_file:
                script_file.write(batch_script_content)

            # 배치 파일 실행
            result = subprocess.run([script_file_path], shell=True, capture_output=True, text=True)

            # 배치 파일 삭제 (선택 사항)
            os.remove(script_file_path)

            # 반환된 결과에서 경로 추출
            current_dir = os.path.abspath(os.getcwd())
            return {"chrome_path": os.path.join(current_dir, "chrome"),
                    "driver_path": os.path.join(current_dir, "chromedriver")}

