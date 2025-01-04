import numpy as np
import pandas as pd
class DataCleaner:
    """
    cleanup = DataCleaner(df)
    df = cleanup.get_df_cleaned()
    df_prices = cleanup.get_price_df()
    """
    def __init__(self, df):
        self.df = df.copy()
        self._preprocess_df()
        self._cleanup_columns()

    def _preprocess_df(self):
        self.df = self.df.sort_values(["year", "series", "size"], axis=0, ascending=False)
        def transform_text(x):
            if isinstance(x, str):
                x = x.replace("  ", " ")  # 두 개의 공백을 하나로 변경
                x = x.replace("™", "")  # ™ 제거
                x = x.replace("®", "")  # ® 제거
                x = x.replace("\n\n", "\n ")  # 이중 줄바꿈을 단일 줄바꿈으로 변경
                x = x.replace(" \n", "\n ")  # 공백 후 줄바꿈 처리
                x = x.strip()  # 앞뒤 공백 제거
                x = x.lower()  # 모두 소문자로 변경
            return x

        self.df = self.df.map(transform_text)
        self.df.columns = [transform_text(x) for x in self.df.columns]
        self.df = self.df.groupby('series').apply(lambda x: x.ffill().bfill()).reset_index(drop=True)
        self.df = self.df.groupby('series').apply(lambda x: x.ffill().bfill()).reset_index(drop=True).infer_objects()
        self.df = self.df.sort_values(by=["series"])
        self.df.columns = self.df.columns.str.strip()
        try:
            self.df = self.df.rename(columns={"rated power consumption": "maximum power consumption", "maximum power consumption": "maximum power consumption"})
            self.df['maximum power consumption'] = self.df['maximum power consumption'].astype(str).str.replace('w', '').str.strip()
        except: pass
        self.df = self.df.sort_values(by=['year', 'size', 'series'], ascending=[False, True, False])
        self.df['year'] = self.df['year'].astype('str')
        

    def get_price_df(self):
            df = self.df[
                ["year", "size", "series", "price", "price_original", "price_gap", "description"]]
            df = df.sort_values(["price", "year", "series", "size", ], ascending=False)
            df = df.dropna(subset=['price'])  #
            df['price_gap'] = df['price_gap'].fillna(0)
            df['price_gap'] = df['price_gap'].map(lambda x: int(x))
            df = df.sort_values(by=['year',  'series'], ascending=True)
            df.loc[:, 'description'] = df.apply(lambda row: 
                        f"{row['description']}<br>release: ${row['price_original']}<br>price: ${row['price']} ({row['price_gap']}↓)"  
                                                    if row['price_gap'] != 0 else 
                                                    f"{row['description']}<br>price: ${row['price']}" , axis=1)
            return df
        
    def get_power_concumption_df(self):
        df = self.df.copy()
        try: 
            df['maximum power consumption'] = df['maximum power consumption'].replace('-', np.nan)
            df = df[df['maximum power consumption'].notna()]
            df['maximum power consumption'] = pd.to_numeric(df['maximum power consumption'], errors='coerce') 
            df = df.dropna(subset=['maximum power consumption']) 
        except:
            df['maximum power consumption'] = None  
        return df
        

    def _cleanup_columns(self):
        self.df = self.df.drop_duplicates()

    def get_df_cleaned(self):
        if self.df is not None:
            df = self.df
            df = df.set_index(["year", "series"])
            df = df.fillna("-")
            
            return df