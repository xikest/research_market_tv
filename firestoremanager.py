import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account

class FirestoreManager:
    def __init__(self, credentials_file):
        # 서비스 계정 자격 증명 로드
        self.credentials = service_account.Credentials.from_service_account_file(credentials_file)
        print("Credentials loaded successfully.")
        
        # Firestore 클라이언트 초기화
        self.db = firestore.Client(credentials=self.credentials)
        print("Firestore client initialized successfully.")

    def save_dataframe(self, dataframe, collection_name):
        """데이터프레임의 내용을 Firestore에 저장합니다."""
        for index, row in dataframe.iterrows():
            key = f'key_{index}'  # 키 생성
            # 데이터프레임의 각 행을 Firestore 문서로 저장
            doc_ref = self.db.collection(collection_name).document(key)
            doc_ref.set(row.to_dict())
            print(f"Document {key} added successfully.")

    def read_data(self, collection_name):
        """Firestore에서 데이터를 읽어옵니다."""
        docs = self.db.collection(collection_name).stream()
        data = {}
        for doc in docs:
            data[doc.id] = doc.to_dict()
        return data