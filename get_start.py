from modelspec import ModelScraper , FileManager, ModelInfo
from datetime import date
from fastapi import FastAPI, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

app = FastAPI()

# SQLite 데이터베이스에 연결
DATABASE_URL = "sqlite:///./model_info.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@app.post("/start")
def create_model_info():
    # webdriver_path = "./chromedriver/chromedriver.exe"
    # browser_path = "./chrome/chrome.exe"

    webdriver_path = "/workspace/research-market-tv/chromedriver/chromedriver"
    browser_path = "/workspace/research-market-tv/chrome/chrome"
    enable_headless = True

    sms = ModelScraper(webdriver_path = webdriver_path, browser_path=browser_path, enable_headless=enable_headless)
    dict_models = sms.get_models_info()
    file_name = f"sony_model_info_web_{date.today().strftime('%Y-%m-%d')}"
    FileManager.dict_to_excel(dict_models, file_name=file_name, sheet_name="global")

    # SQLAlchemy 세션 생성, 딕셔너리를 데이터베이스에 저장
    db = SessionLocal()
    for model_name, model_info in dict_models.items():
        db_model = ModelInfo(model_name=model_name, model_info=str(model_info))
        db.add(db_model)
    db.commit()
    db.close()

# 데이터베이스 세션을 context manager로 관리하는 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/info")
def read_model_info(db: Session = Depends(get_db)):
    # 데이터베이스에서 딕셔너리 읽어오기
    rows = db.query(ModelInfo).all()
    result = {row.model_name: row.model_info for row in rows}
    return result