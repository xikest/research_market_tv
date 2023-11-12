import time
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import requests
from .tools import WebDriver
from urllib.parse import urljoin, urlparse, parse_qs


class Amazon():
    def __init__(self, webdriver_path: str, browser_path: str=None, enable_headless=True):
        self.web_driver = WebDriver(executable_path=webdriver_path, browser_path=browser_path, headless=enable_headless)
        self.wait_time = 1


    def get_allcomments(self,url:str="https://www.amazon.com/Sony-QD-OLED-7-1-4ch-Theater-Speaker/product-reviews/B0CBDJKR1V/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews",
                        maker=None, product=None) -> list:

        allcomments_list = []

        while True:
            driver = self.web_driver.get_chrome()
            url = url.lower()
            print(f"connecting to {url}")
            driver.get(url)
            time.sleep(self.wait_time)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            # next_page = self._is_next_page(soup)
            allcomments_list.extend(self._get_comments(soup=soup, url=url, maker=maker, product=product))
            driver.quit()

            try:
                next_page_link = driver.find_element(By.CLASS_NAME, 'a-last')
                next_page_link.click()
                time.sleep(self.wait_time)
                print("Next page 링크를 클릭했습니다.")
            except Exception as e:
                print(e)
                break  # 만약 다음 페이지가 없으면 반복문을 종료합니다.

        df=pd.DataFrame(allcomments_list)
        df = df.reset_index()
        # print(df.head())
        # print(df.tail())
        df.to_csv('test.csv', index=False)
        return allcomments_list



    def _get_comments(self, soup, url=None, maker=None, product=None) -> list:
        quote_contents = soup.find_all('div', class_='a-row a-spacing-small review-data')
        comments_list = []
        for quote_content in quote_contents:
            comments = quote_content.span.get_text(strip=True)
            comments_list.append({"url":url, 'Maker': maker, 'Product': product, 'Comments': comments})
            # print("comments:", comments)
        return comments_list


    def _is_next_page(self, soup) -> str:
        next_page_link = soup.find('li', class_='a-last').find('a')
        next_page_link = "https://amazon.com"+next_page_link['href'].lower()
        return next_page_link
    #
    # def is_different_url(self, url1, url2):
    #     # URL을 정규화하여 비교하는 함수
    #     parsed_url1 = urlparse(url1)
    #     parsed_url2 = urlparse(url2)
    #
    #     # 하나라도 다른 조건이 있다면 True 반환
    #     return (
    #             parsed_url1.scheme != parsed_url2.scheme or
    #             parsed_url1.netloc != parsed_url2.netloc or
    #             parsed_url1.path != parsed_url2.path or
    #             parse_qs(parsed_url1.query) != parse_qs(parsed_url2.query)
    #     )
