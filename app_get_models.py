import time
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from market_research.scraper import Specscraper_s
from market_research.scraper import Specscraper_l
from market_research.scraper import Specscraper_se
from tools.db.firestoremanager import FirestoreManager

app = FastAPI()

file_path = 'firestore-001.json'
firestore_manager = FirestoreManager(file_path)

class ScraperResponse(BaseModel):
    status: str
    message: str

@app.post("/run", response_model=ScraperResponse)
async def run_scraper():
    try:
        print(f"작업 시작: {datetime.now()}")

        # Sony 데이터 수집
        scraper_s = Specscraper_s()
        df = scraper_s.data.set_index('model')
        firestore_manager.save_dataframe(df, 'sony')
        
        # LG 데이터 수집
        scraper_l = Specscraper_l()
        df = scraper_l.data.set_index('model')
        firestore_manager.save_dataframe(df, 'lg')
        
        # Samsung 데이터 수집
        scraper_se = Specscraper_se()
        df = scraper_se.data.set_index('model')
        firestore_manager.save_dataframe(df, 'samsung')

        print(f"작업 완료: {datetime.now()}")
        return {"status": "success", "message": "데이터 수집이 완료되었습니다."}
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import os
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
