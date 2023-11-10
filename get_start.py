import  sys
from getmodelspec.lineup import LineUp
from datetime import date

sys.path.insert(0, '/usr/bin/chromedriver')  # 크롬 드라이버 지정

lineUp = LineUp()
dictModels = lineUp.getSony(src='global')
# dictModels = lineUp.getPana()
fileName=f"sony_TV_series_{date.today().strftime('%Y-%m-%d')}.xlsx"
# df_models.to_excel(fileName)# 엑셀 파일로 저장
