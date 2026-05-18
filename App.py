import asyncio

import streamlit as st
from Configuration import Test_Conncection_To_Gemini ,Test_Conncection_To_Gemma3
from Orchestration import ragembeddings,runAnalysis


st.subheader("SYSTEM STATUS")

with st.container(border= True):
    st.write("LLM & RAG Connection Test")
    st.metric(label="GeminiConnections", value=Test_Conncection_To_Gemini())
    st.metric(label="Gemma3Connection",value=Test_Conncection_To_Gemma3())

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
           async def main():
                await runAnalysis(prompt)