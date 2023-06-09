from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
import subprocess

class WebDriver:
    def __init__(self):

        pass

    @staticmethod
    def getChrome():
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
    def move_element_to_center(driver:"WebDriver", element):
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
    def installChromiumSeleniumBs4():
        """
        설명:
            Colab 환경에서 Chromium, Selenium 및 BeautifulSoup4(bs4)를 설치합니다.
        """
        script = """
           # Add debian buster
           cat > /etc/apt/sources.list.d/debian.list <<'EOF'
           deb [arch=amd64 signed-by=/usr/share/keyrings/debian-buster.gpg] http://deb.debian.org/debian buster main
           deb [arch=amd64 signed-by=/usr/share/keyrings/debian-buster-updates.gpg] http://deb.debian.org/debian buster-updates main
           deb [arch=amd64 signed-by=/usr/share/keyrings/debian-security-buster.gpg] http://deb.debian.org/debian-security buster/updates main
           EOF

           # Add keys
           apt-key adv --keyserver keyserver.ubuntu.com --recv-keys DCC9EFBF77E11517
           apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 648ACFD622F3D138
           apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 112695A0E562B32A

           apt-key export 77E11517 | gpg --dearmour -o /usr/share/keyrings/debian-buster.gpg
           apt-key export 22F3D138 | gpg --dearmour -o /usr/share/keyrings/debian-buster-updates.gpg
           apt-key export E562B32A | gpg --dearmour -o /usr/share/keyrings/debian-security-buster.gpg

           # Prefer debian repo for chromium* packages only
           # Note the double-blank lines between entries
           cat > /etc/apt/preferences.d/chromium.pref << 'EOF'
           Package: *
           Pin: release a=eoan
           Pin-Priority: 500


           Package: *
           Pin: origin "deb.debian.org"
           Pin-Priority: 300


           Package: chromium*
           Pin: origin "deb.debian.org"
           Pin-Priority: 700
           EOF

           # Install chromium and chromium-driver
           apt-get update
           apt-get install chromium chromium-driver

           # Install selenium
           pip install selenium

           # Install bs4
           pip install beautifulsoup4
           
           # Kill the process after installation
           import os
           os.kill(os.getpid(), 9)

       """
        subprocess.run(['bash', '-c', script], check=True, shell=True)




