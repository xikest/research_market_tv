
import requests
from bs4 import BeautifulSoup
import time
from ..tools.functions import *


class Sepcifications:
    def __init__(self, escapeNum:int=200):
        self.escapeNum = escapeNum
        self.dictUrlModel = {"sony":"https://www.displayspecifications.com/en/brand/47e6f",
                             "lge":"",
                             "panasonic":"",
                             "hisense":"",
                             "tpv":"",
                             "sharp":""}

        pass

    def getSpec(self, maker:str = "sony", model:str="XR-65A80L"):
        print(f"TV spec info: {maker} {model}")
        dictLink = self.__getAllModels__(self.dictUrlModel.get(maker))
        urlModel = dictLink.get(model)
        return self.__getSpec__(urlModel)

    def getSepcs(self, url = "https://www.displayspecifications.com/en/brand/47e6f"):
        dictLink = self.__getAllModels__(url)
        print(f'total: {len(dictLink)}')
        dictspecs = {}
        cnt = 0
        for model, urlModel in dictLink.items():
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
                key = columns[0].text.strip()
                value = columns[1].get_text(strip=True)  # HTML 태그 제거

                if key == "":
                    key = header_text
                info_dict[key] = value  # info_dict 업데이트
            combined_dict.update(info_dict)
        return combined_dict

