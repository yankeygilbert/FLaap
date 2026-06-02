import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from mcp.server.stdio import stdio_server
from Rag.EmbeddingsAndVectorStore import context_retrieval
from ollama import chat
from ollama import ChatResponse

server = FastMCP("theoriticalServer")

#--- Analysis Server Tool method with search grounding activated ---#
async def contextRet(prompt,web_search):
        TheoriticalExtractionQuery = """
        Represent this query for retrieving relevant academic document sections stored as metadata pages(images): 
        A research paper Abstract, Introduction, Background, Literature Review, and Discussion sections containing: 
        primary hypotheses, foundational premises, axiomatic assumptions, causal mechanisms, and conceptual frameworks. 
        This extraction must capture the core deductive reasoning, axiomatic boundaries, 
        and theoretical paradigms necessary to detect theoretical flaws, such as circular reasoning, unbacked conceptual leaps, 
        flawed premises, and invalid causal claims.
        """
        gemmaEmbInstructPfx: str = TheoriticalExtractionQuery.strip() +" User Prompt:"+ prompt
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

@server.tool(name="theoriticalServer")
async def theoriticalanalysis(prompt: str, webres:str ) :
    """Tool To Perform logical Flaw Analysis

        Args:
            prompt: A user Prompt
    """

    systemPrompt = """
        You are Theoritical Flaw Anaylsis Specialist In R&D     
        Your Job is to analyse and detection theoritical flaws in a Design Implementation
        Your role is to examine technical implementations, and identify all theoritical weaknesses.
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
        If the argument contains no flaws, state explicitly that the implementation is theoritically correct and explain why.
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

