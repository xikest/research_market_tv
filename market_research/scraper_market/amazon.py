import time
from bs4 import BeautifulSoup
import pandas as pd
import requests
from market_research.tools import WebDriver


class Amazon():
    def __init__(self, webdriver_path: str, browser_path: str=None, enable_headless=True):
        self.web_driver = WebDriver(executable_path=webdriver_path, browser_path=browser_path, headless=enable_headless)
        self.wait_time = 1


    def get_allcomments(self,url:str="https://www.amazon.com/Sony-QD-OLED-7-1-4ch-Theater-Speaker/product-reviews/B0CBDJKR1V/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews",
                        maker=None, product=None) -> list:

        allcomments_list = []
        page = 0
        last_comment=None
        while True:
            page +=1
            driver = self.web_driver.get_chrome()
            page_url =  f"{url}&pageNumber={page}".lower()
            print(f"connecting to {page_url}")
            driver.get(page_url)
            time.sleep(self.wait_time)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            allcomments_list.extend(self._get_comments(soup=soup, url=url, maker=maker, product=product))
            driver.quit()
            print(f"ppp: {allcomments_list[-1]['Comments']}")
            try:
                if last_comment is not None:
                    print(f"last_comment1: {last_comment}")
                    print(f"last_comment2: {allcomments_list[-1]['Comments']}")
                    print(last_comment == allcomments_list[-1]['Comments'])
                    if last_comment == allcomments_list[-1]['Comments']:
                        break
                    else:
                        last_comment = allcomments_list[-1]['Comments']
            except Exception as e:
                print("error")
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


