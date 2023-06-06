from selenium import webdriver

class WebDriver:
    def __init__(self):

        pass

    @staticmethod
    def get_crome():
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')  # 헤드리스 모드로 실행
        chrome_options.add_argument('--no-sandbox')  # 헤드리스 크롬 브라우저를 "사용자 네임스페이스" 옵션 없이 실행하도록 설정
        chrome_options.add_argument('--disable-dev-shm-usage')  # 헤드리스
        chrome_options.add_argument('user-agent={0}'.format(user_agent))  # 에이전트 우회
        # chrome_options.add_argument('lang=ko_kr')  # 브라우저 언어
        wd = webdriver.Chrome('chromedriver', options=chrome_options)
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

