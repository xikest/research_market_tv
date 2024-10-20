from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from market_research.scraper import Specscraper_s
from market_research.scraper import Specscraper_l
from market_research.scraper import Specscraper_se
import os
import logging
# from tools.db.firestoremanager import FirestoreManager


app = FastAPI()
logging.basicConfig(level=logging.INFO)

# file_path = 'firestore-001.json'
# firestore_manager = FirestoreManager(file_path)

class ScraperResponse(BaseModel):
    status: str
    message: str
    webdriver_path: dict  

@app.post("/run", response_model=ScraperResponse)
async def run_scraper():
    webdriver_path = {"driver_path": '/usr/local/bin/chromedriver',
                      "chrome_path": '/usr/bin/google-chrome'}

    try:
        # Sony 데이터 수집
        data_dict= dict()
        scraper_s = Specscraper_s(webdriver_path=webdriver_path)
        df_sony = scraper_s.data.set_index('model')
        data_dict['sony'] = df_sony.to_dict(orient='records')  # DataFrame을 dict 형태로 변환하여 저장
        # firestore_manager.save_dataframe(df, 'sony')
        
        # LG 데이터 수집
        scraper_l = Specscraper_l(webdriver_path=webdriver_path)
        df_lg = scraper_l.data.set_index('model')
        data_dict['lg'] = df_lg.to_dict(orient='records')  # DataFrame을 dict 형태로 변환하여 저장
    
        # firestore_manager.save_dataframe(df, 'lg')
        
        # Samsung 데이터 수집
        scraper_se = Specscraper_se(webdriver_path=webdriver_path)
        df_samsung = scraper_se.data.set_index('model')
        data_dict['samsung'] = df_samsung.to_dict(orient='records')  # DataFrame을 dict 형태로 변환하여 저장
        # firestore_manager.save_dataframe(df, 'samsung')

        print(f"작업 완료: {datetime.now()}")
        

        return data_dict  # data_dict만 반환
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import os
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
