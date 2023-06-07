# Research on the TV market

TV 제품의 사양 및 평가 지표 정보를 수집합니다.

## 개요

이 프로젝트는 TV 제품의 모델 정보를 수집하는 스크래핑 도구입니다. 주요 기능은 다음과 같습니다:

- 메인 페이지에서 시리즈 추출
- 서브 시리즈 페이지에서 모델 추출
- 모델 정보를 수집하여 데이터프레임으로 변환
- 데이터프레임을 엑셀 파일로 저장

## 요구사항

- Python 3.7 이상
- pandas 라이브러리
- BeautifulSoup 라이브러리
- Selenium 라이브러리

## 사용법

### 1) GetSONY 클래스의 인스턴스 생성:
envr 매개변수는 실행 환경을 지정합니다. "weak"로 설정하면 샘플 데이터만 추출하고 스크래핑을 빠르게 완료합니다.
```python
sony_scraper = GetSONY(envr="weak")
```
### 2) 모델 정보 가져오기:
toExcel 매개변수를 True로 설정하면 추출한 모델 정보를 Excel 파일로 저장합니다.
```python
dfModels = sony_scraper.getModels()
```

### 3) 결과 확인:
#### 3-1) 데이터프레임 출력:
```python
print(dfModels)

```
#### 3-2) Excel 파일로 저장된 경우:
```pytohn
dfModels = pd.read_excel("sony_TV_series_YYYY-MM-DD.xlsx")
```

## 참고 문서
- [SONY 공식 웹사이트](https://electronics.sony.com)
- [pandas 공식 문서](https://pandas.pydata.org/docs/)
- [BeautifulSoup 공식 문서](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Selenium 공식 문서](https://selenium-python.readthedocs.io/)
