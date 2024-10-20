FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

RUN python -c "import json; from tools.web import Installer; \
                paths = Installer.install_chrome_and_driver(); \
                with open('/app/webdriver_paths.json', 'w') as json_file: \
                    json.dump(paths, json_file)"


EXPOSE 8080


CMD ["uvicorn", "app_get_models:app", "--host", "0.0.0.0", "--port", "8080"]
