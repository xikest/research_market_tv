이 프로젝트는 웹사이트에서 제품 모델 사양을 가져오는 기능을 제공합니다.
## 노트북 파일
이 프로젝트는 다음과 같은 노트북 파일을 제공합니다:
각 노트북 파일을 열어 자세한 사용법을 확인하세요
- [제품 라인업 가져오기에 대한 Quick Guide](https://githubtocolab.com/xikest/Research-on-the-TV-market/blob/main/quick_guide_lineup.ipynb)
- [제품 스코어 가져오기에 대한 Quick Guide](https://githubtocolab.com/xikest/Research-on-the-TV-market/blob/main/quick_guide_score.ipynb)
- [제품 사양 가져오기에 대한 Quick Guide](https://githubtocolab.com/xikest/Research-on-the-TV-market/blob/main/quick_guide_specifications.ipynb)

## 설명
이 프로젝트는 Selenium 라이브러리를 사용하여 웹사이트에서 제품 정보를 수집합니다. 
디렉토리 생성, 페이지 로딩 대기, 데이터 백업 등과 같은 작업을 위한 여러 유틸리티 함수를 포함하고 있습니다. 
또한, 웹 드라이버와 상호작용하기 위한 WebDriver 클래스와 웹사이트에서 제품 정보를 가져오는 LineUp 클래스가 포함되어 있습니다.

## 설치
"GetModelSpec" 프로젝트를 사용하기 위해 다음 단계를 따르세요:

시스템에 Python >= 3.7를 설치합니다.
다음 명령을 실행하여 필요한 라이브러리를 설치합니다:
```python
pip install selenium pandas
```
Chrome 브라우저 버전과 운영체제에 맞는 ChromeDriver 실행 파일을 다운로드합니다.
ChromeDriver 실행 파일을 시스템의 PATH 환경 변수에 포함된 디렉토리에 위치시킵니다.
GitHub에서 "GetModelSpec" 프로젝트 저장소를 클론합니다:
```bash
git clone https://github.com/your-username/GetModelSpec.git
```
프로젝트 디렉토리로 이동합니다:
```bash
cd GetModelSpec
```

## 사용법
### 1. 필요한 라이브러리 설치
```bash
pip install selenium pandas openpyxl
```
### 2. lineup 모듈 임포트
```python
from getmodelspec import LineUp
```
### 3. LineUp 클래스 인스턴스 생성
```python
lineup = LineUp()
```
### 4-1. 사이트에서 제품 정보 가져오기
```python
df_global = lineup.getSony(src="global", fastMode=True, toExcel=True)
```
- src: 가져올 Sony 웹사이트의 소스를 지정합니다. "global"을 선택하면 Sony 글로벌 사이트에서 제품 정보를 가져옵니다.
- fastMode: 빠른 모드를 사용할지 여부를 지정합니다. True로 설정하면 일부 정보를 생략하여 더 빠르게 가져옵니다.
- toExcel: 가져온 제품 정보를 Excel 파일로 저장할지 여부를 지정합니다. True로 설정하면 Excel 파일로 저장됩니다.

### 4-2. Sony 일본 사이트에서 제품 정보 가져오기
```python
df_jp = lineup.getSony(src="jp", fastMode=True, toExcel=True)
```
- src: 가져올 Sony 웹사이트의 소스를 지정합니다. "jp"를 선택하면 Sony 일본 사이트에서 제품 정보를 가져옵니다.
- toExcel: 가져온 제품 정보를 Excel 파일로 저장할지 여부를 지정합니다. True로 설정하면 Excel 파일로 저장됩니다.

## 주의사항
이 도구는 Selenium을 사용하여 웹 스크래핑을 수행하므로 Chrome 웹 드라이버가 필요합니다. Chrome 웹 드라이버를 설치하고 경로를 올바르게 설정해야 합니다.
빠른 모드를 사용할 경우 일부 정보가 생략되므로 결과의 완전성을 확인하기 위해 정확성을 검토해야 합니다.

## 라이선스
이 프로젝트는 MIT 라이선스를 따릅니다.

## 후원
만약 이 프로젝트가 도움이 되었다면, 커피 한 잔의 후원은 큰 격려가 됩니다. ☕️

