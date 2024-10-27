FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
ENV SELENIUM_URL="http://selenium:4444/wd/hub"
EXPOSE 8080
CMD ["uvicorn", "app_get_models:app", "--host", "0.0.0.0", "--port", "8080"]