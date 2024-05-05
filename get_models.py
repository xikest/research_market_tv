from market_research.scraper import Specscraper_s, Specscraper_l, Specscraper_sjp, Specscraper_p


scraper_s = Specscraper_s(export_prefix="sony_model_info_web")
df_s_models = scraper_s.get_models_info()

scraper_l = Specscraper_l(export_prefix="lge_model_info_web")
df_l_models = scraper_l.get_models_info()

scraper_sjp = Specscraper_sjp(export_prefix="sony_model_info_web_jp")
df_sjp_models = scraper_sjp.get_models_info()

scraper_p = Specscraper_p(export_prefix="pana_model_info_web")
df_p_models = scraper_p.get_models_info()