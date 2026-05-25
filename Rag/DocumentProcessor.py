import io
import os
import base64

import pytesseract
from pdf2image import convert_from_path
from llama_index.core import Document

def custom_ocr_image_extractor(file_path: str, errors: str = "ignore") -> list[Document]:
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
                    "source_file": os.path.basename(file_path),
                    "page_number": page_num + 1,
                    "contains_image": True,
                    "full_page_image_b64": img_b64_str
                }
            )
            doc.metadata_template = "{key}: {value}"
            doc.metadata_separator = "|"
            doc.text_template = "File: {source_file} | Page: {page_number}\n\nContent:\n{content}"
            doc.excluded_embed_metadata_keys = ["full_page_image_b64"]
            doc.excluded_llm_metadata_keys = ["full_page_image_b64"]
            documents.append(doc)
    print("Conversion and Extraction Done")
            
    return documents