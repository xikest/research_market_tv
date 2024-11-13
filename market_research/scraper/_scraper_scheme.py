from abc import ABC, abstractmethod
import pandas as pd
from pathlib import Path
from datetime import date
from tools.web import WebDriver
import logging

class Scraper(ABC):

    def __init__(self, enable_headless=True, export_prefix:str="scraper", intput_folder_path = None, output_folder_path=None):
        """
        enable_headless=True,
        export_prefix:str="scaper",
        intput_folder_path = "input",
        output_folder_path="results"
        """
        self.intput_folder:Path
        self.output_folder:Path
        self.output_xlsx_name = None
        self._initialize_data_paths(export_prefix=export_prefix, intput_folder_path=intput_folder_path, output_folder_path=output_folder_path)
        self.web_driver = WebDriver(headless=enable_headless)
        logging.info("initialized web driver")
        self.wait_time = 1

    def _initialize_data_paths(self,export_prefix:str=None, intput_folder_path:str=None, output_folder_path:str=None):
        if intput_folder_path is not None:
            self.intput_folder = Path(intput_folder_path)  # 폴더 이름을 지정
            if not self.intput_folder.exists():
                self.intput_folder.mkdir(parents=True, exist_ok=True)

        if output_folder_path is not None:
            self.output_folder = Path(output_folder_path)
            if not self.output_folder.exists():
                self.output_folder.mkdir(parents=True, exist_ok=True)
            if export_prefix is not None:
                self.output_xlsx_name = self.output_folder /  f"{export_prefix}{date.today().strftime('%Y-%m-%d')}.xlsx"
            else:
                self.output_xlsx_name = self.output_folder / f"{date.today().strftime('%Y-%m-%d')}.xlsx"
            
            
              
    @staticmethod
    def try_loop(try_total):
        def decorator(func):
            def wrapper(*args, **kwargs):
                for cnt_try in range(try_total):
                    try:
                        return func(*args, **kwargs)  # 인스턴스 메서드 여부와 관계없이 호출
                    except Exception as e:
                        if cnt_try + 1 == try_total:
                            print(f"Error after {try_total} attempts: {e}")
                        continue  # 다음 시도로 넘어감
            return wrapper
        return decorator


class Modeler(ABC):

    @abstractmethod
    def fetch_model_data(self, demo_mode: bool = False) -> pd.DataFrame:
        """
        Collect model information from URLs and return the data in the desired format.
        """
        pass

    @abstractmethod
    def _get_series_urls(self) -> set:
        """
        Get the series URLs by scrolling down the main page.
        """
        pass

    @abstractmethod
    def _extract_models_from_series(self, url: str) -> dict:
        """
        Extract all model URLs from a given series URL.
        """
        pass

    @abstractmethod
    def _extract_model_details(self, url: str) -> dict:
        """
        Extract model information (name, price, description) from a given model URL.
        """
        pass

    @abstractmethod
    def _extract_global_specs(self, url: str) -> dict:
        """
        Extract global specifications from a given model URL.
        """
        pass



class CustomException(Exception):
    def __init__(self, message:str=""):
        super().__init__(message) 

