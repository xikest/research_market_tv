import time
import re
import pandas as pd
import numpy as np
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tools.webdriver import WebDriver
from selenium.webdriver import ActionChains





def parse_text_to_dict(text):
    dictSpec = {text[i].strip(): text[i + 1].strip() for i in range(0, len(text)-1, 2)}
    # print(dictSpec)
    return dictSpec


url = 'https://electronics.sony.com/tv-video/televisions/all-tvs/p/xr42a90k'
wd =  WebDriver.get_crome()
wd.get(url=url)
# 페이지 로딩을 위한 대기 시간 설정
wait = WebDriverWait(wd, 10)

# 페이지 로딩 완료를 기다림
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.custom-variant-selector__body')))

#spec 열기
element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "product-specification")))
element.click()

time.sleep(1)

# 클래스에 매칭되는 see_more 요소 모두 가져오기
elements = wd.find_elements(By.CSS_SELECTOR, '.sony-btn.sony-btn--primary--inverse')
elements[1].click() # 두 번째 요소 클릭
time.sleep(1)

#팝업 창의 스크롤 선택 후 클릭
wd.find_element(By.CLASS_NAME, "ps__rail-y").click()

dictSpec={}

for i in range(10):
    elements = wd.find_elements(By.CLASS_NAME, "full-specifications__specifications-single-card__sub-list")
    for element in elements:
        dictSpec.update(parse_text_to_dict(element.text.split('\n')))
        # print(element.text)
    wd.find_element(By.TAG_NAME,'body').send_keys(Keys.PAGE_DOWN)
print(dictSpec)


# time.sleep(10)
# wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

# 아래로 스크롤
# wd.execute_script("window.scrollBy(0, 15 * 100)")  # 500px 아래로 스크롤
# time.sleep(1)
# element = wd.find_element(By.CLASS_NAME, value='product-specification')


# # 아래로 스크롤
# wd.execute_script("window.scrollBy(0, 15 * 100)")  # 500px 아래로 스크롤
# time.sleep(1)
# element = wd.find_element(By.CLASS_NAME, value='product-specification')


# try:
#     dictModel["price"] = [wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'custom-product-summary__price'))).text]
# except:
#     print("price error")
#     pass
#     # dictModel["price_disc"] = [wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'custom-product-summary__price--sale-price'))).text]
#     # dictModel["price"] = [wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'custom-product-summary__price--original-price'))).text]