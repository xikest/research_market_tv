from modelspec import Rtings
import pandas as pd
from datetime import date
from pathlib import Path

webdriver_path = "./chromedriver/chromedriver.exe"
browser_path = "./chrome/chrome.exe"

# webdriver_path = "./workspace/research-market-tv/chromedriver/chromedriver"
# browser_path = "/workspace/research-market-tv/chrome/chrome"
enable_headless = True


## 불러온 데이터 경로
file_name="rtings_url.xlsx"
folder_path = Path("input_data/rtings")
folder_path.mkdir(parents=True, exist_ok=True)
file_path = folder_path / file_name
df = pd.read_excel(file_path)
urls = df["urls"]

for url in urls:
    maker = url.split("/")[-2]
    model = url.split("/")[-1]


    rtings = Rtings(webdriver_path = webdriver_path, browser_path=browser_path, enable_headless=enable_headless)

    # 저장할 데이터 경로
    file_name = f"{maker}_{model}_rtings_comments_{date.today().strftime('%Y-%m-%d')}.xlsx"
    folder_path = Path("results/rtings/comments")
    folder_path.mkdir(parents=True, exist_ok=True)
    file_path = folder_path / file_name
    comments_df = rtings.get_commetns(url, format_df=True)
    comments_df.to_excel(f"{file_path}", index=False, sheet_name='comments')

    # 저장할 데이터 경로
    file_name = f"{maker}_{model}_rtings_scores_{date.today().strftime('%Y-%m-%d')}.xlsx"
    folder_path = Path("results/rtings/scores")
    folder_path.mkdir(parents=True, exist_ok=True)
    file_path = folder_path / file_name
    score_df= rtings.get_score(url,format_df=True)
    score_df.to_excel(f"{file_path}", index=False, sheet_name='score')
