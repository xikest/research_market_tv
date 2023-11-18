import pandas as pd
from openai import OpenAI

class AIManager:
    def __init__(self, api_key, gpt_model="gpt-3.5-turbo-1106"):
        self.client = OpenAI(api_key=api_key)
        self.messages_prompt = []
        self.gpt_model=gpt_model

    def add_message_to_prompt(self, role, content):
        self.messages_prompt.append({"role": role, "content": content})

    def get_text_from_gpt(self, prompt):
        # "gpt-3.5-turbo"
        response = self.client.chat.completions.create(model=self.gpt_model, temperature=0.1,messages=prompt, timeout=60)
        answer = response.choices[0].message.content
        return answer
    def getImageURLFromDALLE(self, user_input):
        response = self.client.images.generate(model="dall-e-3", prompt=user_input,n=1, size="1024x1024", quality="standard")
        image_url = response.data[0].url
        return image_url


    def dataframe_to_text(self,df:pd.DataFrame):
        text = df.to_markdown()
        return text

