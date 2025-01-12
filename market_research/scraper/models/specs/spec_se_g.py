from bs4 import BeautifulSoup
import time
import pandas as pd
from tqdm import tqdm
import re
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from market_research.scraper._scraper_scheme import Scraper, Modeler
from tools.file import FileManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class ModelScraper_se_g(Scraper, Modeler):
    def __init__(self, enable_headless=True,
                 export_prefix="sse_model_info_web", intput_folder_path="input", output_folder_path="results",
                 wait_time=1, verbose=False):
        Scraper.__init__(self, enable_headless, export_prefix, intput_folder_path, output_folder_path)
        self.wait_time = wait_time
        self.verbose = verbose
        pass
    
    def fetch_model_data(self) -> pd.DataFrame:        
        def find_urls() -> dict:
            url_set = set()
            url_series_set = self._get_series_urls()

            
            for url in tqdm(url_series_set):
                url_models_set = self._extract_models_from_series(url=url)
                url_set.update(url_models_set)

            url_dict = {idx: url for idx, url in enumerate(url_set)}
            print(f"Total model: {len(url_dict)}")
            return url_dict
        
        def extract_sepcs(url_dict):
            dict_models = {}
            for key, url in tqdm(url_dict.items()):
                try:
                    dict_info = self._extract_model_details(url)
                    dict_models[key] = dict_info
                    dict_spec = self._extract_global_specs(url=url)
                    dict_spec['url'] = url
                    dict_models[key].update(dict_spec)
                except Exception as e:
                    if self.verbose:
                        print(f"fail to collect: {url}")
                        print(e)
                    pass
            return dict_models
        
        def transform_format(dict_models, json_file_name: str) -> pd.DataFrame:
            df_models = pd.DataFrame.from_dict(dict_models).T
            df_models = df_models.rename(columns={'Type':'display type'})
            df_models = df_models.dropna(subset=['price'])
            df_models.to_json(self.output_folder / json_file_name, orient='records', lines=True)
            return df_models
        print("start collecting data")
        url_dict = find_urls()
        dict_models = extract_sepcs(url_dict)
        
        df_models = transform_format(dict_models, json_file_name="se_g_scrape_model_data.json")
            
        FileManager.df_to_excel(df_models.reset_index(), file_name=self.output_xlsx_name)
        return df_models
    
    @Scraper.try_loop(2)
    def _get_series_urls(self) -> set:

        def extract_urls_from_segments():
            seg_urls = {
                "gaming_price_under200":"https://www.samsung.com/us/computing/monitors/gaming/?technology=Gaming&price=Under+%24200",
                "gaming_price_200to500":"https://www.samsung.com/us/computing/monitors/gaming/?technology=Gaming&price=%24200+-+%24500",
                "gaming_price_over500":"https://www.samsung.com/us/computing/monitors/gaming/?price=Over+%24500&technology=Gaming",
                "featured_gaming_monitors": "https://www.samsung.com/us/computing/monitors/gaming/?technology=Featured-gaming-monitors"
                }
            url_series = set()
            
            for seg, seg_url in seg_urls.items():
                urls=find_series_urls(seg_url, prefix = "https://www.samsung.com")
                url_series.update(urls)
            return url_series   
        

                
        def find_series_urls(url:str, prefix:str) -> set:
        
            print(f"Starting to scrape series URLs from: {url}")
            prefix = "https://www.samsung.com"
            url_series = set()
            url = url
            prefix = prefix
            step = 200

            try:
                driver = self.set_driver(url)
                scroll_distance_total = self.web_driver.get_scroll_distance_total()
                scroll_distance = 0
                
                while scroll_distance < scroll_distance_total:
                    for _ in range(2):
                        html = driver.page_source
                        soup = BeautifulSoup(html, 'html.parser')
                        elements = soup.find_all('a', class_="StarReview-review-1813701344 undefined")
                        for element in elements:
                            url_series.add(prefix + element['href'].strip())
                        driver.execute_script(f"window.scrollBy(0, {step});")
                        time.sleep(self.wait_time)
                        scroll_distance += step
                        tt= url.split('/')[-1]
                        driver.save_screenshot(f'ss/{tt}distance{scroll_distance}.png')    
                    
                        
                return url_series
            except Exception as e:
                if self.verbose:
                    print(f"error find_series_urls: {e}")
                pass
            finally:
                driver.quit()
               
        url_series = extract_urls_from_segments()

        print(f"The website scan has been completed.\ntotal series: {len(url_series)}")
        for i, url in enumerate(url_series, start=1):
            print(f"Series: [{i}] {url.split('/')[-2]}")
        return url_series
    
    @Scraper.try_loop(2)
    def _extract_models_from_series(self, url: str) -> set:
        
        def extract_url(url, XPATH = '//*[@id="details"]/div[2]/div[3]/div[2]/div[8]/div[1]/div[2]/div[2]') -> set:
            url_series_set= set()
            url_series_set.add(url)
            driver = self.set_driver(url)
            try:
                sereis_element = driver.find_elements(By.XPATH, XPATH)
                for element in sereis_element:
                    a_tags = element.find_elements(By.TAG_NAME, 'a')  
                    for a_tag in a_tags:
                        href = a_tag.get_attribute('href')  
                        if href:
                            href = href.strip()
                            url_series_set.add(href)
            except Exception as e:
                print(e)
            finally:
                driver.quit()              
                return url_series_set

        
        try: 
            url_models_set = set()
            series_url_set = extract_url(url,
                                         '//*[@id="details"]/div[2]/div[3]/div[2]/div[8]/div[1]/div[2]/div[2]')
            # print(f"series_url_set {len(series_url_set)}")
            for series_url in series_url_set:      
                url_models =  extract_url(series_url, 
                                              '//*[@id="details"]/div[2]/div[3]/div[2]/div[8]/div[1]/div[3]/div[2]')
                
                # if self.verbose:
                    # print(f"url_models of :{series_url}")
                    # print(f"url_models: {len(url_models)}")
                    # print(url_models)
                url_models_set.update(url_models)
        except Exception as e:
            if self.verbose:
                print(f"error_extract_models_from_series {url}")
        
        # if self.verbose:
            # print(url_models_set)
        return url_models_set
            
    @Scraper.try_loop(5)
    def _extract_model_details(self, url: str='') -> dict:
    
        def extract_model(driver):
            try:
                label_element = driver.find_element(By.XPATH,'//*[@id="details"]/div[2]/div[3]/div[2]/div[1]/div[1]/strong[2]')
                label = label_element.text
                model = label.split()[-1]
            except:
                try:
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    label = soup.find('span', {'data-testid': 'atom_label'}).text.strip()
                    model = label.split('/')[-1].strip()
                except:
                    try:
                         title = driver.title
                         model = title.split('|')[0].split('-')[-1].strip()
                    except Exception as e:
                        if self.verbose:
                            print(e)
            return {"model": model}
            
        def extract_description(driver)->dict: 
            try:
                description = driver.find_element(By.XPATH,'//*[@id="details"]/div[2]/div[3]/div[2]/h1').text    

            except:
                soup = BeautifulSoup(driver.page_source, 'html.parser')

                try:
                    description = soup.find('div', class_='ProductTitle_product__q2vDb').text.strip()
                    description = description.split('/')[-1].strip()
                except:
                    try:
                         title = driver.title
                         description = title.split('-')[0].strip()
                    except Exception as e:
                        if self.verbose:
                            print(e)
                    
                    
            description = description.replace('"', "'") 
            return {"description": description}
             
        def extract_prices(driver) -> dict:
            prices_dict = {}
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            try:
                price_info = soup.find('div', class_='PriceInfoText_priceInfo__QEjy8')
                price_now = float(price_info.find('b').text.strip().replace('$', '').replace(',', ''))
                price_original = price_now  
                strike_tag = price_info.find('strike')
                if strike_tag and strike_tag.text.strip():
                    price_original = float(strike_tag.text.strip().replace('$', '').replace(',', ''))
            except:
                try:
                    price_info = soup.find('span', class_='product-top-nav__font-desc noRecycle noTradein noNEO')
                    price_now = float(price_info.find('span', class_='epp-price price-color').text.strip().replace('$', '').replace(',', ''))
                    price_original = price_now  
                except Exception as e:
                    print(e)
                
            prices_dict["price"] = price_now
            prices_dict["price_original"] = price_original
            prices_dict["price_gap"] = price_original - price_now
            return prices_dict
            
        def extract_info_from_model(model: str)->dict:
            model = model.lower()  # 대소문자 구분 제거
            dict_info = {}

            # 연도 매핑
            year_mapping =  {'a': "2021",
                            'b': "2022",
                            'c': "2023",
                            'd': "2024"}
            dict_info["size"] = model[2:4]
            dict_info["year"] = model[4]
            dict_info["grade"] = model[:2]
            dict_info["series"] = model[1:8]
            dict_info["year"] = year_mapping.get(dict_info.get("year"), "0000")
            return dict_info
        
        dict_info = {}
        if self.verbose:
            print(f"Connecting to {url.split('/')[-2]}: {url}")
        logging.info(f"Connecting to {url.split('/')[-2]}: {url}")
        try: 
            driver = self.set_driver(url)
            
            # Extract model
            dict_info.update(extract_model(driver))
            dict_info.update(extract_description(driver))
            dict_info.update(extract_prices(driver))
            dict_info.update(extract_info_from_model(dict_info.get("model")))
            if self.verbose: 
                print(dict_info)
            logging.info(dict_info)
            
            
        except Exception as e:
            if self.verbose:
                print(f"error_extract_model_details: {url}")
                print(e)
            logging.error(f"error_extract_model_details: {url}")
            pass
        finally:
            if driver:  
                driver.quit()    
        return dict_info


    @Scraper.try_loop(3)
    def _extract_global_specs(self, url: str) -> dict:
        def find_spec_tab(driver) -> None:
            try: 
                # JavaScript로 'Specs' 링크 클릭
                driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "#specsLink"))
                
                # 'See All Specs' 버튼 클릭
                driver.execute_script("arguments[0].click();", driver.find_element(By.CSS_SELECTOR, ".keyboard_navigateable.tl-btn-expand.Specs_expandBtn__0BNA_"))
                
                time.sleep(self.wait_time)
            except:
                try:
                    driver.execute_script("arguments[0].click();", driver.find_element(By.CSS_SELECTOR, "a[href='#specs']"))
                    # 'See All Specs' 버튼 클릭
                    driver.execute_script("arguments[0].click();", driver.find_element(By.CLASS_NAME, "tl-btn-expand"))
                
                except Exception as e :
                    if self.verbose:
                        print(f"error find_spec_tab {e}")
                    pass
                    time.sleep(self.wait_time)
                    
            return None 

        def extract_spec_detail(driver) -> dict:  
            dict_spec = {}
            try:
                table_elements = driver.find_elements(By.CLASS_NAME, "subSpecsItem.Specs_subSpecsItem__acKTN")
            except:
                try:
                    table_elements = driver.find_elements(By.CLASS_NAME, "Specs_specRow__e9Ife.Specs_specDetailList__StjuR")
                except:
                    try:
                        table_elements = driver.find_elements(By.CLASS_NAME, "spec-highlight__container")
                    except Exception as e:
                        print(f"error extract_spec_detail_click {e}")

            for element in table_elements:
                try:
                    item_name = element.find_element(By.CLASS_NAME, 'Specs_subSpecItemName__IUPV4').text
                    item_value = element.find_element(By.CLASS_NAME, 'Specs_subSpecsItemValue__oWnMq').text
                except:
                    try:
                        item_name = element.find_element(By.CLASS_NAME, 'Specs_subSpecItemName__IUPV4.Specs_type-p2__s07Sd').text
                        item_value = element.find_element(By.CLASS_NAME, 'Specs_type-p2__s07Sd.Specs_subSpecsItemValue__oWnMq').text 
                    except:
                        try:
                            item_name = element.find_element(By.CLASS_NAME, "spec-highlight__title").text
                            item_value = element.find_element(By.CLASS_NAME, "spec-highlight__value").text 
                        except Exception as e:
                            print(f"error extract_spec_detail_table {e}")  

                label = re.sub(r'[\n?]', '', item_name)
                content = re.sub(r'[\n?]', '', item_value)
                original_label = label
                while label in dict_spec and dict_spec.get(label)!=content:
                    asterisk_count = label.count('*')
                    label = f"{original_label}{'*' * (asterisk_count + 1)}"
                dict_spec[label] = content
                if self.verbose: 
                    if label == "" and content == "":
                        print(f"[{label}] {content}")
            return dict_spec
    
        dict_spec = {}
        try:
            driver = self.set_driver(url)
            find_spec_tab(driver)
            dict_spec = extract_spec_detail(driver)
            
            if self.verbose:
                print(f"Received information from {url}")
            logging.info(f"Received information from {url}")
        except Exception as e:
            print(f"error extract_specs_detail from {url}")
            pass
        finally:
            driver.quit()  
        return dict_spec



    def set_driver(self, url):
        driver = self.web_driver.get_chrome()
        driver.get(url=url)
        time.sleep(self.wait_time)
        return driver