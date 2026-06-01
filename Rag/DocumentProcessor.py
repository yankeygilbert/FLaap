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
        pages = convert_from_path(file_path, dpi=300)
        documents = []

        for page_num, page_image in enumerate(pages):
            # OCR the text
            ocr_text = pytesseract.image_to_string(page_image)
            
            # Base64 compress the visual page image for the Qdrant Payload
            buffered = io.BytesIO()
            page_image.save(buffered, format="JPEG", quality=90)
            img_b64_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            if ocr_text.strip():
                doc = Document(
                    text=ocr_text,
                    metadata={
                        "contains_image": True,
                        "full_page_image_b64": img_b64_str
                    },
                    excluded_embed_metadata_keys=["contains_image", "full_page_image_b64"],
                    excluded_llm_metadata_keys=["contains_image"]
                )
                self.image_store[doc.doc_id] = img_b64_str
                documents.append(doc)
        print("Conversion and Extraction Done")
                
        return documents