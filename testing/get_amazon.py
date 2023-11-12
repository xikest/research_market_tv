from modelspec.amazon import Amazon

webdriver_path = "../chromedriver/chromedriver.exe"
browser_path = "../chrome/chrome.exe"

# webdriver_path = "./workspace/research-market-tv/chromedriver/chromedriver"
# browser_path = "/workspace/research-market-tv/chrome/chrome"
enable_headless = True



amazon = Amazon(webdriver_path = webdriver_path, browser_path=browser_path, enable_headless=enable_headless)
comments_dict = amazon.get_allcomments()
# print(comments_dict)