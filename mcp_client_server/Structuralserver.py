import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from mcp.server.stdio import stdio_server
from Rag.EmbeddingsAndVectorStore import context_retrieval
from ollama import chat
from ollama import ChatResponse


server = FastMCP("structuralServer")

#--- Analysis Server Tool method with search grounding activated ---#
async def contextRet(prompt,web_search):
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

        content = f"""
                ### User Query ###
                {prompt}   

                ### Web Search Results ###
                {web_search}
                
                ###PDF TEXT CONTENT :###
                {pdf_context}

                ###Memory context :##
                {memory_context}

                ### Base64 Encoded Page Images: ###
                {base64_images}
            """
        

        return content


@server.tool(name= "structuralServer")
async def StructuralAnalysis(prompt: str, webres:str) :
    """Tool To Perform logical Flaw Analysis

        Args:
            prompt: A user Prompt
    """

    systemPrompt = """
                You are a Structural Analysis Specialist in R&D.

                Your job is to analyse the structure of a design implementation.
                Focus on how the implementation is organised, connected, sequenced, and operationalised.

                You must check for:
                - Missing design components
                - Poor workflow sequence
                - Unclear dependencies
                - Weak architecture
                - Incomplete methodology steps
                - Missing control variables
                - Poor variable operationalisation
                - Inconsistent implementation structure
                - Missing procedural details

                For every structural issue you detect, you must:
                1. Name the structural issue
                2. Quote the exact part of the implementation that contains it
                3. Explain why it weakens the implementation
                4. Suggest how the structure could be improved

                Do not analyse logical reasoning flaws unless they directly affect the implementation structure.

                Your output format must be:
                1. Summary of structural quality
                2. Detected structural issues
                3. Explanation of each issue
                4. Suggested corrections

                If the implementation has no structural issues, state clearly that the implementation is structurally sound and explain why.
                """
        
        
    
    

    contents = await contextRet(prompt,webres)  

    try:
        response: ChatResponse = chat(
        model='gemma3:4b',
        messages=[
            {
                'role':'system',
                'content': systemPrompt
            },

            {
                'role': 'user',
                'content': contents
  
                }
            ]
        )
        result = response.message.content
        return str(result).strip()
    
    except Exception as e:
        sys.stderr.write(f"Something went Wrong : {e}")


def main():
    server.run(transport= "stdio") 

if __name__ == "__main__":
    main()
