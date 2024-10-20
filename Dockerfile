FROM python:3.10-slim
WORKDIR /app
COPY . .


RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    libnspr4 \
    libnss3 \
    libxss1 \
    libxrandr2 \
    libgbm1 \
    libxcomposite1 \
    libxcursor1 \
    libxi6 \
    libxdamage1 \
    libxfixes3 \
    libxrender1 \
    libxtst6 \
    libpango1.0-0 \
    libjpeg62-turbo \
    libasound2 \
    libxkbcommon0 \  
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y wget unzip && \
    wget https://storage.googleapis.com/chrome-for-testing-public/128.0.6613.86/linux64/chrome-linux64.zip && \
    unzip chrome-linux64.zip && \
    rm chrome-linux64.zip && \
    mv chrome-linux64 chrome && \
    rm -rf chrome-linux64

RUN wget https://storage.googleapis.com/chrome-for-testing-public/128.0.6613.86/linux64/chromedriver-linux64.zip && \
    unzip chromedriver-linux64.zip && \
    rm chromedriver-linux64.zip && \
    mv chromedriver-linux64 chromedriver && \
    rm -rf chromedriver-linux64

RUN pip install -r requirements.txt

EXPOSE 8080
CMD ["uvicorn", "app_get_models:app", "--host", "0.0.0.0", "--port", "8080"]