import requests

# FastAPI 서버의 URL 설정 (로컬에서 실행 중일 경우)
url = "http://localhost:8080/run"

# POST 요청 보내기
response = requests.post(url)

# 응답 출력
if response.status_code == 200:
    print("성공:", response.json())
else:
    print("에러 발생:", response.status_code, response.text)
