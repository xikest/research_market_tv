import  sys
from modelspec.sony_model import SonyModelScraper
from datetime import date


sms = SonyModelScraper(webdriver_path = "./chromedriver/chromedriver.exe", headless=False)
dictModels = sms.get_models_info()
# dictModels = lineUp.getPana()
fileName=f"sony_TV_series_{date.today().strftime('%Y-%m-%d')}.xlsx"
# df_models.to_excel(fileName)# 엑셀 파일로 저장
