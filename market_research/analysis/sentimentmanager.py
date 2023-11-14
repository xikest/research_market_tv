import pandas as pd
import re
from tqdm import tqdm
import seaborn as sns
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt
import pickle
from ..tools.aimanager import AIManager
class SentimentManager:
    def __init__(self, api_key=None, verbose=True, gpt_model="gpt-3.5-turbo-1106"):
        self.api_key = api_key
        self.aim = AIManager(self.api_key, gpt_model=gpt_model)
        self.messages_prompt = []
        self.verbose = verbose
        self.df_analyzed_results:pd.DataFrame = None

    def add_message(self, role, content):
        self.messages_prompt.append({"role": role, "content": content})

    def reset_message(self):
        self.messages_prompt =[]

    def analyze_sentiment(self, keyword:str, sentence:str) -> float:
        try:
            # print(f"keyword {keyword}, sentence {sentence}")
            self.add_message("assistant", "You excel as a Picture quality expert and demonstrate exceptional skills in sentiment analysis.")
            # "You are a highly skilled sentiment analyst"
            self.add_message("user", f"Analyze the sentiment of the following text: "
                                     f"Rate the '{keyword}' in the sentence '{sentence}' on a scale from 0 (strongly negative) to 10 (strongly positive)."
                                     f"only respond as only number")
            bot_response = self.aim.get_text_from_gpt(self.messages_prompt)
            # print(f"bot_response: {bot_response}")
            bot_response = float(bot_response)
        except Exception as e:
            print("Analysis error occurred: Returning default value.")
            bot_response = 5.0

        self.reset_message()  # 리셋
        return bot_response

    def analyze_sentences(self, input_sentences:list, keywords: list) ->pd.DataFrame:
        dict_analyzed_scores = dict()
        dict_sentences = dict()
        df_scores_list = []
        # df_scores = pd.DataFrame(columns=keywords)

        for i, sentence in tqdm(enumerate(input_sentences), desc="Processing", unit="sentence"):
            dict_scores = {keyword: self.analyze_sentiment(keyword, sentence) for keyword in keywords}
            dict_analyzed_scores[i] = dict_scores
            dict_sentences[i] = sentence
            # dict_analyzed_scores[f"{i}_{sentence}"]= dict_scores

            if self.verbose:
                print(f"{dict_scores}:{i}_{sentence}")  # Corrected print statement

            df = pd.DataFrame.from_dict(dict_scores, orient='index')
            df_scores_list.append(df)

        df_scores = pd.concat(df_scores_list, axis=1).T
        df_scores.reset_index(drop=True, inplace=True)

        self.df_analyzed_results = df_scores - 5
        return self.df_analyzed_results


    def save_df_as_pickle(self, df, file_name):
        pickle_path = f"{file_name}.pkl"

        with open(pickle_path, 'wb') as file_analyzed:
            pickle.dump(df, file_analyzed)
        print(f"Dataframes saved as pickle: {pickle_path}")

    def load_df_from_pickle(self, file_name):
        pickle_path = f"{file_name}.pkl"
        with open(pickle_path, 'rb') as file_analyzed:
            df = pickle.load(file_analyzed)
        return df

    def save_df_as_csv(self, df: pd.DataFrame) -> bytes:

        csv_file = df.to_csv(index=False).encode('utf-8')
        # if preview:
        #     st.dataframe(df.head(3))
        return csv_file

    def read_df_from(self, data_uploaded, column_name="sentences") -> pd.Series:
        df = pd.DataFrame()
        supported_formats = ['.csv', '.xlsx', '.txt']
        if data_uploaded.name.endswith(tuple(supported_formats)):
            if data_uploaded.name.endswith('.csv'):
                df = pd.read_csv(data_uploaded)
            elif data_uploaded.name.endswith('.xlsx'):
                df = pd.read_excel(data_uploaded, engine='openpyxl')
            elif data_uploaded.name.endswith('.txt'):
                df = pd.read_csv(data_uploaded, delimiter='\t')  # Assuming tab-separated text file
        else:
            print("This file format is not supported. Please upload a CSV, Excel, or text file.")
        return df

    # 전처리 함수 정의

    def preprocess_text(self, text):
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        text = ' '.join(text.split())
        text = text.lower()
        return text

    def sample_sentences(self):
        sentences = [
            "I see the calibration settings page on each TV’s review. Are those the calibration settings that you’re saying should be used for actual viewing, or are they specifically designed for consistency during the testing process? I probably won’t pay a professional to calibrate my screen, but if there are some 'no brainer' settings to tweak, I want to be sure I’m doing it.",
            "The chart in your video has the S90C brightness numbers a lot higher compared to Rtings as well.So when looking at the comparison between S90C and A95L the chart on HDTVTest and if you would make one of the Rtings numbers both tell pretty much the same story. A95L has the upper hand in window sizes <10%, then at 10% things get more equal and at 25% and higher the peak brightness is basically identical. So the source you posted doesn’t contradict the Rtings measurements, rather it backs them up. HDTVTest for some reason just has higher numbers for all TVs, maybe a difference in how he measures things.",
            "So we did double check the brightness measurements and got very similar results. I can manage to get flashes closer to 1500 nits but they don’t stay that bright once the tv has warmed up. For what it’s worth, based on Vincent’s charts, it looks like his unit was around 1550 nits and our unit was around 1450. At high brightness levels, 100 nits won’t be super noticeable so it’s also quite possible that both units are within the expected tolerance. All in all, it remains one of the overall brightest OLED’s we’ve tested with great EOTF tracking. Hope that helps!",
            "Sony claims a 200% increase in peak brightness from the K to the L. and some reviewers noted  a difference. in unspecified brightness.rtings.com:  peak brightness readings  between the two from 10% window to 100% window do not come close to a 200% increase. Little difference. Difficult to explain reviewers comments. However, the HDR brightness went from 82 to 86.Two reviewers said the L came  very close to a $30,000 Sony broadcast monitor. Well, if that’s the case, the K, the LG G3 and Samsung 95C are also close to the monitor. Both the LG and Samsung are brighter than the K or L. Lg by a little. Samsung quite a bit.The only area on which those three were way  worse than the L was pre-calibration.Sure, it’s nice to have it close out of the box, but what rtings.com reader doesn’t calibrate his or her set to rtings.com calibrations? (Only very lazy ones.) Making this pretty meaningless.",
            "note Insider-exclusive early access results were used when comparing the A95L to other models – the text below may be revised when the final review is out (presumably sometime next week).wow, Sony. well done. compared to the A95K, the newer model has a couple of advantages.Sony got rid of the weird and wacky stand from last year, presumably because many users complained that placing a soundbar in front of the TV would block some of the bottom portion of the TV.the overall scores have increased a bit; see below A95K is left score, A95L is right score.mixed usage – 9.0 ➜ 9.2; this is the  highest score for mixed usage on TB 1.11, as of Nov 3, 2023 TV shows – 8.8 ➜ 8.9 sports – 8.9 ➜ 9.1 video games – 9.2 ➜ 9.3 movies in HDR – 9.1 ➜ 9.3 gaming in HDR – 9.0 ➜ 9.1 use as a PC monitor – 9.2 ➜ 9.4 below are the notable differences between the A95K and A95L. HDR – the A95L gets a bit brighter (score went from 8.2 to 8.6) in every realistic scene and window size, although ABL is ever so slightly worse.SDR – A95L is reasonably brighter; score went from 7.2 to 8.1.accuracy – A95L has much accuracy before calibration going from a score of 7.7 to 9.3.stutter – slightly worse on the newer model; was already bad due to the OLED panel’s nearly instantaneous response time.Xbox Series X/S compatibility – A95L now supports full 4K/ 120Hz in Dolby Vision; A95K didn’t support Dolby Vision at all on either console.that is everything that isn’t exactly the same or very close."
        ]
        df = pd.DataFrame({"sentences": sentences})
        return df

    def plot_hist_each(self, output_folder=None, file_name=None):
        if self.df_analyzed_results is None:
            return None
        else:
            df_analyzed_results = self.df_analyzed_results
            columns = df_analyzed_results.columns
            for i, column in enumerate(columns):
                sns.set_style("white")
                fig, axes = plt.subplots(figsize=(10, 4), sharey=True)

                sns.histplot(df_analyzed_results[column], kde=True, label=column, bins=10, binwidth=1, ax=axes)
                axes.set_ylabel("Density")
                axes.set_title(f"{column}")
                # axes.legend(loc="upper right")
                axes.set_xlim(-5, 5)
                axes.set_xlabel("")
                bins = range(-5, 6)
                axes.set_xticks(bins)
                axes.yaxis.set_major_locator(MaxNLocator(integer=True))
                sns.despine()
                plt.tight_layout()

                save_path = None  # 초기화
                if output_folder is not None and file_name is not None:
                    save_path = output_folder / f"{file_name}_{column}_histogram.png"
                if save_path is not None:
                    plt.savefig(save_path, format='png', dpi=300)
                plt.show()

    def plot_hist_all(self, output_folder=None, file_name=None):
        if  self.df_analyzed_results is None:
            return None
        else:
            df_analyzed_results = self.df_analyzed_results
            sns.set(style="white")
            fig, axes = plt.subplots(figsize=(10, 4))

            # 데이터프레임의 각 열에 대해 히스토그램 그리기
            for i, column in enumerate(df_analyzed_results.columns):
              color = sns.color_palette("Set1", len(df_analyzed_results.columns))[i]  # Set1 컬러맵 사용
              sns.histplot(df_analyzed_results[column], kde=True, label=column, bins=10, binwidth=1, ax=axes, color=color)

            # x축 설정
            axes.set_xlim(-5, 5)
            bins = range(-5, 6)
            axes.set_xticks(bins)

            # y축 눈금 설정 (정수로)
            axes.yaxis.set_major_locator(MaxNLocator(integer=True))

            # 레이블 및 타이틀 설정
            axes.set_ylabel("Density")
            axes.set_title("")
            axes.set_xlabel("")

            # 범례 표시
            axes.legend()
            sns.despine()

            save_path = None  # 초기화
            if output_folder is not None and file_name is not None:
              save_path = output_folder / f"{file_name}_all_columns_histogram.png"
            if save_path is not None:
              plt.savefig(save_path, format='png', dpi=300)

            # 그래프 출력
            plt.show()


