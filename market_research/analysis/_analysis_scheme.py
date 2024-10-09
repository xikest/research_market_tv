from pathlib import Path
from datetime import date


class Analysis:
    def __init__(self,  export_prefix:str="scraper", intput_folder_path = None, output_folder_path=None):
        self.intput_folder:Path
        self.output_folder:Path
        self.output_xlsx_name = None
        self.set_data_path(export_prefix=export_prefix, intput_folder_path=intput_folder_path, output_folder_path=output_folder_path)


    def set_data_path(self, export_prefix: str = None, intput_folder_path: str = None, output_folder_path: str = None):
        # 현재 작업 디렉토리 경로
        current_folder = Path.cwd()

        if intput_folder_path is not None:
            self.intput_folder = Path(intput_folder_path)  # 폴더 이름을 지정
            if not self.intput_folder.exists():
                try:
                    self.intput_folder.mkdir(parents=True, exist_ok=True)
                except PermissionError:
                    print(f"PermissionError: '{intput_folder_path}'에 접근할 수 없습니다. 현재 폴더로 설정합니다.")
                    self.intput_folder = current_folder  # 현재 폴더로 설정

        if output_folder_path is not None:
            self.output_folder = Path(output_folder_path)
            if not self.output_folder.exists():
                try:
                    self.output_folder.mkdir(parents=True, exist_ok=True)
                except PermissionError:
                    print(f"PermissionError: '{output_folder_path}'에 접근할 수 없습니다. 현재 폴더로 설정합니다.")
                    self.output_folder = current_folder  # 현재 폴더로 설정
            if export_prefix is not None:
                self.output_xlsx_name = self.output_folder / f"{export_prefix}{date.today().strftime('%Y-%m-%d')}.xlsx"
            else:
                self.output_xlsx_name = self.output_folder / f"{date.today().strftime('%Y-%m-%d')}.xlsx"