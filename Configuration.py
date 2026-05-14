from google import genai
from dotenv import load_dotenv
import os


load_dotenv()

#Test Connection to Gemini
def Test_Conncection_To_Gemini():

    client = genai.Client(api_key = os.getenv("Gemini_Api_Key"))

    Response = client.models.generate_content(
        model = "gemini-3-flash-preview",
        contents = "Hey gemini"
    )


    if Response:
        print("Connection Status: Connceted"  )
        return True
    print("Something went Wrong"  )
    return False
