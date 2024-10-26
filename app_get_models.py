from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from market_research.scraper import Specscraper_s
from market_research.scraper import Specscraper_l
from market_research.scraper import Specscraper_se
from tools.db.firestoremanager import FirestoreManager
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

class SecretResponse(BaseModel):
    secret: str

class ScraperRequest(BaseModel):
    pass

@app.post("/run_mkretv")
async def run_scraper(scraper_request: ScraperRequest):
    firestore_manager = FirestoreManager()
    data_dict = {}
    logging.info("start scraping")
    try:
        scraper_s = Specscraper_s()
        df = scraper_s.fetch_model_data()
        data_dict['sony'] = df.set_index('model')
        logging.info("sony finish")
        
        scraper_l = Specscraper_l()
        df = scraper_l.data.fetch_model_data()
        data_dict['lg'] = df.set_index('model')
        logging.info("lg finish")
        
        scraper_se = Specscraper_se()
        df = scraper_se.fetch_model_data()
        data_dict['samsung'] = df.set_index('model')
        logging.info("samsung finish")
        
        firestore_manager.save_dataframe(data_dict, 'tv_maker_web_data')
        
        logging.info(f"작업 완료: {datetime.now()}")
        return {"status": "ok"}  

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
