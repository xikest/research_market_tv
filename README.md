이 프로젝트는 웹사이트에서 제품 모델 사양을 가져오는 기능을 제공합니다.

## 설명
이 프로젝트는 웹사이트에서 제품 정보를 수집하고 분석 합니다.
> **Demo Note book**  
> [model spec information](https://colab.research.google.com/github/xikest/research-market-tv/blob/main/notebook/quick_guide_get_models.ipynb)  
> [sentiment gpt analysis](https://colab.research.google.com/github/xikest/research-market-tv/blob/main/notebook/quick_guide_sentgpt.ipynb)
## 주의사항
Selenium을 사용하여 웹 스크래핑을 수행하므로 Chrome 웹 드라이버가 필요합니다.   
Chrome 웹 드라이버를 설치하고 경로를 올바르게 설정해야 합니다.

## 설치
프로젝트를 사용하기 위해 다음 단계를 따르세요  
다음 명령을 실행하여 필요한 라이브러리를 설치합니다
```python
pip install -r requirements.txt
```
Chrome 브라우저 버전과 운영체제에 맞는 [ChromeDriver](https://chromedriver.chromium.org/downloads) 실행 파일을 다운로드합니다.  
Chrome 브라우저와 드라이버의 위치를 지정 합니다.  
Chrome 브라우저의 위치는 선택 입니다.  
※ path에 문제가 발생하면 절대 경로로 변경하여 실행하세요.

```
webdriver_path: `./chromedriver/chromedriver.exe`
browser_path = `./chrome/chrome.exe`
```

아래 스크립트로 `Chrome 브라우저와 드라이버 및 필수 패키지`를 설치 할 수도 있습니다.
```bash
install_env.sh
```

## 사용법

기본은 headless로 동작합니다. `enable_headless`를 통해 `mode`를 변경할 수 있습니다.

```python
from modelspec import ModelScraper
from modelspec import FileManager
from datetime import date

webdriver_path = "./chromedriver/chromedriver.exe"
browser_path = "./chrome/chrome.exe"
enable_headless = True

sms = ModelScraper(webdriver_path = webdriver_path, browser_path=browser_path, enable_headless=enable_headless)
dict_models = sms.get_models_info()

file_name = f"sony_model_info_web_{date.today().strftime('%Y-%m-%d')}"
FileManager.dict_to_excel(dict_models, file_name=file_name, sheet_name="global")
```


## 라이선스
이 프로젝트는 MIT 라이선스를 따릅니다.

## 후원
만약 이 프로젝트가 도움이 되었다면, 커피 한 잔의 후원은 큰 격려가 됩니다. ☕️

