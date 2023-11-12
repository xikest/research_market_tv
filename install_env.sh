#!/bin/bash

# Update pip
pip install --upgrade pip

# Install required Python packages
pip install -U openpyxl requests selenium beautifulsoup4 tqdm numpy pandas
# Update apt-get
apt-get update

# Download and setup Chrome
wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/linux64/chrome-linux64.zip
unzip chrome-linux64.zip
rm chrome-linux64.zip
mv chrome-linux64 chrome

# Download and setup ChromeDriver
wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/linux64/chromedriver-linux64.zip
unzip chromedriver-linux64.zip
rm chromedriver-linux64.zip
mv chromedriver-linux64 chromedriver
