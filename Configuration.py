import os
import sys
import subprocess

from ollama import chat
from dotenv import load_dotenv

load_dotenv()


#--- Set Up local Resources ---#
def localResourcesShellSetup():
    try:
        result = subprocess.run(
           ["zsh", "shellScriptConfig.zsh"],
            text= True,
            capture_output= True,
            check= True
        )
        print(f'Local Resource Setup complete')
    except subprocess.CalledProcessError as e:
        print(f'Failed to Setup Local Resources \n')
        print(f'Error Details : {e.returncode}', file=sys.stderr)


def Test_Connection_To_Gemma3():
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
    





