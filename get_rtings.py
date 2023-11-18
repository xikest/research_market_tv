
from datetime import date
from pathlib import Path
import pandas as pd


from market_research import Rtings
from market_research.tools import FileManager
webdriver_path = "./chromedriver/chromedriver.exe"
browser_path = "./chrome/chrome.exe"

# webdriver_path = "./workspace/research-market-tv/chromedriver/chromedriver"
# browser_path = "/workspace/research-market-tv/chrome/chrome"
enable_headless = True



# ## 불러온 데이터 경로
# file_name="rtings_url.xlsx"
# folder_path = Path("input_data/rtings")
# folder_path.mkdir(parents=True, exist_ok=True)
# file_path = folder_path / file_name
# df = pd.read_excel(file_path)
# urls = df["urls"]


# for url in urls:
#     maker = url.split("/")[-2]
#     model = url.split("/")[-1]
#
#
#     rtings = Rtings(webdriver_path = webdriver_path, browser_path=browser_path, enable_headless=enable_headless)
#
#     # 저장할 데이터 경로
#     file_name = f"{maker}_{model}_rtings_comments_{date.today().strftime('%Y-%m-%d')}.xlsx"
#     folder_path = Path("results/rtings/comments")
#     folder_path.mkdir(parents=True, exist_ok=True)
#     file_path = folder_path / file_name
#     comments_df = rtings.get_commetns(url, format_df=True)
#     comments_df.to_excel(f"{file_path}", index=False, sheet_name='comments')
#
#     # 저장할 데이터 경로
#     file_name = f"{maker}_{model}_rtings_scores_{date.today().strftime('%Y-%m-%d')}.xlsx"
#     folder_path = Path("results/rtings/scores")
#     folder_path.mkdir(parents=True, exist_ok=True)
#     file_path = folder_path / file_name
#     score_df= rtings.get_score(url,format_df=True)
#     score_df.to_excel(f"{file_path}", index=False, sheet_name='score')
#
#     # 저장할 데이터 경로
#     file_name = f"{maker}_{model}_rtings_measurement_{date.today().strftime('%Y-%m-%d')}.xlsx"
#     folder_path = Path("results/rtings/measurement")
#     folder_path.mkdir(parents=True, exist_ok=True)
#     file_path = folder_path / file_name
#     measurement_df= rtings.get_measurement_reuslts(url)
#     measurement_df.to_excel(f"{file_path}", index=False, sheet_name='measurement')

intput_folder = Path("input_urls")  # 폴더 이름을 지정
if not intput_folder.exists():
    intput_folder.mkdir(parents=True)

output_folder = Path('results')
if not output_folder.exists():
    output_folder.mkdir(parents=True, exist_ok=True)

urls= ["https://www.rtings.com/tv/reviews/sony/a95l-oled",
       "https://www.rtings.com/tv/reviews/lg/g3-oled"]

score_df = pd.DataFrame()
measurement_df = pd.DataFrame()
comments_df = pd.DataFrame()
for url in urls:
    maker = url.split("/")[-2]
    model = url.split("/")[-1]

    # 저장할 데이터 경로
    file_name = f"rtings{date.today().strftime('%Y-%m-%d')}.xlsx"
    output_file_name = output_folder / file_name
    rtings = Rtings(webdriver_path=webdriver_path, browser_path=browser_path, enable_headless=enable_headless)

    df = rtings.get_score(url, format_df=True)
    score_df = pd.concat([score_df, df], axis=0)
    FileManager.df_to_excel(score_df, file_name=output_file_name, sheet_name="scores", mode='w')

    # 저장할 데이터 경로
    df = rtings.get_measurement_reuslts(url)
    measurement_df = pd.concat([measurement_df, df], axis=0)
    FileManager.df_to_excel(measurement_df, file_name=output_file_name, sheet_name="measurement", mode='a')

    comments_df = rtings.get_commetns(url, format_df=True)
    comments_df = pd.concat([comments_df, df], axis=0)
    FileManager.df_to_excel(comments_df, file_name=output_file_name, sheet_name="comments", mode='a')