import typing
import ollama
import io
import tempfile
import os

from llama_index.core import VectorStoreIndex, Settings, StorageContext
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.readers.file import PDFReader
import qdrant_client
from llama_index.vector_stores.qdrant import QdrantVectorStore

# Ollama embeddings configuration
ollama_embeddings = OllamaEmbedding(
    model_name="embeddinggemma:latest",
    base_url="http://localhost:11434",
    ollama_additional_kwargs={"context_length": 2000}
)

# Bind to LlamaIndex global settings
Settings.embed_model = ollama_embeddings
Settings.text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)

# Qdrant client
QDrant_Client = qdrant_client.QdrantClient(host="localhost", port=6333)


def EmbbeddingsAndIndexing(prompt: str = None, data: list[io.BytesIO] = None):

    index = None

    if not prompt and not data:
        print("Nothing to embed — provide a prompt or data")
        return

    # --- Embed user prompt ---
   
    # Add this temporarily to EmbeddingsAndVectorStore.py inside the prompt try block

    if prompt:
        try:
            print("DEBUG 1: creating vector store")
            Vec_Store = QdrantVectorStore(
                collection_name="PromptandResponse",
                client=QDrant_Client,
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
            print("DEBUG 5: indexing complete")
        except Exception as e:
            print(f"Prompt embedding failed: {e}")
            import traceback
            traceback.print_exc()  # prints full error stack
    # --- Embed attached PDF documents ---
    if data:
        try:
            Vec_Store = QdrantVectorStore(
                collection_name="ResearchDocumentation",
                client=QDrant_Client,
            )
            stg_context = StorageContext.from_defaults(vector_store=Vec_Store)
            reader = PDFReader()
            all_documents = []

            for file_contents in data:
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                    tmp.write(file_contents.read())
                    tmp_path = tmp.name

                file_docs = reader.load_data(
                    file=tmp_path,
                    extra_info={"file_name": getattr(file_contents, "name", "unknown")}
                )
                all_documents.extend(file_docs)
                os.unlink(tmp_path)

            index = VectorStoreIndex.from_documents(
                all_documents,
                storage_context=stg_context
            )
            print("Documents vectorized and indexed into Qdrant")
        except Exception as e:
            print(f"Document embedding failed: {e}")

    if index:
        print("Vectorized and indexed into Qdrant using Ollama Gemma embeddings")
    else:
        print("Something went wrong — index was not created")
