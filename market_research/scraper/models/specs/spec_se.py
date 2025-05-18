from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import re
from market_research.scraper._scraper_scheme import Scraper, Modeler
from playwright.async_api import async_playwright
from tools.file import FileManager
import logging

class ModelScraper_se(Scraper):
    def __init__(self, 
                 export_prefix="sse_model_info_web", intput_folder_path="input", output_folder_path="results",
                 wait_time=1, verbose=False):
        Scraper.__init__(self, use_web_driver=False, export_prefix= export_prefix, intput_folder_path=intput_folder_path, output_folder_path=output_folder_path)
        self.wait_time = wait_time
        self.verbose = verbose
        
        self.json_file_name = "se_scrape_model_data.json"
        pass

    async def fetch_model_data(self) -> pd.DataFrame:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            print("start collecting data")
            url_dict = await self._find_urls(page)
            dict_models = await self._extract_all_specs(page, url_dict)
            await browser.close()
            df_models = self._transform_format(dict_models, self.json_file_name)
            FileManager.df_to_excel(df_models.reset_index(), file_name=self.output_xlsx_name)
            
            return df_models

    async def _find_urls(self, page) -> dict:
        url_set = set()
        url_series_set = await self._get_series_urls(page)


        for url in tqdm(url_series_set):
            models = await self._extract_models_from_series(page, url)
            url_set.update(models)

        url_dict = {idx: url for idx, url in enumerate(url_set)}
        print(f"Total model: {len(url_dict)}")
        return url_dict

    async def _get_series_urls(self, page) -> set:
        seg_urls = {
            "neo_qled": "https://www.samsung.com/us/televisions-home-theater/tvs/all-tvs/?technology=Samsung+Neo+QLED+8K,Samsung+Neo+QLED+4K",
            "oled": "https://www.samsung.com/us/televisions-home-theater/tvs/oled-tvs/",
            "the_frame": "https://www.samsung.com/us/televisions-home-theater/tvs/all-tvs/?technology=The+Frame",
            "qled": "https://www.samsung.com/us/televisions-home-theater/tvs/qled-4k-tvs/",
            "crystal_uhd_tvs": "https://www.samsung.com/us/televisions-home-theater/tvs/all-tvs/?technology=Crystal+UHD+TVs",
        }
        url_series = set()
        for seg, seg_url in seg_urls.items():
            await page.goto(seg_url)
            await page.wait_for_timeout(self.wait_time * 1000)
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            elements = soup.find_all('a', class_="StarReview-review-1813701344 undefined")
            urls = {f"https://www.samsung.com{a['href'].strip()}" for a in elements}
            url_series.update(urls)
            logging.info(f"List of collected series URLs: {url_series}")
        print(f"The website scan has been completed.\ntotal series: {len(url_series)}")
        return url_series

    async def _extract_models_from_series(self, page, url: str) -> set:
        await page.goto(url)
        await page.wait_for_timeout(self.wait_time * 1000)
        url_models_set = set()
        buttons = await page.query_selector_all('.SizeTile_details__09vrW')
        for btn in buttons:
            try:
                await btn.click()
                await page.wait_for_timeout(500)
                curr_url = page.url
                url_models_set.add(curr_url.strip())
            except:
                continue
        return url_models_set

    async def _extract_all_specs(self, page, url_dict: dict) -> dict:
        dict_models = {}
        for key, url in tqdm(url_dict.items()):
            try:
                model_info = await self._extract_model_details(page, url)
                global_specs = await self._extract_global_specs(page, url)
                global_specs['url'] = url
                model_info.update(global_specs)
                dict_models[key] = model_info
            except Exception as e:
                if self.verbose:
                    print(f"fail to collect: {url}")
                    print(e)
                continue
        return dict_models

    async def _extract_model_details(self, page, url: str) -> dict:
        await page.goto(url)
        await page.wait_for_timeout(self.wait_time * 1000)
        dict_info = {}

        try:

            label = await page.locator('.ModelInfo_modalInfo__Dlls0').inner_text()
            if self.verbose:
                print(f"After getting label text: {label}")
            logging.info(f"After getting label text: {label}")
            model = label.split()[-1]
            dict_info["model"] = model


            desc = await page.locator('.ProductTitle_product__KGKRj').inner_text()
            logging.info(f"After getting description text:{desc}")
            if self.verbose:
                print(f"After getting description text:{desc}")
            dict_info["description"] = desc

            price_text = await page.locator(".PriceInfoText_priceInfo__pAyUK").first.inner_text()
            split_price = re.split(r'[\n\s]+', price_text)
            if self.verbose:
                print(f"After getting price text:{price_text}")
            logging.info(f"After getting price text:{price_text}")

            prices = [float(p.replace('$', '').replace(',', '')) for p in split_price if '$' in p]
            dict_info["price"] = prices[0] if prices else None
            dict_info["price_original"] = prices[1] if len(prices) > 1 else prices[0]
            dict_info["price_gap"] = prices[2] if len(prices) > 2 else 0.0

            model_lower = model.lower()
            dict_info.update(self._parse_model_code(model_lower))
        except Exception as e:
            if self.verbose:
                print(f"Error extracting model from {url}: {e}")
        return dict_info

    async def _extract_global_specs(self, page, url: str) -> dict:
        dict_spec = {}
        try:
            await page.goto(url)
            await page.wait_for_timeout(self.wait_time * 1000)
            if self.verbose:
                await page.screenshot(path=f"screenshots/1.png", full_page=True)

            await page.click('[data-testid="#specs"]')
            await page.wait_for_timeout(self.wait_time * 1000)
            if self.verbose:
                await page.screenshot(path=f"screenshots/2.png", full_page=True)


            try:
                await page.get_by_text("See All Specs", exact=True).first.click()
                await page.wait_for_timeout(self.wait_time * 1000)
            except Exception as e:
                print(f"[오류] 'See All Specs' 클릭 실패: {e}")
            try:
                # 두 번째 백업: CSS 선택자를 이용
                btn = page.locator("a.Specs_expandBtn__TAtH7").first
                await btn.wait_for(state="visible", timeout=3000)
                await btn.click()
                await page.wait_for_timeout(self.wait_time * 1000)
            except Exception as e2:
                print(f"[오류] 백업 클릭도 실패: {e2}")



            if self.verbose:
                await page.screenshot(path=f"screenshots/3.png", full_page=True)
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")

            # 1. 일반 스펙 (name-value 쌍)
            for item in soup.find_all("div", class_=re.compile(r"^Specs_subSpecsItem_")):
                try:
                    name = item.find("div", class_=re.compile(r"^Specs_subSpecItemName_|^Specs_type-p2_"))
                    value = item.find("div", class_=re.compile(r"^Specs_subSpecsItemValue_|^Specs_type-p2_"))
                    if name and value:
                        dict_spec[name.text.strip()] = value.text.strip()
                        print(dict_spec[name.text.strip()])
                except Exception:
                    continue

            # 2. 상세 리스트 스펙 (.Specs_specDetailList__)
            for group in soup.find_all("ul", class_=re.compile(r"^Specs_specDetailList_")):
                try:
                    title_elem = group.find_previous("div", class_=re.compile(r"^Specs_specGroupName_"))
                    title = title_elem.get_text(strip=True) if title_elem else "Detail List"
                    items = [li.get_text(strip=True) for li in group.find_all("li") if li.get_text(strip=True)]
                    if items:
                        dict_spec[title] = ", ".join(items)
                        print(dict_spec[title])
                except Exception:
                    continue

            # 3. 요약 스펙 (.spec-highlight__container)
            for block in soup.find_all("div", class_=re.compile(r"^spec-highlight__container")):
                try:
                    name = block.find("div", class_=re.compile(r"^spec-highlight__title"))
                    value = block.find("div", class_=re.compile(r"^spec-highlight__value"))
                    if name and value:
                        dict_spec[name.text.strip()] = value.text.strip()
                        print(dict_spec[name.text.strip()]) 
                except Exception:
                    continue

        except Exception as e:
            if self.verbose:
                print(f"Spec extraction failed from {url}: {e}")
        return dict_spec

    def _transform_format(self, dict_models, json_file_name: str) -> pd.DataFrame:
        df = pd.DataFrame.from_dict(dict_models).T
        df = df.drop(['Series'], axis=1, errors='ignore')
        df = df.rename(columns={'Type': 'display type'})
        df = df.dropna(subset=['price'])

        try:
            valid = df['Color*'].dropna().index
            df.loc[valid, 'Color'] = df.loc[valid, 'Color*']
        except:
            pass

        df.to_json(self.output_folder / json_file_name, orient='records', lines=True)
        return df

    def _parse_model_code(self, model: str) -> dict:
        def extract_grade_model(model):
            return model[:2], model[2:-4]

        def extract_size_model(model):
            match = re.match(r'\d+', model)
            if match:
                size = match.group()
                rest = model[len(size):]
                return size, rest
            return None, model

        def extract_year_series(model, grade):
            mapping = {
                'qn': {'t': "2021", 'b': "2022", 'c': "2023", 'd': "2024", 'e': "2025"},
                'un': {'c': "2023", 'd': "2024", 'e': "2025"},
            }
            year = "na"
            series = model
            if "qn" in grade:
                match = re.search(r'([A-Za-z]+\d+)([A-Za-z]+)', model)
                if match:
                    year_char = match.group(2)[0]
                    year = mapping.get('qn', {}).get(year_char, "na")
                    series = match.group(1) + year_char
            elif "un" in grade:
                year_char = model[0]
                year = mapping.get('un', {}).get(year_char, "na")
                series = model
            return year, series

        info = {}
        grade, model = extract_grade_model(model)
        size, model = extract_size_model(model)
        year, series = extract_year_series(model, grade)
        info.update({"grade": grade, "size": size, "year": year, "series": series})
        return info


