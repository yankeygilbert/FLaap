"""
    App.py is the entry point for the For the Application using streamlit
    Stages:
        1. Setting up configurations :
            Local dependecies ie. Ollama running gemmaembeddings, Gemma3:4b, docker, Qdrant  is configured and span up. 
            configuration script can be found in "shellScriptConfig.zsh"
        2. Running Orchestrator:
            Managements Rag System and communication between Rag and LLM and MCP servers is handled by the Orchestrator Engine
            The orchestrator runs three MCP clients that connects to all MCP servers and also coordinates processes between Rag system
            an all other components of the entire architecture.
          
"""
import asyncio
import sys

import streamlit as st
from Configuration import Test_Connection_To_Gemma3, localResourcesShellSetup
from Orchestration import ragembeddings,runAnalysis,promptexpansion
from Evaluation import Evaluation

st.markdown(
    '''
    <style>
            [data-testid="stMetricValue"] {
        font-size: 20px !important;
        font-family: 'Courier New', monospace !important;
    }
    </style>
    ''',
    unsafe_allow_html= True
)

with st.form("Analysis Tool"):
    prompt = st.text_input("Prompt")

    uploaded_files = st.file_uploader(
        label= "upload Documentation",
        type ="pdf",
        accept_multiple_files= True
    )
    submitted = st.form_submit_button("Analyze")
    if submitted:
        with st.spinner("Connecting to LLMS"):
            localResourcesShellSetup()
            GemmaConnection = Test_Connection_To_Gemma3()
   
        st.subheader("SYSTEM STATUS")

        with st.container(border= True):
            st.write("LLM & RAG Connection Test")
            st.metric(label="Gemma3:4b Status",value=GemmaConnection) # type: ignore

        if uploaded_files:
            try:
                with st.spinner("Processing And Embedding Data"):
                    result = asyncio.run(ragembeddings(Data=uploaded_files))
            except Exception as e:
                print(f'Error with Document upload: {e}')
            

        if not prompt:
            st.error("A prompt is required")
        
        else:
            st.subheader("Analysis Result")

            with st.container(border= True):
                with st.spinner("Running Analytics"):
                    
                    exPrompt = promptexpansion(prompt) # Call Prompt expansion Implementation Function
                    print(f'Expanded Prompt: \n {exPrompt} \n')

                    result = asyncio.run(runAnalysis(prompt= exPrompt))  # type: ignore
                    evl_result = Evaluation(result, exPrompt) # type: ignore
                    
                    if evl_result >= 7:
                        st.text(result)
                        await ragembeddings(Prompt= response.message.content)#type: ignore
                    else:
                       result = asyncio.run(runAnalysis(prompt= prompt))    
                       st.text(result)
                       await ragembeddings(Prompt= response.message.content)#type: ignore
                     

