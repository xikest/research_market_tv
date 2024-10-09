import pandas as pd
import seaborn as sns
import os
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
import io
import wget
from nltk.probability import FreqDist
from nltk import pos_tag
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import fitz  # PyMuPDF
from ._analysis_scheme import Analysis


class TextAnalysis(Analysis):
    def __init__(self,
                 export_prefix="text_", intput_folder_path="/content/input",  output_folder_path="results"):
        self.comments:list
        self.nouns:list
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



    def download_pdfs(self, urls:list):
        for url in urls:
            try:
                filename = os.path.join(self.intput_folder, os.path.basename(url))
                if not os.path.exists(filename):
                    wget.download(url, filename)
            except Exception as e:
                print(f"Error downloading {url}: {str(e)}")

        print(f"downloaded in '{os.path.join(os.getcwd(), self.intput_folder)}'")

    def set_comments(self, comments: list, cleaning_words: list = None) -> None:
        self.comments = comments
        self._prepare_nouns(cleaning_words)
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
    
    def _prepare_nouns(self, cleaning_words) -> None:
        all_words = []
        for comment in self.comments:
            tokens = word_tokenize(comment)
            all_words.extend(tokens)
        stop_words = set(stopwords.words('english'))
        stop_words.update(cleaning_words)
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

    def plot_wordcloud(self, comment, cleaning_words=[]):
        
        self.set_comments([comment], cleaning_words)
                
        nouns = self._nouns

        width = 1000 
        height = 1000 

        try:
            wordcloud = WordCloud(width=width, height=height, background_color='white').generate(" ".join(nouns))

            img = io.BytesIO()
            wordcloud.to_image().save(img, format='PNG')
            img.seek(0)
            encoded_img = base64.b64encode(img.getvalue()).decode()

            fig = go.Figure()
            fig.add_layout_image(
                dict(
                    source=f'data:image/png;base64,{encoded_img}',
                    x=0, y=1,
                    xref="paper", yref="paper",
                    sizex=1, sizey=1,
                    xanchor="left", yanchor="top",
                    opacity=1,
                    layer="above"
                )
            )

            fig.update_layout(
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                width=width,
                height=height,
                margin=dict(l=0, r=0, t=0, b=0)  
            )

            # fig.show()
        except Exception as e:
            print(e)
            print("data not prepared")
        return fig
            
            

    def pdf_to_text(self, pdf_path):
        text = ''
        with fitz.open(pdf_path) as pdf_reader:
            num_pages = pdf_reader.page_count
            for page_num in range(num_pages):
                page = pdf_reader[page_num]
                text += page.get_text()
        
        return text

