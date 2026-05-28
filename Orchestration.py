import asyncio

from mcp_client_server.mcp_client import mcpclient
from Rag.EmbeddingsAndVectorStore import context_retrieval, EmbbeddingsAndIndexing
from llama_index.llms.ollama import Ollama
from ollama import chat
from ollama import ChatResponse


#--- Function to embed User data and/or Prompt into Qdrant ---#
def ragembeddings(Prompt: str = "", Data: list =[]):

    EmbbeddingsAndIndexing(prompt=Prompt,data=Data)

#--- Prompt Expansion Sytem Prompt for Gemma ---#
PROMPT_EXPANDER_SYSTEM_ROLE = """
    You are an advanced Prompt Engineering middleware engine.
    Your sole task is to rewrite, enrich, and expand the user's brief query into a comprehensive, 
    highly detailed prompt. To do this, you must analyze the provided PDF TECHNICAL CONTEXT 
    (which includes raw code, data logs, tables, or structural flowchart markers) and make logical inferences.
    CRITICAL RULES:
    1. Do NOT answer the user's question.
    2. Infer hidden requirements from the PDF (e.g., if the user asks about an error, find the relevant system component names, variables, or architecture layout in the PDF and include them).
    3. Output ONLY the finalized, expanded prompt text. Do not include introductory text like 'Here is your expanded prompt:'.
"""

# --- Context Retrieval Factory function ---#
def contextpromptexpansion(contextRet,prompt: str):
    pdf_context= [context.node.text for context in contextRet]
    page_num = [context.node.metadata.get("page_number") for context in contextRet]
    base64imgEncoding =[context.node.get("full_page_image_b64") for context in contextRet]
    source_file = [context.node.metadata.get("source_file") for context in contextRet]

    response: ChatResponse = chat(
        model='gemma3:4b',
        messages=[
            {
                'role':'system',
                'content': PROMPT_EXPANDER_SYSTEM_ROLE
            },

            {
                'role': 'user',
                'content':[
                        f""" ### RAW USER QUERY TO EXPAND:
                                {prompt}
                            ### PDF TECHNICAL CONTEXT :
                            Source File {source_file} - Page {page_num}
                   
                            Text Content:
                            {pdf_context}
              
                            ###base64 encoded page Image:
                            {base64imgEncoding}

                            """
                ]
            }
        ]
    )

    result = response.message.content
    return str(result).strip() 
    
#--- Context Retrieval Implementation Functions ---#    
def promptexpansion(prompt: str) -> str:

    Instruction_Prefix = """
        Represent this query for retrieving relevant academic document sections stored as metadata pages(images): 
        A research paper Abstract, methodology, Implementation, Results, Discussion, Evaluation,
        or Findings sections. This is for prompt expansion to to address vague prompts. Prompt :
    """
    gemmaEmbInstructPfx: str = Instruction_Prefix.strip()+ " User Prompt: "+ prompt
    extracted_context = context_retrieval(query_Docs= gemmaEmbInstructPfx)
    response = contextpromptexpansion(extracted_context,prompt)

    return response.strip()


#--- Domain Agent Analysis ---#
async def runAnalysis(prompt: str):
    Theoretical_Domain = mcpclient("Theoretical")
    Structural_Domain = mcpclient("Structural")
    Logical_Domain = mcpclient("Logical")

    try:
        await asyncio.gather(
        Theoretical_Domain.connect_to_server("mcp_client_server/Theoreticalserver.py",),
        Structural_Domain.connect_to_server("mcp_client_server/Strcturalserver.py"),
        Logical_Domain.connect_to_server("mcp_client_server/logicalserver.py")
        )

    except Exception as e:
        print(f'Connection to Servers failed : status {e}')
    try:
       result =  await asyncio.gather(
                    Theoretical_Domain.call_analysis("TheoreticalServer", args={"prompt": promptexpansion(prompt)}),
                    Structural_Domain.call_analysis("structuralServer", args={"prompt": promptexpansion(prompt)}),
                    Logical_Domain.call_analysis("logicalServer", args={"prompt": promptexpansion(prompt)})
                     )
    except Exception as e:
        print(f'Something went wrong: Error Details : {e}')
        
    finally:    
        await asyncio.gather(
            Theoretical_Domain.close_async_context(),
            Structural_Domain.close_async_context(),
            Logical_Domain.close_async_context(),
            return_exceptions= True
        )


   # --- Gemma Summarizes Results --- #
    try:
        repsonse: ChatResponse = chat(
            model='gemma3:4b',
            messages=[
                {
                'role': 'user',
                'content': [
                    'Merge all these Responses into One cohessive Response Stictly adhere to what is provided',
                    f'{result[0]}', # type: ignore
                    f'{result[1]}', # type: ignore
                    f'{result[2]}'  # type: ignore
                ]
            }
            ]
        )

        ragembeddings(Prompt= repsonse.message.content)#type: ignore
        return repsonse.message.content
    
    except Exception as e:
        print("failed summarize all Analysis ")
        print("Error Details : {e} ")

        



    
    
    

    