from Orchestration import runAnalysis, ragembeddings
from ollama import chat
from ollama import ChatResponse

def Evaluation(response,prompt):
    result: str =""
    try:
        systemPrompt= """
                        You are a strict evaluation API. Your ONLY output allowed is a single,
                        raw integer from 0 to 10 reflecting the responses alignment to users prompt.
                        Factor Scoring on Hallucination and ALigned Reasoning.
                        Do NOT include markdown block wraps (like ```), do NOT include text,
                        do NOT include spaces, do NOT include punctuation, and do NOT explain your reasoning.
                      """
        print("\n Running Evaluation \n")
        response1: ChatResponse = chat(
            model='gemma3:4b',
            messages=[
                {
                    'role':'system',
                    'content':systemPrompt
                },
                {
                'role': 'user',
                'content':f"""
                    ### Users Prompt##
                    {prompt}
                    
                    ### Generated Response ###
                    {response}
                """
            }
            ]
        )
        print("Evaluation Score:",response1.message.content)
        result = response1.message.content #type: ignore
        return int(result)
    except Exception as e:
        print("something Went Wrong")
        return 0