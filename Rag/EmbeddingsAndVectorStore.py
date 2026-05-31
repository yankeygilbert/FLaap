import ollama
import io
import base64
import tempfile
import os
import qdrant_client
import fitz

from llama_index.core import VectorStoreIndex, Settings, StorageContext, SimpleDirectoryReader
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.schema import TextNode
from llama_index.vector_stores.qdrant import QdrantVectorStore
from  Rag.DocumentProcessor import custom_ocr_image_extractor

# --- Ollama embeddings configuration ---
ollama_embeddings= OllamaEmbedding(
    model_name= "embeddinggemma:latest",
    base_url= "http://localhost:11434",
    ollama_additional_kwargs= {"context_length": 2000}
)

# --- Bind to LlamaIndex global settings ---
Settings.embed_model = ollama_embeddings
Settings.text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)

# --- Qdrant client ---
QDrant_Client = qdrant_client.QdrantClient(host="localhost", port=6333)

#--- Embeddings and Indexing Function---
def EmbbeddingsAndIndexing(prompt: str="", data: list=[], ):

    index = None

    if not prompt and not data:
        print("Nothing to embed — provide a prompt or data")
        return

    # --- Embed user prompt & AI respsonses  ---
    # --- Memory Simulation ----
    if prompt:
        try:
            print("DEBUG 1: creating vector store")
            Vec_Store = QdrantVectorStore(
                collection_name="PromptandResponse",
                client= QDrant_Client,
            )
            print("DEBUG 2: vector store created")
            stg_context = StorageContext.from_defaults(vector_store=Vec_Store)
            print("DEBUG 3: storage context created")
            prompt_doc = Document(text=prompt)
            print("DEBUG 4: document created")
            index = VectorStoreIndex.from_documents(
                [prompt_doc],
                storage_context=stg_context
            )
            print("DEBUG 5: Memory indexing complete")
        except Exception as e:
            print(f"Prompt embedding failed: {e}")
            import traceback
            traceback.print_exc()  # prints full error stack
            
    # --- Embed attached PDF documents ---
    if data:
        try:
            Vec_Store = QdrantVectorStore(
                collection_name="ResearchDocumentation",
                client=QDrant_Client
            )
            stg_context = StorageContext.from_defaults(vector_store=Vec_Store)
           
            with tempfile.TemporaryDirectory() as temp_dir_path:
                for file_contents in data:
                    filename= file_contents.name
                    filebytes= file_contents.getvalue()

                    file_temp_targetpath= os.path.join(temp_dir_path,file_contents.name)

                    with open(file_temp_targetpath, 'wb') as pdf_file:
                        pdf_file.write(filebytes)

                file_extractor = {".pdf": custom_ocr_image_extractor} 
                reader = SimpleDirectoryReader(
                    input_dir= temp_dir_path,
                    file_extractor= file_extractor #type: ignore 
                  
                )
                
                pdf_documents= reader.load_data()

            

            index = VectorStoreIndex.from_documents(
                pdf_documents,
                storage_context=stg_context
            )
            print("Documents vectorized and indexed into Qdrant")
        except Exception as e:
            print(f"Document embedding failed: {e}")

    if index:
        print("Vectorized and indexed into Qdrant using Ollama Gemma embeddings")
    else:
        print("Something went wrong — index was not created")

# --- Context Retrieveal ---
# Implemented For Memory query and Context Data for Analytics agents Query.
def context_retrieval(query_memory: str= "", query_Docs: str= ""):
    response = None
    index = None

    if not query_memory and not query_Docs:
        print("No inference Prompt provided to retrieve ")
        return

    if query_memory:
        vec_store = QdrantVectorStore(
        collection_name= "PromptandResponse",
        client=  QDrant_Client
        )

        index= VectorStoreIndex.from_vector_store(vector_store= vec_store)
        
        response= index.as_retriever(similarity_top_k = 2 )
        nodes = response.retrieve(query_Docs)

        return nodes
    
    if query_Docs:
        vec_store =QdrantVectorStore(
            collection_name= "ResearchDocumentation",
            client= QDrant_Client
        )

        index= VectorStoreIndex.from_vector_store(vector_store= vec_store)
        response= index.as_retriever(similarity_top_k = 2 )
        nodes = response.retrieve(query_Docs)

        return nodes

