import time
import re
import pandas as pd
import numpy as np
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tools.webdriver import WebDriver




def getPage3rd(url: str) -> pd.DataFrame:
    pageWaiting: int = 10

    wd = WebDriver.get_crome()
    wd.get(url=url)
    wait = WebDriverWait(wd, pageWaiting)

    dict_models = {}
    # time.sleep(waitingPage) # 웹페이지 대기

    name = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'product-intro__code'))).text
    print(name)
    descr = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'product-intro__title'))).text.strip()
    print(descr)

    try:
        price = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'custom-product-summary__price'))).text
        print(price)
        price_disc = np.NaN
    except:
        price_disc = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, 'custom-product-summary__price--sale-price'))).text
        print(price_disc)
        price = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, 'custom-product-summary__price--original-price'))).text
        print(price)

    element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'product-specification')))  # 스펙창을 열기 위해 클릭
    print(element.is_enabled())
    element.click()

    element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sony-btn--primary--inverse")))  # 스펙 팝업창 띄우기
    element.click()

    # 스크롤의 높이와 이동 가능한 거리를 추출합니다. (스펙 팝업창의 스크롤)
    scrollable_distance_attr = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "ps__rail-y"))).get_attribute('style')
    scroll_distance = int(re.search(r'height: (\d+)px', scrollable_distance_attr).group(1))

    scrollable_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ps__thumb-y")))
    style_attr = scrollable_element.get_attribute('style')
    scroll_height = int(re.search(r'height: (\d+)px', style_attr).group(1))

    # 팝업창의 스크롤 클릭: 스크롤링을 하기 위함
    scrollable_element.click()

    cnt = int(scroll_distance / scroll_height)  # 스크롤 바의 높이와 거리 값을 추출하여 pagedown 누름 동작 횟수 정의
    dict_spec = {}
    for i in range(cnt):
        elements = wait.until(EC.presence_of_all_elements_located(
            (By.CLASS_NAME, "full-specifications__specifications-single-card__sub-list")))  # 모든 스펙 긁어 오기
        for element in elements:
            try:
                # print(element.text)
                dict_spec.update(parse_text_to_dict(element.text))
            except:
                print('main_page_error')
                pass

        # 스크롤 작업을 수행합니다.
        wd.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)

    print(dict_spec)

    dict_models = {}
    df_models = pd.DataFrame()
    for model_url in dict_allSeries.values():
        # wd = webdriver.Chrome('chromedriver', options=self.chrome_options)
        df_model = self.getPage3rd(model_url)
        df_models = pd.concat([df_models, df_model], axis=0)
        # dict_models.update(dict_model)
        # print(dict_models)
