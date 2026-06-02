import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from Configuration import client1
from mcp.server.stdio import stdio_server
from google.genai import types
from Rag.EmbeddingsAndVectorStore import context_retrieval

server = FastMCP("structuralServer")

#--- Analysis Server Tool method with search grounding activated ---#
def contextRet(prompt):
        structuralExtractionQuery = """
            Represent this query for retrieving relevant Research document sections stored as metadata pages(images): 
            A research paper Abstract, Introduction, Methodology, and Experimental Design sections containing: study architectures, 
            sampling strategies, variable operationalisation, control frameworks, and procedural steps. 
            This extraction must capture the organizational logic, workflow boundaries, 
            and data collection protocols necessary to detect structural flaws, 
            such as missing control groups, variables left unmeasured, data collection gaps, and systemic design-to-hypothesis mismatches
            """
         
        gemmaEmbInstructPfx: str = structuralExtractionQuery.strip() +" User Prompt:"+prompt
        context_ret = context_retrieval(query_docs= gemmaEmbInstructPfx)
        
        doc_results = context_ret.get("docs", [])
        memory_results = context_ret.get("memory", [])

        # Extract from docs (text + b64 from Qdrant scroll)
        pdf_context = [r["text"] for r in doc_results]
        base64_images = [r["img_b64"] for r in doc_results if r["img_b64"] is not None]

        # Extract from memory
        memory_context = [r["text"] for r in memory_results]

        content = [ f"""
                ### User Query ###
                {prompt}   
                
                ###PDF TEXT CONTENT :###
                {pdf_context}

                ###Memory context :##
                {memory_context}

                ### Base64 Encoded Page Images: ###
                {base64_images}
            """
        ]

        return content


@server.tool(name= "structuralServer")
async def StructuralAnalysis(prompt: str) :
    """Tool To Perform logical Flaw Analysis

        Args:
            prompt: A user Prompt
    """

    systemPrompt = """
        You are Structural Flaw Anaylsis Specialist In R&D     
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
    
    contents = contextRet(prompt)
    try:
        grounding_tool = types.Tool(
                google_search = types.GoogleSearch()
            )

        config = types.GenerateContentConfig(
            tools = [grounding_tool],
            system_instruction = systemPrompt    
            )

        response = client1.models.generate_content(
                model= "gemini-3-flash-preview",
                contents= contents, # type: ignore   
                config = config  
            )

        return response.text
    except Exception as e:
        return print(f'Response Error', file=sys.stderr)

def main():
    server.run(transport= "stdio") 

if __name__ == "__main__":
    main()

