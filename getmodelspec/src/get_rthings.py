from selenium import webdriver

# Chrome WebDriver 생성
wd = webdriver.Chrome('chromedriver')

prefix = "https://www.rtings.com/tv/reviews/sony/x85k"
model = "x85k"
url = prefix + model

# 웹 페이지 로드
wd.get(url)

# scorecard-row-content 클래스를 가진 요소들을 선택
elements = wd.find_elements_by_css_selector('.scorecard-row-content')

# 각 요소에서 score와 name을 추출하여 출력
for element in elements:
    score_element = element.find_element_by_css_selector('.e-score_box-value')
    name_element = element.find_element_by_css_selector('.scorecard-row-name')
    
    score = score_element.text.strip()
    name = name_element.text.strip()
    print(score)
    print(name)

# WebDriver 종료
wd.quit()

