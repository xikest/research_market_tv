from bs4 import BeautifulSoup
import time
from tqdm import tqdm
import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from tools.file import FileManager
from market_research.scraper._scraper_scheme import Scraper, Modeler, CustomException
from market_research.scraper.models.visualizer.data_visualizer import DataVisualizer
import logging

class ModelScraper_s(Scraper, Modeler, DataVisualizer):
    def __init__(self, enable_headless=True,
                 export_prefix="sony_model_info_web", intput_folder_path="input", output_folder_path="results",
                 wait_time=1):
        Scraper.__init__(self, enable_headless, export_prefix, intput_folder_path, output_folder_path)
        self.wait_time = wait_time
        pass
    
    def fetch_model_data(self) -> pd.DataFrame:
        def find_urls() -> dict:
            url_set = set()
            url_series_set = self._get_series_urls()
            for url in url_series_set:
                url_models_set = self._extract_models_from_series(url=url)
                url_set.update(url_models_set)
            url_dict = {idx: url for idx, url in enumerate(url_set)}
            logging.info(f"Total model: {len(url_dict)}")
            return url_dict
        
        def extract_specs(url_dict):
            dict_models = {}
            for key, url in tqdm(url_dict.items()):
                try:
                    dict_info = self._extract_model_details(url)
                    dict_models[key] = dict_info
                    dict_spec = self._extract_global_specs(url=url)
                    dict_models[key].update(dict_spec)
                    dict_models['url'] = url
                except Exception as e:
                    pass
            return dict_models
        
        def transform_format(dict_models, json_file_name: str) -> pd.DataFrame:
            df_models = pd.DataFrame.from_dict(dict_models).T
            df_models = df_models.dropna(subset=['price'])
            df_models.to_json(self.output_folder / json_file_name, orient='records', lines=True)
            return df_models
        
        
        logging.info("start collecting data")
        url_dict = find_urls()
        dict_models = extract_specs(url_dict)
        df_models = transform_format(dict_models, json_file_name="s_scrape_model_data.json")
            
        FileManager.df_to_excel(df_models.reset_index(), file_name=self.output_xlsx_name)
        return df_models
    
    @Scraper.try_loop(2)
    def _get_series_urls(self) -> set:
        def find_series_urls(url:str, prefix:str) -> set:
            logging.info(f"Starting to scrape series URLs from: {url}")
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
                        elements = soup.find_all('a', class_="custom-product-grid-item__image-container")
                        for element in elements:
                            url_series.add(prefix + element['href'].strip())
                        driver.execute_script(f"window.scrollBy(0, {step});")
                        time.sleep(self.wait_time)
                        scroll_distance += step
                return url_series
            except Exception as e:
                logging.error(f"{e}")
                pass
            finally:
                driver.quit()                  
        url_series = find_series_urls(url = "https://electronics.sony.com/tv-video/televisions/c/all-tvs/", prefix = "https://electronics.sony.com/")
        logging.info(f"The website scan has been completed.\ntotal series: {len(url_series)}")
        for i, url in enumerate(url_series, start=1):
            logging.info(f"Series: [{i}] {url.split('/')[-1]}")
        return url_series
    
    @Scraper.try_loop(2)
    def _extract_models_from_series(self, url: str) -> set:
        
        def extract_model_url(driver)->set:
            url_models_set= set()
            try: 
                element = driver.find_element(By.CLASS_NAME,
                                               'custom-variant-selector__body')
                url_elements = element.find_elements(By.TAG_NAME, 'a')
                for url_element in url_elements:
                    url = url_element.get_attribute('href')
                    url_models_set.add(url.strip())

                return url_models_set
            except:
                logging.error("error extract_models_from_series")
                return None
        
        url_models_set = set()
        try:
            driver = self.set_driver(url)
            url_models_set = extract_model_url(driver)
        except CustomException as e:
            logging.error(f"error_extract_models_from_series: {url}")
            pass
        finally:
            driver.quit()
        return url_models_set
            
    @Scraper.try_loop(2)
    def _extract_model_details(self, url: str) -> dict:
        
        def extract_model(driver):
            model = driver.find_element(By.XPATH,
                                        '//*[@id="cx-main"]/app-product-details-page/div/app-custom-product-intro/div/div/div[1]/div/span').text

            model = model.split(":")[-1].strip()
            return {"model": model}
        
        def extract_description(driver)->dict:
            try:
                description = driver.find_element(By.XPATH,
                                                    '//*[@id="cx-main"]/app-product-details-page/div/app-custom-product-intro/div/div/div[1]/h1/p').text
            except:
                description = ""
            return {"description": description}
        
        def extract_prices(driver)->dict:
            prices_dict = dict()
            try:
                price_now = driver.find_element(By.XPATH,
                                                '//*[@id="PDPOveriewLink"]/div[1]/div/div/div[2]/div/app-custom-product-summary/app-product-pricing/div/div[1]/p[1]').text
                price_original  = driver.find_element(By.XPATH,
                                                        '//*[@id="PDPOveriewLink"]/div[1]/div/div/div[2]/div/app-custom-product-summary/app-product-pricing/div/div[1]/p[2]').text

                price_now = float(price_now.replace('$', '').replace(',', ''))
                price_original = float(price_original.replace('$', '').replace(',', ''))
                price_gap = price_original - price_now
                
                prices_dict['price'] = price_now
                prices_dict['price_original'] = price_original
                prices_dict['price_gap'] = round(price_gap, 1)

            except:
                try:
                    price_now = driver.find_element(By.XPATH,
                                                    '//*[@id="PDPOveriewLink"]/div[1]/div/div/div[2]/div/app-custom-product-summary/app-product-pricing/div/div[1]/p').text
                    
                    price_now = float(price_now.replace('$', '').replace(',', ''))
                    prices_dict['price'] = price_now
                    prices_dict['price_original'] = price_now
                    prices_dict['price_gap'] = 0.0
                except:
                    prices_dict['price'] = float('nan')
                    prices_dict['price_original'] = float('nan')
                    prices_dict['price_gap'] = float('nan')
            return prices_dict
        
        def extract_info_from_model(model: str)->dict:
            dict_info = {}
            model = model.lower()
            dict_info["model"] = model
            dict_info["year"] = model.split("-")[1][-1]
            dict_info["series"] = model.split("-")[1][2:]
            dict_info["size"] = model.split("-")[1][:2]
            dict_info["grade"] = model.split("-")[0]
                
            year_mapping = {
                'l': "2023",
                'k': "2022",
                'j': "2021",
            }

            dict_info["year"] = year_mapping.get(dict_info.get("year"), "2024")

            return dict_info
        
        dict_info = {}

        logging.info(f"Connecting to {url.split('/')[-1]}: {url}")
        try:
            driver = self.set_driver(url)
            
            # Extract model
            dict_info.update(extract_model(driver))
            dict_info.update(extract_description(driver))
            dict_info.update(extract_prices(driver))
            dict_info.update(extract_info_from_model(dict_info.get("model")))
            logging.info(dict_info)
            return dict_info
        except CustomException as e:
            logging.error(f"error_extract_model_details: {url}")
            pass
        finally:
            driver.quit()
    
    
    @Scraper.try_loop(5)
    def _extract_global_specs(self, url: str) -> dict:
        
        def find_emphasize_text(driver) -> None:
            time.sleep(self.wait_time)
            see_more_features = False
            for i in range(10):
                try:
                    self.remove_popup(driver)
                    see_more_features = driver.find_element(By.CLASS_NAME, 'see_more_features_button.container')
                except:               
                    if i == 9:
                        logging.error("error find_emphasize_text")
                    ActionChains(driver).key_down(Keys.PAGE_DOWN).perform()
                    pass

            self.web_driver.move_element_to_center(see_more_features)
            see_more_features.click()
            time.sleep(self.wait_time)
            
        def extract_emphasize_text(driver) -> dict:
            
            def remove_txt_group(text_list, text_gr = ["picture", "sound", "design", "smart", "gaming", "eco"]):
                i = 0
                while i <= len(text_list) - len(text_gr):
                    if text_list[i:i+len(text_gr)] == text_gr:
                        del text_list[i:i+len(text_gr)]
                    else:
                        i += 1
                return text_list
            
            text_list = []
            text_dict = {}
            
            text_elements = driver.find_elements(By.CLASS_NAME, 'custom-product-features__components')
            for text_element in text_elements:
                elements = text_element.find_elements(By.XPATH, ".//h2 | .//p")
                
                for elem in elements:
                    text = elem.text.strip().lower()
                    if text == '':
                        continue
                    text_list.append(text)
            
            text_grs = [['sound', 'smart', 'gaming', 'design', 'eco'],
                        ["picture", "sound", "design", "smart", "gaming", "eco"]]
            for text_gr in text_grs:        
                text_list = remove_txt_group(text_list, text_gr)
    
            check_inx_dict={'picture':'all features',
                            "xr picture" :"xr sound",
                            "picture & sound" : 'all features'}
            for check_key, check_value in check_inx_dict.items():
                first_idx = None
                last_idx = None
                for i, text in enumerate(text_list):
                    if text == check_key and last_idx is None:
                        first_idx = i+1
                    if text == check_value and first_idx is not None:
                        last_idx = i  
                        break  
                if first_idx is not None and last_idx is not None:
                  break  

            text_list = text_list[first_idx:last_idx]
            for i, text in enumerate(text_list):
                text_dict[f'text{i}'] = text
            return text_dict
        
        def find_spec_tab(driver) -> None:
            
            def find_element_spec(driver) -> None:
                element_spec = driver.find_element(By.XPATH, '//*[@id="PDPSpecificationsLink"]')
                self.web_driver.move_element_to_center(element_spec)
                time.sleep(self.wait_time)
                return None
                
            def find_click_spec(driver) -> None:
                element_click_spec = driver.find_element(By.XPATH, '//*[@id="PDPSpecificationsLink"]/cx-icon')
                element_click_spec.click()
                time.sleep(self.wait_time)
                return None
            
            def act_click_see_more(driver):
                self.remove_popup(driver)
                try:
                    element_see_more = driver.find_element(By.XPATH,'//*[@id="cx-main"]/app-product-details-page/div/app-product-specification/div/div[2]/div[3]/button')
                    self.web_driver.move_element_to_center(element_see_more)
                    element_see_more.click()
                    logging.debug("Clicked the 'see more' button from the first locator.")
                except Exception as e:
                    logging.error(f"Cannot find the 'see more' button from the first locator: {e}")
                    try:
                        element_see_more = driver.find_element(By.XPATH, '//*[@id="cx-main"]/app-product-details-page/div/app-product-specification/div/div[2]/div[2]/button')
                        self.web_driver.move_element_to_center(element_see_more)
                        element_see_more.click()
                        logging.debug("Clicked the 'see more' button from the second locator.")
                    except Exception as e:
                        logging.error(f"Cannot find the 'see more' button from the second locator: {e}")
                time.sleep(self.wait_time)
                return None
            
            find_element_spec(driver)
            find_click_spec(driver)
            act_click_see_more(driver)                
            return None
            
        def extract_specs_detail(driver) -> dict:
            def convert_soup_to_dict(soup):
                """
                Convert BeautifulSoup soup to dictionary.
                """
                try:
                    h4_tag = soup.find('h4').text.strip()
                    p_tag = soup.find('p').text.strip()
                except :
                    logging.warning("First level parsing error, attempting with empty 'p' tag")
                    try:
                        h4_tag = soup.find('h4').text.strip()
                        p_tag = ""
                    except Exception as e:
                        logging.error("Parser error", exc_info=e)
                        h4_tag = "Parser error"
                        p_tag = "Parser error"
                return h4_tag, p_tag
            
            dict_spec = {}
            driver.find_element(By.ID, "ngb-nav-0-panel").click()
            for _ in range(15):
                elements = driver.find_elements(By.CLASS_NAME,"full-specifications__specifications-single-card__sub-list")
                for element in elements:
                    soup = BeautifulSoup(element.get_attribute("innerHTML"), 'html.parser')
                    label, content  = convert_soup_to_dict(soup)
                    original_label = label
                    while label in dict_spec and dict_spec.get(label)!=content:
                        asterisk_count = label.count('*')
                        label = f"{original_label}{'*' * (asterisk_count + 1)}"
                    dict_spec[label] = content
                    logging.info(f"[{label}] {content}")
                ActionChains(driver).key_down(Keys.PAGE_DOWN).perform()

            return dict_spec
        
        dict_spec = {}

        try:
            driver = self.set_driver(url)
            find_emphasize_text(driver)   
            dict_spec.update(extract_emphasize_text(driver))

        except Exception as e:
            logging.error(f"Failed to get header text from {url}.")
            pass
        finally:
            driver.quit()
            
        try:
            driver = self.set_driver(url)  
            find_spec_tab(driver)   
            dict_spec.update(extract_specs_detail(driver))
            logging.info(f"Received information from {url}")
        except CustomException as e:
            pass
        finally:
            driver.quit()
            
        return dict_spec
        
    
    def remove_popup(self, driver) -> None:
        for _ in range(5):
            try:
                # 팝업 닫기 버튼을 기다렸다가 클릭
                close_button = driver.find_element(By.XPATH, '//*[@id="contentfulModalClose"]')
                close_button.click()
                break
            except Exception as e:
                pass
        return None 
    
    
    def set_driver(self, url):
        driver = self.web_driver.get_chrome()
        driver.get(url=url)
        time.sleep(self.wait_time)
        self.remove_popup(driver)
        return driver
        
            
