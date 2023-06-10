import requests
from bs4 import BeautifulSoup
from ..tools.functions import *
import re
class Specifications:
    dictLinks = None

    def __init__(self, escapeNum:int=200):
        self.escapeNum = escapeNum
        self.dictUrlModel = {"sony":"https://www.displayspecifications.com/en/brand/47e6f",
                             "lge":"",
                             "panasonic":"",
                             "hisense":"",
                             "tpv":"",
                             "sharp":""}
        pass

    def getSpec(self, maker:str = "sony", model:str="XR-65A80L",  url = "https://www.displayspecifications.com/en/brand/47e6f"):

        # print(f"{maker}: {model} specification ")

        # 클래스 변수에 각 모델의 spec 접속 Link 업데이트
        if Specifications.dictLinks == None:
            try:
                urlSpecs = self.dictUrlModel.get(maker)
            except:
                urlSpecs = url
            Specifications.dictLinks = self.__getAllModels__(urlSpecs)
        # 클래스 변수 spec 접속 Link에서 접속 주소 가져 옴
        urlModel = Specifications.dictLinks.get(model)
        return self.__getSpec__(urlModel)

    def getSepcs(self, maker:str = "sony", url = "https://www.displayspecifications.com/en/brand/47e6f"):
        dictspecs = {}
        cnt = 0

        # 클래스 변수에 각 모델의 spec 접속 Link 업데이트
        if Specifications.dictLinks == None:
            try:   urlSpecs = self.dictUrlModel.get(maker)
            except:urlSpecs = url
            Specifications.dictLinks = self.__getAllModels__(urlSpecs)

        print(f'total: {len(Specifications.dictLinks)}')

        # 클래스 변수 spec 접속 Link에서 접속 주소 가져 옴
        for model, urlModel in Specifications.dictLinks.items():
            dictspecs[model] = self.__getSpec__(urlModel)
            print(model, urlModel)
            cnt += 1
            if cnt == self.escapeNum:
                return dictspecs
        return dictspecs
    def __getAllModels__(self, url: str = "https://www.displayspecifications.com/en/brand/47e6f") -> dict:
        time.sleep(1)
        response = requests.get(url)
        if response.ok:
            soup = BeautifulSoup(response.text, 'html.parser')
            containers = soup.find_all(class_='model-listing-container-80')
            result = {}
            for cnt, container in enumerate(containers):
                for element in container:
                    linkLabel = element.find('h3').find('a')
                    href = linkLabel['href']
                    label = linkLabel.text.split()[1:]
                    label = ' '.join(label)
                    result[label] = href
            return result
        else:
            print("Failed to retrieve the webpage.")
            return None

    def __getSpec__(self, url: str = "https://www.displayspecifications.com/en/model/01b732ea") -> dict:
        time.sleep(1)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        section_headers = soup.find_all(class_='section-header')
        information_tables = soup.find_all(class_='model-information-table row-selection')

        combined_dict = {}
        for header, table in zip(section_headers, information_tables):
            header_text = header.find('h2', class_='header').text.strip()
            rows = table.find_all('tr')
            info_dict = {}
            for row in rows:
                columns = row.find_all('td')
                try: text_p = columns[0].find('p').text
                except:
                    text_p = ""
                key = columns[0].text.replace(text_p, "")
                value = columns[1].get_text(strip=True)  # HTML 태그 제거
                if key == "":
                    key = header_text + "etc"
                info_dict[key] = value  # info_dict 업데이트
            combined_dict.update(info_dict)
        return combined_dict

