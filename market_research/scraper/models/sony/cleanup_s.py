import pandas as pd
import numpy as np

class DataCleanup_s:
    """
    cleanup = DataCleanup(df)
    df = cleanup.get_df_cleaned()
    df_prices = cleanup.get_price_df()
    """
    def __init__(self, df, stop_words=None):
        self.df = df.copy()
        self.df_prices = None
        if stop_words is None:
            stop_words = self._call_stop_words()
        self.stop_words = [stop_word.lower() for stop_word in stop_words]
        self._preprocess_df()
        self._create_price_df()
        self._cleanup_columns()

    def _call_stop_words(self):
        stop_words_list = ["price", "model", "description",
                           "weight", "dimension", "size", "stand", "W x H", "W x H x D", "Wi-Fi", "atore", "audio",
                           "frame", "length", "qty",
                           "power", "usb", "channels", "language", "timer", "apple", "TALKBACK", "voice", "sensor",
                           "system", "channel", "storage", "cable",
                           "style", "protection", "hdmi", "energy", "sound", "camera", "subwoofer", "satellite",
                           "input", "output", "caption", "headphone", "radio", "text", "internet", "dsee", "speaker",
                           "bluetooth", "accessories", "mercury", "remote", "smart", "acoustic", "support",
                           "wallmount", "mic", "network", "android", "ios", "miracast",
                           "operating", "store", "clock", "rs-232c", "menu", "mute", "4:3", "hdcp",
                           "built", "tuners", "demo", "presence", "switch", "reader", "face", "surround", "phase",
                           "batteries", "info", "Parental", "setup", "aspect", "dashboard", "formats", "accessibility",
                           "ci+",
                           "bass", "master", "shut", "sorplas", "volume", "wireless", "china",
                           "hole", "program", "manual", "latency",
                           "inversion","twin","h x v","bravia","motion", "netflix","calman","rate"]
        return stop_words_list

    def _preprocess_df(self):
        self.df = self.df.sort_values(["year", "series", "size", "grade"], axis=0, ascending=False)
        self.df = (self.df.map(lambda x: x.replace("  ", " ") if isinstance(x, str) else x)  # 공백 2개는 하나로 변경
                   .map(lambda x: x.replace("™", "") if isinstance(x, str) else x)  # ™ 제거
                   .map(lambda x: x.replace("®", "") if isinstance(x, str) else x)  # ® 제거
                   .map(lambda x: x.replace("\n\n", "\n ") if isinstance(x, str) else x)
                   .map(lambda x: x.replace(" \n", "\n ") if isinstance(x, str) else x)
                   .map(lambda x: x.strip() if isinstance(x, str) else x)  # 문장 끝 공백 제거
                   .map(lambda x: x.lower() if isinstance(x, str) else x))

        self.df.columns = [x.replace("  ", " ").replace("™", "").replace("®", "").strip() if isinstance(x, str) else x
                           for x in self.df.columns]
        self.df.columns = self.df.columns.map(lambda x: x.lower())

    def _create_price_df(self):
        ds_prices = (self.df.loc[:, ["price"]]
                     .map(lambda x: x.split(" ") if isinstance(x, str) & len(x) > 0 else np.nan).dropna()
                     .map(lambda x: [x[0], x[0]] if len(x) < 2 else x))  # idx 정보 보관 및 스플릿

        list_prices = [[idx, prices[0],
                        prices[1],
                        (1 - float(prices[0].replace(',', '').replace('$', '')) / float(prices[1].replace(',', '').replace('$', '')))*100 ]
                                              for idx, prices in zip(ds_prices.index, ds_prices.price)]
        df_prices = pd.DataFrame(list_prices, columns=["idx", "price_now", "price_release", "price_discount"])
        df_prices = df_prices.set_index("idx")
        self.df = pd.merge(df_prices, self.df, left_index=True, right_index=True).drop(["price"], axis=1)
        self.df_prices = self.df[
            ["year", "display type", 'size', "series", 'model', 'price_release', 'price_now', "price_discount",
             'description']]

    def get_price_df(self):
        if self.df_prices is not None:
            return self.df_prices.sort_values(["price_discount", "year", "display type", "series", "size", ],
                                              ascending=False)

    def _cleanup_columns(self):
        col_remove = []
        for column in self.df.columns:
            for stop_word in self.stop_words:
                if stop_word in column:
                    col_remove.append(column)
        self.df = self.df.drop(col_remove, axis=1)
        self.df = self.df.drop_duplicates()
        self.df = pd.merge(self.df_prices[['model', 'size']], self.df, left_index=True, right_index=True)

    def get_df_cleaned(self):
        if self.df is not None:
            df = self.df.set_index(["year", "display type", "series"]).drop(
                ["model", "size", "grade"], axis=1)
            # df = df.fillna("-")
            return df
