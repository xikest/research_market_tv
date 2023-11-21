import pandas as pd

from market_research.scraper import Specscraper_s, Specscraper_sjp, Specscraper_p
from market_research.tools import FileManager
from datetime import date


scraper_s = Specscraper_s(export_prefix="sony_model_info_web")
df_s_models = scraper_s.get_models_info()


scraper_sjp = Specscraper_sjp(export_prefix="sony_model_info_web_jp")
df_sjp_models = scraper_sjp.get_models_info()


scraper_p = Specscraper_p(export_prefix="pana_model_info_web")
df_p_models = scraper_p.get_models_info()