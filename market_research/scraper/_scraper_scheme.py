from abc import ABC, abstractmethod
import pandas as pd
from pathlib import Path
from datetime import date
from tools.web import WebDriver
import logging
import subprocess
import os
import logging





class Scraper(ABC):

    def __init__(self, use_web_driver=True, export_prefix:str="scraper", intput_folder_path :str= "input", output_folder_path:str="results"):
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
        if use_web_driver:
            self.web_driver = WebDriver(headless=True)
        else: #playwright 설치치
            # 쉘 스크립트 내용
            shell_script_content = """
            playwright install
            """

            script_file_path = "set_chrome.sh"
            with open(script_file_path, "w") as script_file:
                script_file.write(shell_script_content)

            # 쉘 스크립트 실행
            result = subprocess.run(["bash", script_file_path], capture_output=True, text=True)

            # 쉘 스크립트 파일 삭제 (선택 사항)
            os.remove(script_file_path)

            if result.returncode == 0:
                logging.info("finish playwright installing.")
            else:
                logging.error(f"occured error: {result.stderr}")

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

    """
    동기/비동기 여부 상관없이 메서드 이름만 강제.
    """

    required_methods = [
        "fetch_model_data",
        "_get_series_urls",
        "_extract_models_from_series",
        "_extract_model_details",
        "_extract_global_specs",
    ]

    def __init_subclass__(cls):
        for method_name in cls.required_methods:
            if not hasattr(cls, method_name):
                raise TypeError(f"{cls.__name__} is missing required method: {method_name}")



