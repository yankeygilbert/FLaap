"""
                       ---- Orchestrator Engine ----
    This Engine Acts as the main brain of the Failure Analysis Agent.
    Functions:
        1.Receive User input and pass them to the Rag embedding and document processing layer to perform 
        required embeddings and document processing task.

        2. Perform User Prompt expansion by retrieving data from the Rag system and passing that data along side
        a system prompt to Gemma3:4b to expand user prompt into a more detailed prompt for analytics Engines to 
        work with.

        3. Receive the expanded prompt and set up MCP client connections to the three analytics Servers.

        4. Perform a web search on targeted sites ie. github, arxiv,stackoverflow etc and extract relevant context 
        to user prompt.

        5. Pass the web search result and expanded prompt to the Analytics Servers through the instantiated MCP clients
        
        6. Receive the results from all three analytics and pass it to Gemma3:4b to perform an aggregation and return 
        the final output result.
"""

import asyncio

from mcp_client_server.mcp_client import mcpclient
from Rag.EmbeddingsAndVectorStore import context_retrieval, EmbbeddingsAndIndexing
from ollama import chat
from ollama import ChatResponse
from Rag.websearch import web_search


#--- Function to embed User data and/or Prompt into Qdrant ---#
def ragembeddings(Prompt: str = "", Data: list =[]):

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

# --- Context Retrieval From Rag function definition ---#
def contextpromptexpansion(context_ret: dict,prompt: str):
    doc_results = context_ret.get("docs", [])
  
    # Extract from docs (text + b64 image encoding from Qdrant )
    pdf_context = [r["text"] for r in doc_results]
    base64_images = [r["img_b64"] for r in doc_results if r["img_b64"] is not None]

    #Pass context retrieved to gemma3:4b for prompt expansion
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
async def runAnalysis(prompt: str, EvalScore: str = "None"):
    # Set up MCP clients to all three MCP servers
    Theoritical_Domain = mcpclient("Theoretical")
    Structural_Domain = mcpclient("Structural")
    Logical_Domain = mcpclient("Logical")

    #Connect To MCP Servers 
    try:
        await asyncio.gather(
        Theoritical_Domain.connect_to_server("mcp_client_server/theoriticalserver.py",),
        Structural_Domain.connect_to_server("mcp_client_server/Structuralserver.py"),
        Logical_Domain.connect_to_server("mcp_client_server/logicalserver.py")
        )

    except Exception as e:
        print(f'Connection to Servers failed : status {e}')
    
    #Call MCP server Anlaytics tools with expanded Prompt and Web Search results
    result = []
    try:
       webresult = await web_search(prompt)
       result =  await asyncio.gather(
                    Theoritical_Domain.call_analysis("theoriticalServer", {"prompt": prompt, "webres":webresult,"EvlScore":EvalScore}),
                    Structural_Domain.call_analysis("structuralServer", {"prompt": prompt,"webres":webresult,"EvlScore":EvalScore}),
                    Logical_Domain.call_analysis("logicalServer", {"prompt": prompt,"webres":webresult,"EvlScore":EvalScore})
                     )
    except Exception as e:
        print(f'Something went wrong: Error Details : {e}')
        
    finally:    
        #Close all asynchronous threads after tool call finishes
        await asyncio.gather(
            Theoritical_Domain.close_async_context(),
            Structural_Domain.close_async_context(),
            Logical_Domain.close_async_context(),
            return_exceptions= True
        )


   # --- Gemma Summarizes Results --- #
    response = "" #type: ignore
    
    try:
        systemP= """
                    Merge all these Responses into One cohessive Response Stictly adhere to what is provided.
                    Your Output should be the merged Analysis only. NO Preambles or anything of that sort
                 """
        response: ChatResponse = chat(
            model='gemma3:4b',
            messages=[
                {
                    'role':'system',
                    'content': systemP
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
        return str(response.message.content).strip()
    except Exception as e:
        print("failed summarize all Analysis ")
        print(f"Error Details : {e} ")
        return


        

        



    
    
    

    