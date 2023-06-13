import  sys

from getmodelspec import LineUp
from getmodelspec import dictToexcel
from datetime import date

sys.path.insert(0, '/chromedriver_win32/chromedriver')  # 크롬 드라이버 지정

lineUp = LineUp()
dictModels = lineUp.getSony(src='jp')
dictModels = lineUp.getPana()
# fileName=f"sony_TV_series_{date.today().strftime('%Y-%m-%d')}.xlsx"
# df_models.to_excel(fileName)# 엑셀 파일로 저장
