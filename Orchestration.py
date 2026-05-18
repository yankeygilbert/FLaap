import asyncio


from mcp_client_server.mcp_client import mcpclient
from Rag.EmbeddingsAndVectorStore import context_retrieval, EmbbeddingsAndIndexing
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.llms.ollama import Ollama
from ollama import chat
from ollama import ChatResponse
#--- Function to embed User data and Prompt into Qdrant ---#
def ragembeddings(Prompt: str = "", Data: list =[]):

    EmbbeddingsAndIndexing(prompt=Prompt,data=Data)


#--- Prompt Expansion Sytem Prompt for Gemma ---#
PROMPT_EXPANDER_SYSTEM_ROLE = (
    "You are an advanced Prompt Engineering middleware engine.\n"
    "Your sole task is to rewrite, enrich, and expand the user's brief query into a comprehensive, "
    "highly detailed prompt. To do this, you must analyze the provided PDF TECHNICAL CONTEXT "
    "(which includes raw code, data logs, tables, or structural flowchart markers) and make logical inferences.\n\n"
    "CRITICAL RULES:\n"
    "1. Do NOT answer the user's question.\n"
    "2. Infer hidden requirements from the PDF (e.g., if the user asks about an error, find the relevant system component names, variables, or architecture layout in the PDF and include them).\n"
    "3. Output ONLY the finalized, expanded prompt text. Do not include introductory text like 'Here is your expanded prompt:'."
)

gemma3 = Ollama(
    model= 'gemma3:4b',
    temperature = 0.4
)

def contextpromptexpansion(context,prompt: str):
    pdf_context= context.node.text
    page_num = context.node.metadata.get("page_number","unkown")
    source_file = context.node.metadata.get("source_file","Document")

    messages = [
        ChatMessage(
            role = MessageRole.SYSTEM,
            content = PROMPT_EXPANDER_SYSTEM_ROLE
        ),
        ChatMessage(
            role= MessageRole.USER,
            content=(
                f"### PDF TECHNICAL CONTEXT ({source_file} - Page {page_num}):\n"
                f"```text\n"
                f"{pdf_context}\n"
                f"```\n\n"
                f"### RAW USER QUERY TO EXPAND:\n"
                f"{prompt}\n\n"
                f"### EXPANDED PROMPT OUTPUT:"
            )
        )

    ]
    response = gemma3.chat(messages)
    result = response.message.content
    return str(result).strip() 
    
def promptexpansion(prompt: str):

    extracted_context = context_retrieval(query_agent= prompt)
    response = contextpromptexpansion(extracted_context,prompt)

    return response


#--- Domain Agent Analysis ---#
async def runAnalysis(prompt: str):
    Theoritical_Domain = mcpclient()
    Structural_Domain = mcpclient()
    Logical_Domain = mcpclient()

    try:
        await asyncio.gather(
        Theoritical_Domain.connect_to_server("mcp_client_server/theoriticalserver.py",),
        Structural_Domain.connect_to_server("mcp_client_server/Strcturalserver.py"),
        Logical_Domain.connect_to_server("mcp_client_server/theoriticalserver.py")
        )

    except Exception as e:
        print(f'Connection to Servers failed : status {e}')
    try:
       result =  await asyncio.gather(
                    Theoritical_Domain.call_analysis("theoriticalServe", args={"prompt": promptexpansion(prompt)}),
                    Structural_Domain.call_analysis("structuralServer", args={"prompt": promptexpansion(prompt)}),
                    Logical_Domain.call_analysis("logicalServer", args={"prompt": promptexpansion(prompt)})
                     )
    except Exception as e:
        print(f'Something went wrong: Error Details : {e}')
        
    await asyncio.gather(
        Theoritical_Domain.close_async_context(),
        Structural_Domain.close_async_context(),
        Logical_Domain.close_async_context()
    )


   # --- Gemma Summarizes Results --- #
    repsonse: ChatResponse = chat(
        model='gemma3:4b',
        messages=[
            {
            'role': 'user',
            'content': [
                'Merge all these Responses into One cohessive Response Stict to what is provided',
                f'{result[0]}', # type: ignore
                f'{result[1]}', # type: ignore
                f'{result[2]}'  # type: ignore
            ]
        }
        ]
    )

    return repsonse.message.content

    
    
    

    