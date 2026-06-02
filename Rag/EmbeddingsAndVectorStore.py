import ollama
import io
import base64
import tempfile
import os
import qdrant_client
import fitz

from llama_index.core import VectorStoreIndex, Settings, StorageContext, SimpleDirectoryReader
from llama_index.core import Document
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from  Rag.DocumentProcessor import files_extractor
from qdrant_client.models import Filter, FieldCondition, MatchValue

# --- Ollama embeddings configuration ---
ollama_embeddings= OllamaEmbedding(
    model_name= "embeddinggemma:latest",
    base_url= "http://localhost:11434",
    ollama_additional_kwargs= {"context_length": 2000}
)

# --- Bind to LlamaIndex global settings ---
Settings.embed_model = ollama_embeddings

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
            extractor = files_extractor()
           
            with tempfile.TemporaryDirectory() as temp_dir_path:
                for file_contents in data:
                    filename= file_contents.name
                    filebytes= file_contents.getvalue()

                    file_temp_targetpath= os.path.join(temp_dir_path,filename)

                    with open(file_temp_targetpath, 'wb') as pdf_file:
                        pdf_file.write(filebytes)

                file_extractor = {".pdf": files_extractor()} 

                reader = SimpleDirectoryReader(
                    input_dir= temp_dir_path,
                    file_extractor= file_extractor #type: ignore  
                )
                
                pdf_documents= reader.load_data()

            if pdf_documents:
                index = VectorStoreIndex.from_documents(
                    pdf_documents,
                    storage_context=stg_context,
                    insert_batch_size=1    
                )
                print("Documents vectorized and indexed into Qdrant")

                # Upsert b64 into Qdrant payload after indexing
                for doc_id, img_b64 in extractor.image_store.items():
                    QDrant_Client.set_payload(
                        collection_name="ResearchDocumentation",
                        payload={"full_page_image_b64": img_b64},
                        points=Filter(
                            must=[FieldCondition(
                                key="doc_id",
                                match=MatchValue(value=doc_id)
                            )]
                        )
                    )
            else:
                print(f"Document embedding failed")
        except Exception as e:
            print(f"Document embedding failed: {e}")

# --- Context Retrieveal ---
# Implemented For Memory query and Context Data for Analytics agents Query.
def context_retrieval(query_memory: str = "", query_docs: str = ""):
    results = {}

    if not query_memory and not query_docs:
        print("No inference prompt provided to retrieve")
        return results

    if query_memory:
        vec_store = QdrantVectorStore(
            collection_name="PromptandResponse",
            client=QDrant_Client
        )
        index = VectorStoreIndex.from_vector_store(vector_store=vec_store)
        nodes = index.as_retriever(similarity_top_k=2).retrieve(query_memory) 
        results["memory"] = [
            {"score": n.score, "text": n.node.get_content()} for n in nodes
        ]

    if query_docs:
        vec_store = QdrantVectorStore(
            collection_name="ResearchDocumentation",
            client=QDrant_Client
        )
        index = VectorStoreIndex.from_vector_store(vector_store=vec_store)
        nodes = index.as_retriever(similarity_top_k=2).retrieve(query_docs)

        doc_results = []
        for node in nodes:
            node_id = node.node.node_id
            points, _ = QDrant_Client.scroll(
                collection_name="ResearchDocumentation",
                scroll_filter=Filter(
                    must=[FieldCondition(
                        key="doc_id",
                        match=MatchValue(value=node_id)
                    )]
                ),
                with_payload=True,
                limit=1
            )
            img_b64 = None
            if points and points[0].payload:
                img_b64 = points[0].payload.get("full_page_image_b64")
            doc_results.append({
                "score": node.score,
                "text": node.node.get_content(),
                "img_b64": img_b64
            })

        results["docs"] = doc_results

    return results

