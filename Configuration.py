import os
import io

from google import genai
from ollama import chat
from dotenv import load_dotenv

load_dotenv()

#---Test Connection to Gemini---
def Test_Conncection_To_Gemini():
    try:
        client = genai.Client(api_key = os.getenv("Gemini_Api_Key"))

        Response = client.models.generate_content(
            model = "gemini-3-flash-preview",
            contents = "Respond with word 'Success' if you I can reach you"
        )

        print(f'Connection to Gemini Status:{Response.text}')
    except Exception as e:
        print(f'Connection Failed \n Error Details:{e}')


def Test_Conncection_To_Gemma3():
    try:
        response = chat(
            model= 'gemma3:4b',
            messages=[
                {
                    'role':'user',
                    'content':'Respond with word "Success" if you I can reach you'
                }
            ]
        )

        print(f'Connection to Gemma Status {response.message.content}')
    except Exception as e:
        print(f'Connection Failed \n Error Details:{e}')


Test_Conncection_To_Gemini()
Test_Conncection_To_Gemma3()




