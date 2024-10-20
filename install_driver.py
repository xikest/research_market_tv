import json
from tools.web import Installer

paths = Installer.install_chrome_and_driver()
with open('/app/webdriver_paths.json', 'w') as json_file: 
    json.dump(paths, json_file)