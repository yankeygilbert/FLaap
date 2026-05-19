import asyncio

import streamlit as st
from Configuration import Test_All_Gemini_Connection, Test_Conncection_To_Gemma3
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

with st.spinner("Connecting to LLMS"):
    GeminiConnetions = asyncio.run(Test_All_Gemini_Connection())
    GemmaConnection = Test_Conncection_To_Gemma3()
   
st.subheader("SYSTEM STATUS")

with st.container(border= True):
    st.write("LLM & RAG Connection Test")
    st.metric(label="Gemini1 Status:", value=GeminiConnetions[0]) # type: ignore
    st.metric(label="Gemini2 Status", value=GeminiConnetions[1]) # type: ignore
    st.metric(label="Gemini3 Status", value=GeminiConnetions[2]) # type: ignore
    st.metric(label="Gemma3:4b Status",value=GemmaConnection) # type: ignore

with st.form("Analysis Tool"):
    prompt = st.text_input("Prompt")

    uploaded_files = st.file_uploader(
        label= "upload Documentation",
        type ="pdf",
        accept_multiple_files= True
    )
    submitted = st.form_submit_button("Analyze")
    if submitted:
        if uploaded_files:
            ragembeddings(Data=uploaded_files)

        if not prompt:
            st.error("A prompt is required")
        
        else:
            st.subheader("Analysis Result")
            async def main():
                    return await runAnalysis(prompt)

            with st.container(border= True):
                result = asyncio.run(main())  # type: ignore
                st.text(result) 

