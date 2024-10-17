import time
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import re
from tqdm import tqdm
from tools.file import FileManager
from market_research.scraper._scraper_scheme import Scraper
from market_research.scraper.rtings.rvisualizer import Rvisualizer

class Rtings(Scraper, Rvisualizer):
    def __init__(self, enable_headless = True,
                         export_prefix= "rtings",
                         intput_folder_path = "input",
                         output_folder_path = "results", verbose:bool=False, wait_time=1):

        Scraper.__init__(self, enable_headless = enable_headless,
                         export_prefix= export_prefix,
                         intput_folder_path = intput_folder_path,
                         output_folder_path = output_folder_path)
                             
        self.verbose = verbose
        self.wait_time = wait_time
        pass
        
        
    def get_data(self, urls:any, export_excel=True):

        def _process_url(url:str, info_dict:dict, data_getter):
            def _add_info_columns(df, info_dict):
                return df.assign(
                    maker=info_dict.get("maker"),
                    year=info_dict.get("year"),
                    series=info_dict.get("series"),
                )
            df = data_getter(url)
            df = _add_info_columns(df, info_dict)
            return df

        scores_df = pd.DataFrame()
        measurement_df = pd.DataFrame()
        comments_df = pd.DataFrame()
        fail_url_list = []
        
        if isinstance(urls,list):
            url_list = urls
        elif isinstance(urls,dict):
            url_list = list(urls.keys())
             
        for url in tqdm(url_list):
            try:
                if self.verbose:
                    print(f"connecting to {url}")
                
                df = _process_url(url, urls.get(url), self._get_score)
                scores_df = pd.concat([scores_df, df], axis=0)

                df = _process_url(url, urls.get(url), self._get_measurement_reuslts)
                measurement_df = pd.concat([measurement_df, df], axis=0)

                df = _process_url(url, urls.get(url), self._get_comments)
                comments_df = pd.concat([comments_df, df], axis=0)

            except Exception as e:
                fail_url_list.append(url)
                if self.verbose:
                    print(f"fail {url}")
                    print(e)
                continue
            
        scores_df = scores_df.reset_index(drop=True)
        measurement_df = measurement_df.reset_index(drop=True)
        comments_df = comments_df.reset_index(drop=True)
        
        if fail_url_list:
            print(f"failed URL: {fail_url_list}")
        
        scores_df.to_json(self.output_folder / "rtings_scores_data.json", orient='records', lines=True)
        measurement_df.to_json(self.output_folder / "rtings_measurement_data.json", orient='records', lines=True)
        if export_excel:
            FileManager.df_to_excel(scores_df, file_name=self.output_xlsx_name, sheet_name="scores", mode='w')
            FileManager.df_to_excel(measurement_df, file_name=self.output_xlsx_name, sheet_name="measurement", mode='a')
            FileManager.df_to_excel(comments_df, file_name=self.output_xlsx_name, sheet_name="comments", mode='a')
                    
        return {
            "scores":scores_df,
                "measurement":measurement_df,
                "comments":comments_df
        }
        
        

    def _get_score(self, url:str="https://www.rtings.com/tv/reviews/sony/a95l-oled") :

        url = url.lower()
        driver = self.web_driver.get_chrome()
        driver.get(url)
        time.sleep(self.wait_time)     


        # scorecard-row-content 클래스를 가진 요소들을 선택
        elements = driver.find_elements(By.CLASS_NAME, "scorecard-row-content")
        try:
            score_dict = {}
            for element in elements:
                score_type = element.find_element(By.CLASS_NAME, 'scorecard-row-name').text.strip()
                score = element.find_element(By.CLASS_NAME, 'e-score_box-value ').text.strip()
                score_dict[score_type] = score

            rows = []
            for score_type, score in score_dict.items():
                rows.append({'category': score_type, 'score': score})
            scores_df = pd.DataFrame(rows)           
            scores_df['url'] = url
            return scores_df
        except Exception as e:
            if self.verbose:
                print(f"get specification error: {e}")
        finally:
            driver.quit()
            

    def _get_comments(self, url:str="https://www.rtings.com/tv/reviews/sony/a95l-oled", min_sentence_length = 0):
        """
        return dict or DataFrame

        """

        # Selenium을 사용하여 웹 드라이버 시작
        driver = self.web_driver.get_chrome()
        maker = url.split("/")[-2]
        product = url.split("/")[-1]
        url = url.lower()
        # url = url +"#page-comments"
        driver.get(url)
        time.sleep(self.wait_time)
        ## Load More 버튼 열기
        try:
            while True:
                try:
                    button_div = driver.find_element(By.CLASS_NAME, "comment_list-footer")
                    button = button_div.find_element(By.CLASS_NAME, "e-button")
                    button.click()
                    time.sleep(1)
                except:
                    break
            try:
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                comment_contents = soup.find_all('div', class_='comment_list-item-content e-discussion_content is-newest')
                comments_list = []

                for idx, comment_content in enumerate(comment_contents):
                    quote_controls = comment_content.find('div', class_='quote-controls')
                    if quote_controls:
                        quote_controls.decompose()
                    quote_content = comment_content.find('div', class_='quote-content')
                    if quote_content:
                        quote_content.decompose()
                    comment_text = comment_content.get_text(strip=True, separator='\n')
                    comment_text = re.sub(r'https?://\S+', '', comment_text)

                    # min_sentence_length 길이 이상의 문장만 분석
                    if len(comment_text.split()) >= min_sentence_length:
                        comments_list.append(
                            {'idx': idx, 'maker': maker, 'product': product, 'sentences': comment_text})
                comments_df = pd.DataFrame(comments_list).set_index("idx")
            finally:
                driver.quit()
        except:
            if self.verbose:
                print("no comment")
            comments_df = pd.DataFrame([{'idx': 0, 'maker': maker, 'product': product, 'sentences': "No data"}]).set_index("idx")
            comments_df['url'] = url
        return comments_df


    def _get_measurement_reuslts(self, url: str = "https://www.rtings.com/tv/reviews/sony/a95l-oled") ->pd.DataFrame:
        

        url = url.lower()
        driver = self.web_driver.get_chrome()
        driver.get(url)
        time.sleep(self.wait_time)
        page_source = driver.page_source
        driver.quit()
        soup = BeautifulSoup(page_source, 'html.parser')

        results_list = []
        category = ""

        test_groups = soup.find_all('div', class_='test_group e-simple_grid-item-2-pad')
        for test_group in test_groups:
            # test_group-category 텍스트 찾기
            header_element = test_group.find('div', class_='test_group-header')
            category_element = header_element.find('div', class_='test_group-category')
            if category_element:
                category = category_element.get_text(strip=True)
                category_element.extract()
            # span 태그 내의 텍스트 추출 및 '_'로 구분
            scores_headder = '(><)_'.join(header_element.stripped_strings)
            # test_value is-number 찾기
            test_values = test_group.find_all('div', class_='test_value is-number')
            # 리스트 초기화
            for test_value in test_values:
                # test_value-label과 test_result_value 찾기
                label = test_value.find('span', class_='test_value-label').get_text(strip=True)
                result_value = test_value.find('span',
                                               class_='test_result_value e-test_result review-value-score').get_text(strip=True)
                # 딕셔너리에 추가
                results_list.append([category, scores_headder, label, result_value])
            # 리스트를 데이터프레임으로 변환


        results_df = pd.DataFrame(results_list,
                                  columns=["category", "scores_header", "label", "result_value"])
        
        
        # scores_header_list 생성 및 수정
        scores_header_list = results_df.scores_header.map(lambda x: x.split("_"))

        scores_header_list_s = []
        for scores_header in scores_header_list:
           if len(scores_header) <2:
               scores_header_list_s.append(["(><)", scores_header[0]])
           else:
               scores_header_list_s.append([scores_header[0], scores_header[1]])

        # print(scores_header_list_s)

           # scores_header_df 생성
        scores_header_df = pd.DataFrame(scores_header_list_s, columns=["score", "header"])
        scores_header_df["score"] = scores_header_df["score"].map(lambda x:x.replace("(><)", ""))
        # results_df와 scores_header_df 병합
        results_df = pd.concat([results_df, scores_header_df], axis=1)
        results_df = results_df[["category", "header", "score", "label", "result_value"]]
        results_df['url'] = url
        return results_df
