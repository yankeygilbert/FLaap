import os
import io
import asyncio

from google import genai
from ollama import chat
from dotenv import load_dotenv

load_dotenv()
client1 = genai.Client(api_key = os.getenv("Gemini_Api_Key"))
client2 = genai.Client(api_key=os.getenv("Gemini_Api_Key2"))
client3 = genai.Client(api_key=os.getenv("Gemini_Api_Key3"))

#---Test Connection to Gemini---
async def Test_Conncection_To_Gemini_1():

    try:
        Response1 =  client1.models.generate_content(
            model = "gemini-3-flash-preview",
            contents = "Respond with word 'Success' if you I can reach you"
        )

        print(f'Connection to Gemini-1 Status:{Response1.text}')
        return Response1.text # type: ignore
    except Exception as e:
        print(f'Connection Failed \n Error Details:{e}')

async def Test_Conncection_To_Gemini_2():
   
    try:
        Response2 = client2.models.generate_content(
            model = "gemini-3-flash-preview",
            contents = "Respond with word 'Success' if you I can reach you"
        )

        print(f'Connection to Gemin-2 Status:{Response2.text}')      
        return Response2.text # type: ignore
    
    except Exception as e:
        print(f'Connection Failed \n Error Details:{e}')
 

async def Test_Conncection_To_Gemini_3():
   
    try:
        Response3 = client3.models.generate_content(
            model = "gemini-3-flash-preview",
            contents = "Respond with word 'Success' if you I can reach you"
        )

        print(f'Connection to Gemini-3 Status:{Response3.text}')
        return Response3.text # type: ignore
    except Exception as e:
        print(f'Connection Failed \n Error Details:{e}')
    

async def Test_All_Gemini_Connection():
    return [
            await Test_Conncection_To_Gemini_1(),
            await Test_Conncection_To_Gemini_2(),
            await Test_Conncection_To_Gemini_3(),
                ]

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

        print(f'Connection to Gemma3:4b Local Status {response.message.content}')
        return response .message.content# type: ignore
    except Exception as e:
        print(f'Connection Failed \n Error Details:{e}')
    





