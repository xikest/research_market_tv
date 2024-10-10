import time
from datetime import datetime, timedelta
from market_research.scraper import Specscraper_s
from market_research.scraper import Specscraper_l
from market_research.scraper import Specscraper_se
from .firestoremanager import FirestoreManager

def main():
    file_path = 'firestore-001.json'
    firestore_manager = FirestoreManager(file_path)

    one_day = 24 * 60 * 60  # 86400초

    while True:

        print(f"작업 시작: {datetime.now()}")

        scraper_s = Specscraper_s()
        firestore_manager.save_dataframe(scraper_s, 'sony')
        
        scraper_l = Specscraper_l()
        firestore_manager.save_dataframe(scraper_l, 'lg')
        
        scraper_se = Specscraper_se()
        firestore_manager.save_dataframe(scraper_se, 'samsung')

        print(f"작업 완료: {datetime.now()} - 24시간 후에 다시 실행됩니다.")
        time.sleep(one_day)

if __name__ == "__main__":
    main()