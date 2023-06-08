from selenium import webdriver

def get_tv_model_score(prefix, model):
    """
    # 함수 호출 예시
    prefix = "https://www.rtings.com/tv/reviews/sony/"
    model = "x85k"
    result = get_tv_model_score(prefix, model)

    # 결과 출력
    for model, scores in result.items():
        print(model)
        for label, score in scores.items():
            print(label + ": " + score)
     """
    
    
    # Chrome WebDriver 생성
    wd = webdriver.Chrome('chromedriver')

    url = prefix + model

    # 웹 페이지 로드
    wd.get(url)

    # scorecard-row-content 클래스를 가진 요소들을 선택
    elements = wd.find_elements_by_css_selector('.scorecard-row-content')

    # 결과를 저장할 딕셔너리 초기화
    scores = {}

    try:
        for element in elements:
            score_element = element.find_element(By.css_selector, '.e-score_box-value')
	label_element = element.find_element(By.css_selector, '.scorecard-row-name')


            score = score_element.text.strip()
            label = label_element.text.strip()

            scores[label] = score

        # WebDriver 종료
        wd.quit()

        return {model: scores}

    except Exception as e:
        # WebDriver 종료
        wd.quit()

        return {model: ""}

