"""Tool To Perform logical Flaw Analysis

        Args:
            prompt: A user Prompt and web search results
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from ddgs import DDGS
from mcp.server.stdio import stdio_server
from Rag.EmbeddingsAndVectorStore import context_retrieval
from ollama import chat
from ollama import ChatResponse

server = FastMCP("logicalServer")

#--- Analysis Server Tool method with search grounding activated ---#
 
async def contextRet(prompt: str, webres: str, EvlScore: str):
        logicalExtractionQuery = """
        Represent this query for retrieving relevant academic document sections stored as metadata pages(images): 
        A research paper Implementation, Results, Discussion, Evaluation,
        or Findings sections containing: experimental setups, software tools, data collection, and procedural frameworks; 
        participant demographics and sample sizes; and statistical analyses, mathematical models, or performance metrics. 
        This extraction must capture the empirical boundaries, metric definitions, 
        and intermediate data outcomes necessary to cross-examine experimental execution against
        stated hypotheses and detect logical flaws, contradictions, or overgeneralisations
        """
        gemmaEmbInstructPfx: str = logicalExtractionQuery.strip() + " User Prompt: "+ prompt
        context_ret = context_retrieval(query_docs= gemmaEmbInstructPfx)
        
        doc_results = context_ret.get("docs", [])
        memory_results = context_ret.get("memory", [])

        # Extract from docs (text + b64 from Qdrant scroll)
        pdf_context = [r["text"] for r in doc_results]
        base64_images = [r["img_b64"] for r in doc_results if r["img_b64"] is not None]

        # Extract from memory
        memory_context = [r["text"] for r in memory_results]

        content =  f"""
                ###Analytics Evaluation Score: IF "None" means Generate First original Analytics, IF < 7 means Improve Previous Analytics to meet users request###
                Evaluation Score: {EvlScore}
                ### User Query ###
                {prompt}   
                
                ### Web Search Results ###
                {webres}

                ###PDF TEXT CONTENT :###
                {pdf_context}

                ###Memory context :###
                {memory_context}

                ### Base64 Encoded Page Images: ###
                {base64_images}
            """
        
        return content

#--- MCP Server TooL ---#
@server.tool(name= "logicalServer")
async def logicalanalysis(prompt: str, webres: str, EvlScore: str) :

    """Tool To Perform logical Flaw Analysis

        Args:
            prompt: A user Prompt
    """

    systemPrompt = """
            You are a Logical Flaw Analysis Specialist in R&D.

            Your job is to analyse the reasoning quality of a design implementation.
            Focus only on logical consistency, argument quality, assumptions, conclusions, and reasoning gaps.

            You must check for:
            - Explicit contradictions
            - Implicit contradictions
            - Invalid inferences
            - Ambiguity or vagueness
            - Category errors
            - False equivalences
            - Missing premises
            - Overgeneralisation
            - Non sequitur reasoning
            - Unsupported conclusions

            For every logical flaw you detect, you must:
            1. Name the logical flaw
            2. Quote the exact part of the implementation that contains it
            3. Explain why it is a flaw
            4. Suggest how the reasoning could be corrected

            Do not analyse structure, workflow, or architecture unless they create a logical flaw.

            Your output format must be:
            1. Summary of overall reasoning quality
            2. Detected logical flaws
            3. Explanation of each flaw
            4. Suggested corrections

            If the argument contains no logical flaws, state clearly that the implementation is logically correct and explain why.
            """
    
    contents = await contextRet(prompt,webres,EvlScore)  

    # Call to Gemma to Reason on context and Prompt
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
