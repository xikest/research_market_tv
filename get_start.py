from modelspec.sony_model import SonyModelScraper
from modelspec.tools.functions import FileManager
from datetime import date

webdriver_path = "./chromedriver/chromedriver.exe"
enable_headless = True

sms = SonyModelScraper(webdriver_path = webdriver_path, enable_headless=enable_headless)
dict_models = sms.get_models_info()

file_name = f"sony_model_info_web_{date.today().strftime('%Y-%m-%d')}"
FileManager.dict_to_excel(dict_models, file_name=file_name, sheet_name="global")
# df_models.to_excel(fileName)# 엑셀 파일로 저장
