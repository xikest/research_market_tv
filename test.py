# import requests
# response = requests.post("https://mktretv1-598472753671.us-central1.run.app")
# print(response)
import requests

url = "http://127.0.0.1:8080/items/42?q=test"  # 포트를 8080으로 설정


try:
    response = requests.post(url)
    print("요청 성공:", response.json())
except requests.exceptions.RequestException as e:
    print("요청 실패:", str(e))
