import pandas as pd

from market_research import SONYSPEC, SONYSPEC_JP, PANASONICSPEC
from market_research.tools import FileManager
from datetime import date
import platform
os_name = platform.system()

webdriver_path = "./chromedriver/chromedriver.exe"
browser_path = "./chrome/chrome.exe"
# 현재 운영체제 확인

if os_name == "Linux":
    webdriver_path = "/workspace/research-market-tv/chromedriver/chromedriver"
    browser_path = "/workspace/research-market-tv/chrome/chrome"
else:
    print("알 수 없는 운영체제입니다.")

enable_headless = True

mss = SONYSPEC(webdriver_path = webdriver_path, browser_path=browser_path, enable_headless=enable_headless)
dict_models = mss.get_models_info()

df_models = pd.DataFrame.from_dict(dict_models)
df_models.to_pickle('df_models.pkl')
loaded_df_models = pd.read_pickle('df_models.pkl')


# file_name = f"sony_model_info_web_{date.today().strftime('%Y-%m-%d')}"
# FileManager.dict_to_excel(dict_models, file_name=file_name, sheet_name="global")
#
# mssjp = SONYSPEC_JP(webdriver_path = webdriver_path, browser_path=browser_path, enable_headless=enable_headless)
# dict_models = mssjp.get_models_info()
# file_name = f"sony_jp_model_info_web_{date.today().strftime('%Y-%m-%d')}"
# FileManager.dict_to_excel(dict_models, file_name=file_name, sheet_name="jp")
#
#
#
# mspjp = PANASONICSPEC(webdriver_path = webdriver_path, browser_path=browser_path, enable_headless=enable_headless)
# dict_models = mspjp.get_models_info()
# file_name = f"pana_jp_model_info_web_{date.today().strftime('%Y-%m-%d')}"
# FileManager.dict_to_excel(dict_models, file_name=file_name, sheet_name="global")
#
#
#
