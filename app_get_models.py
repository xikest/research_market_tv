from datetime import datetime
from fastapi import FastAPI, HTTPException
from market_research.scraper import Specscraper_s
from market_research.scraper import Specscraper_l
from market_research.scraper import Specscraper_se
from tools.gcp.firestoremanager import FirestoreManager
import logging
import os 
import uvicorn 


app = FastAPI()
logging.basicConfig(level=logging.INFO)


@app.get("/run_mkretv")
async def run_scraper():
    AUTH_PATH = "web-scraper.json"
    firestore_manager = FirestoreManager(credentials_file=AUTH_PATH)
    data_dict = {}
    makers = {"sony":Specscraper_s, "lg":Specscraper_l, "samsung":Specscraper_se}
    finished =[]
    for maker, scraper in makers.items():
        try:
            logging.info("start scraping")
            scraper = scraper()
            df = scraper.fetch_model_data()
            data_dict[maker] = df.set_index('model')
            logging.info(f"{maker} finish")
            firestore_manager.save_dataframe(data_dict, 'tv_maker_web_data')
            logging.info(f"finish upload {maker}: {datetime.now()}")
            finished.append(maker)
        except Exception as e:
            logging.error(f"Error occurred for {maker}: {str(e)}")
            continue
    return {"finished": finished}
        

# if __name__ == "__main__":
#     uvicorn.run("app_get_models:app", host="0.0.0.0", port=8000)