import pandas as pd
import seaborn as sns
from nltk.probability import FreqDist
from nltk import pos_tag
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
from pathlib import Path

class TextAnalysis:
    def __init__(self):
        self.comments:[str,]
        self.nouns:[str,]
        self.df_word_freq:pd.DataFrame
        self._set_datapack()

    def get_comments(self, comments:str)-> None:
        self.comments = comments
        self._prepare_nouns()
        self._prepare_word_freq()
        return None

    def save_df_freq_as_excel(self, output_dir: Path = Path("results"), file_name: str = "your_excel_file_name"):
        output_dir.mkdir(parents=True, exist_ok=True)  # 디렉터리 생성
        df = self.df_word_freq
        df.to_excel(output_dir / (file_name + "_freq.xlsx"), index=False)



    def _set_datapack(self) -> None:
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('averaged_perceptron_tagger')
        return None
    def _prepare_nouns(self) -> None:
        all_words = []
        for comment in self.comments:
            tokens = word_tokenize(comment)
            all_words.extend(tokens)
        stop_words = set(stopwords.words('english'))
        filtered_words = [word.lower() for word in all_words if
                          word.isalnum() and word.lower() not in stop_words]
        self._nouns = [word for (word, tag) in pos_tag(filtered_words) if tag.startswith('N')]
        return None
    def _prepare_word_freq(self) -> None:
        noun_counts = FreqDist(self._nouns)
        df_word_freq = pd.DataFrame(list(noun_counts.items()), columns=['Nouns', 'Frequency'])
        self.df_word_freq = df_word_freq.sort_values(by='Frequency', ascending=False)
        return None

    def plot_freq(self, num_dis: int = 10):
        try:
            df_word_freq=self.df_word_freq
            sns.set(style="white")
            top_words = df_word_freq.head(num_dis)
            plt.figure(figsize=(10, 4))
            sns.barplot(x='Nouns', y='Frequency', data=top_words)
            plt.title("Top 10 Words Frequency")
            plt.xticks(rotation=45)
            sns.despine()
            if save_path:
                plt.savefig(save_path)

            plt.show()

        except Exception as e:
            print(e)
            print("data not prepared")

    def plot_wordcloud(self):
        nouns = self._nouns
        try:
            sns.set(style="white")
            wordcloud = WordCloud(width=800, height=400, background_color="white").generate(" ".join(nouns))
            plt.figure(figsize=(10, 4))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis("off")
            plt.show()

        except Exception as e:
            print(e)
            print("data not prepared")