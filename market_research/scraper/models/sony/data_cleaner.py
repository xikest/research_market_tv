class DataCleaner:
    """
    cleaner = DataCleaner(df)
    cleaned_df = cleaner.get_cleaned_data()
    price_df = cleaner.get_price_data()
    """
    def __init__(self, data_frame):
        self.data_frame = data_frame.copy()
        self._preprocess_data()
        self._remove_duplicates()

    def _preprocess_data(self):
        self.data_frame = self.data_frame.sort_values(["year", "series", "size", "grade"], axis=0, ascending=False)
        
        def clean_text(text):
            if isinstance(text, str):
                text = text.replace("  ", " ")  # Replace double spaces with single space
                text = text.replace("™", "")  # Remove ™ symbol
                text = text.replace("®", "")  # Remove ® symbol
                text = text.replace("\n\n", "\n ")  # Replace double newline with single newline
                text = text.replace(" \n", "\n ")  # Handle space before newline
                text = text.strip()  # Remove leading and trailing spaces
                text = text.lower()  # Convert text to lowercase
            return text

        self.data_frame = self.data_frame.applymap(clean_text)
        self.data_frame.columns = [clean_text(col) for col in self.data_frame.columns]

    def get_price_data(self):
        price_data = self.data_frame[
            ["year", "display type", "size", "series", "model", "price", "original_price", "price_gap", "description"]
        ]
        return price_data.sort_values(["price", "year", "display type", "series", "size"], ascending=False)

    def _remove_duplicates(self):
        self.data_frame = self.data_frame.drop_duplicates()

    def get_cleaned_data(self):
        if self.data_frame is not None:
            cleaned_data = self.data_frame.set_index(["year", "series", "display type"]).drop(
                ["model", "size", "grade"], axis=1
            )
            cleaned_data = cleaned_data.fillna("-")
            return cleaned_data




# class DataCleanup:
#     """
#     cleanup = DataCleanup(df)
#     df = cleanup.get_df_cleaned()
#     df_prices = cleanup.get_price_df()
#     """
#     def __init__(self, df):
#         self.df = df.copy()
#         self._preprocess_df()
#         self._cleanup_columns()


#     def _preprocess_df(self):
#         self.df = self.df.sort_values(["year", "series", "size", "grade"], axis=0, ascending=False)
#         def transform_text(x):
#             if isinstance(x, str):
#                 x = x.replace("  ", " ")  # 두 개의 공백을 하나로 변경
#                 x = x.replace("™", "")  # ™ 제거
#                 x = x.replace("®", "")  # ® 제거
#                 x = x.replace("\n\n", "\n ")  # 이중 줄바꿈을 단일 줄바꿈으로 변경
#                 x = x.replace(" \n", "\n ")  # 공백 후 줄바꿈 처리
#                 x = x.strip()  # 앞뒤 공백 제거
#                 x = x.lower()  # 모두 소문자로 변경
#             return x

#         self.df = self.df.map(transform_text)
#         self.df.columns = [transform_text(x) for x in self.df.columns]


#     def get_price_df(self):
#             df = self.df[
#                 ["year", "display type", "size", "series", "model", "price", "price_original", "price_gap", "description"]]
#             return df.sort_values(["price", "year", "display type", "series", "size", ], ascending=False)

#     def _cleanup_columns(self):
#         self.df = self.df.drop_duplicates()

#     def get_df_cleaned(self):
#         if self.df is not None:
#             df = self.df.set_index(["year", "series", "display type"]).drop(
#                 ["model", "size", "grade"], axis=1)
#             df = df.fillna("-")
#             return df