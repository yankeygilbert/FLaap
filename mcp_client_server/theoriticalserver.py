import asyncio
import sys

from mcp.server.fastmcp import FastMCP
from Configuration import client1
from mcp.server.stdio import stdio_server
from google.genai import types

server = FastMCP("theoriticalServer")

#--- Analysis Server Tool method with search grounding activated ---#
@server.tool(name="theoriticalServer")
async def logicalanalysis(args: dict ) :
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
        A research paper Abstract, Introduction, Background, Literature Review, and Discussion sections containing: 
        primary hypotheses, foundational premises, axiomatic assumptions, causal mechanisms, and conceptual frameworks. 
        This extraction must capture the core deductive reasoning, axiomatic boundaries, 
        and theoretical paradigms necessary to detect theoretical flaws, such as circular reasoning, unbacked conceptual leaps, 
        flawed premises, and invalid causal claims.
        """

    grounding_tool = types.Tool(
            google_search = types.GoogleSearch()
        )

    config = types.GenerateContentConfig(
        tools = [grounding_tool],
        system_instruction = systemPrompt    
        )

    response = client1.models.generate_content(
            model= "gemini-3-flash-preview",
            contents= query,    
            config = config  
        )

    return response.text

if __name__ == "__main__":
    server.run(transport= "stdio")
