
# GetSONY
GetSONY is a Python script for scraping Sony TV models and extracting their specifications and scores.
It utilizes web scraping techniques to gather information from Sony's official website and other sources.

## Installation
To use GetSONY, you'll need to install the required dependencies. Run the following command to install them:

```shell
pip install pandas beautifulsoup4 selenium tqdm
```
Usage
The GetSONY class provides methods for retrieving Sony TV models and their specifications. Here's an example of how to use it:

```python
from GetSONY import GetSONY
```
# Create an instance of GetSONY
```python
get_sony = GetSONY()
```
# Get the Sony TV models and their information
```python
models = get_sony.getModels()
```
# Print the models
```python
print(models)
```
By default, the script will scrape information from Sony's official website and save the results to an Excel file. You can customize the behavior by passing different parameters to the GetSONY constructor.

Contributing
Contributions are welcome! If you find any issues or want to add new features, feel free to open a pull request.

License
This project is licensed under the MIT License. See the LICENSE file for details.

vbnet
Copy code

Make sure to replace `GetSONY` with the appropriate file name if needed. Additionally, you may want to include sections like "Features," "Requirements," or "Examples" based on the specific details and functionality of your code.



