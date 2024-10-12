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
        self.df = self.df.sort_values(["year", "series", "size", "grade"], axis=0, ascending=False)
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
        self.df = self.df.groupby('series').apply(lambda x: x.fillna(method='ffill').fillna(method='bfill')).reset_index(drop=True)
        self.df = self.df.sort_values(by=["series","display type"])

    def get_price_df(self):
            df = self.df[
                ["year", "display type", "size", "series", "model", "price", "price_original", "price_gap", "description"]]
            df = df.sort_values(["price", "year", "display type", "series", "size", ], ascending=False)
            return df

    def _cleanup_columns(self):
        self.df = self.df.drop_duplicates()

    def get_df_cleaned(self):
        if self.df is not None:
            df = self.df
            df["display type"] = df["display type"].str.replace(r'display|4k ', '', regex=True)
            df = df.set_index(["year", "series", "display type"]).drop(
                ["model", "size", "grade"], axis=1)
            df = df.fillna("-")
            
            return df