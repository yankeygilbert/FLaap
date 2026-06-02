import asyncio
import sys

import streamlit as st
from Configuration import Test_Connection_To_Gemma3, localResourcesShellSetup
from Orchestration import ragembeddings,runAnalysis

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
                result = asyncio.run(ragembeddings(Data=uploaded_files))
            except Exception as e:
                print(f'Error with Document upload: {e}')
            

        if not prompt:
            st.error("A prompt is required")
        
        else:
            st.subheader("Analysis Result")

            with st.container(border= True):
                result = asyncio.run(runAnalysis(prompt= prompt))  # type: ignore
                st.text(result) 

