import pandas as pd
import seaborn as sns
from nltk.probability import FreqDist
from nltk import pos_tag
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import PyPDF2
from pathlib import Path
import fitz  # PyMuPDF
from ._analysis_scheme import Analysis
class TextAnalysis(Analysis):
    def __init__(self,
                 export_prefix="text_", intput_folder_path="input",  output_folder_path="results"):
        self.comments:[str,]
        self.nouns:[str,]
        self.df_word_freq:pd.DataFrame
        super().__init__(export_prefix=export_prefix,  intput_folder_path=intput_folder_path, output_folder_path=output_folder_path)

        # self._set_datapack()
    def read_files_from_inputpath(self, docs_type="excel"):

        file_type = {"excel":['.xlsx', '.xls'],
                     "pdf":[".pdf"]

                     }
        file_list = self.intput_folder.glob('*')

        files = [file for file in file_list if file.suffix in file_type.get(docs_type)]
        return files
    def set_comments(self, comments:list[str,] , cleaning_words:list=None)-> None:
        self.comments = comments
        self.cleaning_words = cleaning_words
        self._prepare_nouns()
        self._prepare_word_freq()
        return None

    def save_df_freq_as_excel(self, file_name: str = "your_excel_file_name"):
        df = self.df_word_freq
        df.to_excel(self.output_folder / (file_name + "_freq.xlsx"), index=False)

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
        stop_words.update(self.cleaning_words)
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
            top_words = df_word_freq.sort_values(by="Frequency", ascending=False).head(num_dis)
            plt.figure(figsize=(10, 4))
            sns.barplot(x='Nouns', y='Frequency', data=top_words)
            plt.title("Top 10 Words Frequency")
            plt.xticks(rotation=45)
            sns.despine()
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

    def pdf_to_text(self, pdf_path):
        text = ""
        try:
            with fitz.open(pdf_path) as pdf_document:
                for page_number in range(pdf_document.page_count):
                    page = pdf_document[page_number]
                    text += page.get_text().lower().strip()

        except Exception as e:
            print(f"Error: {e}")

        return text

    # def pdf_to_text(self, pdf_path):
    #     text = ''
    #     with open(pdf_path, 'rb') as file:
    #         pdf_reader = PyPDF2.PdfReader(file)
    #         num_pages = len(pdf_reader.pages)
    #
    #         for page_num in range(num_pages):
    #             page = pdf_reader.pages[page_num]
    #             text += page.extract_text()
    #
    #     return text


