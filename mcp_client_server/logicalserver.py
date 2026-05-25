import asyncio
import sys

from mcp.server.fastmcp import FastMCP
from Configuration import client1
from mcp.server.stdio import stdio_server
from google.genai import types
from Rag.EmbeddingsAndVectorStore import context_retrieval

server = FastMCP("logicalServer")

#--- Analysis Server Tool method with search grounding activated ---#
@server.tool(name= "logicalServer")
async def logicalanalysis(args: dict ) :
    """Tool To Perform logical Flaw Analysis

        Args:
            prompt: A user Prompt
    """

    systemPrompt = """
        You are logical Flaw Anaylsis Specialist In R&D     
        Your Job is to analyse and detection logical flaws in a Design Implementation
        Your role is to examine technical implementations, and identify all logical weaknesses.
        Your analysis must include:
        Explicit contradictions
        Implicit contradictions
        Invalid inferences
        Ambiguity or vagueness
        Category errors
        False equivalences
        Missing premises
        Overgeneralisation
        Nonsequitur reasoning
        For every flaw you detect, you must:
        Name the flaw
        Quote the exact part of the implementation that contains it
        Explain why it is a flaw
        Suggest how the reasoning could be corrected
        You must be precise, rigorous, and exhaustive.
        You do not rewrite the argument; you only analyse it.
        You do not soften your critique; you prioritise correctness over politeness.
        Your output format must be:
        1. Summary of overall reasoning quality  
        2. detected flaws  
        3. Explanation of each flaw  
        4. Suggested corrections
        If the argument contains no flaws, state explicitly that the implementation is logically correct and explain why.
        """
   
    query = args["prompt"]

    logicalExtractionQuery = """
        Represent this query for retrieving relevant academic document sections stored as metadata pages(images): 
        A research paper Implementation, Results, Discussion, Evaluation,
        or Findings sections containing: experimental setups, software tools, data collection, and procedural frameworks; 
        participant demographics and sample sizes; and statistical analyses, mathematical models, or performance metrics. 
        This extraction must capture the empirical boundaries, metric definitions, 
        and intermediate data outcomes necessary to cross-examine experimental execution against
        stated hypotheses and detect logical flaws, contradictions, or overgeneralisations
        """
    
    async def contextRet(prompt):

        gemmaEmbInstructPfx: str = logicalExtractionQuery.strip() + " User Prompt: "+ prompt
        contextret = context_retrieval(query_Docs= gemmaEmbInstructPfx)
        
        pdf_context= [context.node.text for context in contextret]# type:ignore
        page_num = [context.node.metadata.get("page_number") for context in contextret]# type:ignore
        base64imgEncoding =[context.node.get("full_page_image_b64") for context in contextret] # type:ignore
        source_file = [context.node.metadata.get("source_file") for context in contextret]# type:ignore

        content = [ f"""
                ### User Query ###
                {query}   
                Sourcefiles : {source_file} | Page Numbers : {page_num}
                ###PDF TEXT CONTENT :###
                {pdf_context}
                
                ### Base64 Encoded Page Images: ###
                {base64imgEncoding}
            """
        ]

        return content

    content = await contextRet(query)    

    grounding_tool = types.Tool(
            google_search = types.GoogleSearch()
        )

    config = types.GenerateContentConfig(
        tools = [grounding_tool],
        system_instruction = systemPrompt    
        )

    response = client1.models.generate_content(
            model= "gemini-3-flash-preview",
            contents= content, # type: ignore   
            config = config  
        )

    return response.text

if __name__ == "__main__":
    server.run(transport= "stdio")
