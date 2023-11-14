from modelspec.tools import FileManager
from datetime import date

webdriver_path = "../chromedriver/chromedriver.exe"
browser_path = "../chrome/chrome.exe"

# webdriver_path = "./workspace/research-market-tv/chromedriver/chromedriver"
# browser_path = "/workspace/research-market-tv/chrome/chrome"
enable_headless = False

sms = ModelScraper_SONY_jp(webdriver_path = webdriver_path, browser_path=browser_path, enable_headless=enable_headless)
dict_models = sms.get_models_info()
file_name = f"sony_model_info_web_{date.today().strftime('%Y-%m-%d')}"
FileManager.dict_to_excel(dict_models, file_name=file_name, sheet_name="global")

