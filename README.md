이 프로젝트는 웹사이트에서 제품 모델 사양을 가져오는 기능을 제공합니다.

## 설명
이 프로젝트는 Selenium 라이브러리를 사용하여 웹사이트에서 제품 정보를 수집합니다.  

## 설치
프로젝트를 사용하기 위해 다음 단계를 따르세요:

시스템에 Python >= 3.10를 설치합니다.
다음 명령을 실행하여 필요한 라이브러리를 설치합니다:
```python
pip install -r requirements.txt
```
Chrome 브라우저 버전과 운영체제에 맞는 [ChromeDriver](https://chromedriver.chromium.org/downloads) 실행 파일을 다운로드합니다.
`chromedriver` 폴더에 chromedriver를 위치시킵니다.
- driver path: `./chromedriver/chromedriver.exe`

GitHub에서 프로젝트 저장소를 클론합니다:
```bash
git clone https://github.com/your-username/GetModelSpec.git
```

## 사용법

```python
from modelspec import ModelScraper
from modelspec import FileManager
from datetime import date

webdriver_path = "./chromedriver/chromedriver.exe"
enable_headless = False

sms = ModelScraper(webdriver_path = webdriver_path, enable_headless=enable_headless)
dict_models = sms.get_models_info()

file_name = f"model_info_web_{date.today().strftime('%Y-%m-%d')}"
FileManager.dict_to_excel(dict_models, file_name=file_name, sheet_name="global")

```

## 주의사항
이 도구는 Selenium을 사용하여 웹 스크래핑을 수행하므로 Chrome 웹 드라이버가 필요합니다. Chrome 웹 드라이버를 설치하고 경로를 올바르게 설정해야 합니다.
빠른 모드를 사용할 경우 일부 정보가 생략되므로 결과의 완전성을 확인하기 위해 정확성을 검토해야 합니다.

## 라이선스
이 프로젝트는 MIT 라이선스를 따릅니다.

## 후원
만약 이 프로젝트가 도움이 되었다면, 커피 한 잔의 후원은 큰 격려가 됩니다. ☕️

