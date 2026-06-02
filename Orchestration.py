import asyncio

from mcp_client_server.mcp_client import mcpclient
from Rag.EmbeddingsAndVectorStore import context_retrieval, EmbbeddingsAndIndexing
from ollama import chat
from ollama import ChatResponse
from Rag.websearch import web_search


#--- Function to embed User data and/or Prompt into Qdrant ---#
async def ragembeddings(Prompt: str = "", Data: list =[]):

    EmbbeddingsAndIndexing(prompt=Prompt,data=Data)

#--- Prompt Expansion Sytem Prompt for Gemma ---#
PROMPT_EXPANDER_SYSTEM_ROLE = """
    You are an advanced Prompt Engineering middleware engine.
    Your sole task is to rewrite, enrich, and expand the user's brief query into a comprehensive, 
    highly detailed prompt. To do this, you must analyze the provided PDF TECHNICAL CONTEXT 
    (which includes raw code, data logs, tables, or structural flowchart markers) and make logical inferences.
    The Expanded prompt should be a user describing a problem he is facing clearly defining the technical Problem inferred from the user prompt.
    CRITICAL RULES:
    Do not propose a design but just expand the user query to contain relevant info that will look like a well written problem query
    1. Do NOT answer the user's question.
    2. Infer hidden requirements from the PDF (e.g., if the user asks about an error, find the relevant system component names, variables, or architecture layout in the PDF and include them).
    3. Output ONLY the finalized, expanded prompt text. Do not include introductory text like 'Here is your expanded prompt:'.
"""

# --- Context Retrieval Factory function ---#
def contextpromptexpansion(context_ret: dict,prompt: str):
    doc_results = context_ret.get("docs", [])
  
    # Extract from docs (text + b64 from Qdrant scroll)
    pdf_context = [r["text"] for r in doc_results]
    base64_images = [r["img_b64"] for r in doc_results if r["img_b64"] is not None]

    response: ChatResponse = chat(
        model='gemma3:4b',
        messages=[
            {
                'role':'system',
                'content': PROMPT_EXPANDER_SYSTEM_ROLE
            },

            {
                'role': 'user',
                'content':f""" ### RAW USER QUERY TO EXPAND:
                                {prompt}
                            ### PDF TECHNICAL CONTEXT :
                            Text Content:
                            {pdf_context}

                            ###base64 encoded page Image:
                            {base64_images}

                            """
                
            }
        ]
    )

    result = response.message.content
    return str(result).strip() 
    
#--- Context Retrieval Implementation Functions ---#    
def promptexpansion(prompt: str) -> str:

    print("Running Prompt Expansion")

    Instruction_Prefix = """
        Represent this query for retrieving relevant academic document sections stored as metadata pages(images): 
        A research paper Abstract, methodology, Implementation, Results, Discussion, Evaluation,
        or Findings sections. This is for prompt expansion to to address vague prompts. Prompt :
    """
    gemmaEmbInstructPfx: str = Instruction_Prefix.strip()+ " User Prompt: "+ prompt
    extracted_context = context_retrieval(query_docs= gemmaEmbInstructPfx)
    response = contextpromptexpansion(extracted_context,prompt) # type: ignore

    return response.strip()

#--- Domain Agent Analysis ---#
async def runAnalysis(prompt: str):
    Theoritical_Domain = mcpclient("Theoretical")
    Structural_Domain = mcpclient("Structural")
    Logical_Domain = mcpclient("Logical")

    exPrompt = promptexpansion(prompt)

    print(f'Expanded Prompt: \n {exPrompt} \n')

    try:
        await asyncio.gather(
        Theoritical_Domain.connect_to_server("mcp_client_server/theoriticalserver.py",),
        Structural_Domain.connect_to_server("mcp_client_server/Structuralserver.py"),
        Logical_Domain.connect_to_server("mcp_client_server/logicalserver.py")
        )

    except Exception as e:
        print(f'Connection to Servers failed : status {e}')
    
    result = []
    try:
       webresult = await web_search(exPrompt)
       result =  await asyncio.gather(
                    Theoritical_Domain.call_analysis("theoriticalServer", {"prompt": exPrompt, "webres":webresult}),
                    Structural_Domain.call_analysis("structuralServer", {"prompt": exPrompt,"webres":webresult}),
                    Logical_Domain.call_analysis("logicalServer", {"prompt": exPrompt,"webres":webresult})
                     )
    except Exception as e:
        print(f'Something went wrong: Error Details : {e}')
        
    finally:    
        await asyncio.gather(
            Theoritical_Domain.close_async_context(),
            Structural_Domain.close_async_context(),
            Logical_Domain.close_async_context(),
            return_exceptions= True
        )


   # --- Gemma Summarizes Results --- #
    try:
        response: ChatResponse = chat(
            model='gemma3:4b',
            messages=[
                {
                    'role':'system',
                    'content':"Merge all these Responses into One cohessive Response Stictly adhere to what is provided"
                },
                {
                'role': 'user',
                'content':f"""
                    {result[0]}
                    {result[1]}
                    {result[2]}
                """
            }
            ]
        )

        await ragembeddings(Prompt= response.message.content)#type: ignore
        return response.message.content
    
    except Exception as e:
        print("failed summarize all Analysis ")
        print(f"Error Details : {e} ")

        



    
    
    

    