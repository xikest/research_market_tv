from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from market_research.scraper import Specscraper_s
from market_research.scraper import Specscraper_l
from market_research.scraper import Specscraper_se
from tools.db.firestoremanager import FirestoreManager
import os
import logging
import uvicorn

app = FastAPI()
logging.basicConfig(level=logging.INFO)

class SecretResponse(BaseModel):
    secret: str

class ScraperRequest(BaseModel):
    pass

@app.get("/get-secret", response_model=SecretResponse)
async def get_secret():
    try:
        secret_file_path = "/keys/firestore"

        if os.path.exists(secret_file_path):
            with open(secret_file_path, 'r') as secret_file:
                firestore_secret = secret_file.read().strip()
                return {"key": firestore_secret}
        else:
            raise HTTPException(status_code=404, detail="Secret file not found!")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run")
async def run_scraper(scraper_request: ScraperRequest):
    firestore = await get_secret()
    firestore_manager = FirestoreManager(firestore.key)
    data_dict = {}
    try:
        scraper_s = Specscraper_s()
        data_dict['sony'] = scraper_s.data.set_index('model')
        logging.info("sony finish")
        
        scraper_l = Specscraper_l()
        data_dict['lg']  = scraper_l.data.set_index('model')
        logging.info("lg finish")
        
        scraper_se = Specscraper_se()
        data_dict['samsung'] = scraper_se.data.set_index('model')
        logging.info("samsung finish")
        
        firestore_manager.save_dataframe(data_dict, 'tv_maker_web_data')
        
        logging.info(f"작업 완료: {datetime.now()}")
        return {"status": "ok"}  

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
