
"""
                       ---- Document Processor ----
    This Program Implements the Extraction of text and conversion of PDF Research documentation into
    Images to be stored in Qdrant.

    NB:  Only extracted text is vectorized. Image blobs are compressed using base64 enconding and stored as 
    a metadata payload in Qdrant using the Qdrant scroll api.
                
"""
import io
import os
import base64

import pytesseract
from pdf2image import convert_from_path
from llama_index.core import Document
from llama_index.core.readers.base import BaseReader

class files_extractor(BaseReader):
    def __init__(self):
        self.image_store = {} 

    def load_data(self, file_path: str, extra_info=None) -> list[Document]:
        """Callback function used by SimpleDirectoryReader to parse PDFs as images."""
        print("Converting Pages to Images and Extracting Text Content")
        pages = convert_from_path(file_path, dpi=300) # convert pdf pages to images
        documents = []

        for page_num, page_image in enumerate(pages):
            # Extract the text from images
            ocr_text = pytesseract.image_to_string(page_image)
            
            # Base64 compress the visual page image for the Qdrant Payload
            buffered = io.BytesIO()
            page_image.save(buffered, format="JPEG", quality=90)
            img_b64_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            # set Up llama Index Document append extracted text, compressed Images go to "self.image_store".
            if ocr_text.strip():
                doc = Document(
                    text=ocr_text,
                    metadata={
                        "contains_image": True,
                    },
                    excluded_embed_metadata_keys=["contains_image", "full_page_image_b64"],
                    excluded_llm_metadata_keys=["contains_image"]
                )
                self.image_store[doc.node_id] = img_b64_str
                documents.append(doc)
        print("Conversion and Extraction Done")
                
        return documents