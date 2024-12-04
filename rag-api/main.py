from fastapi import FastAPI, UploadFile, HTTPException
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List
import tempfile
import os

app = FastAPI()

async def process_pdf_with_langchain(file_path: str) -> List[Document]:
    """Process PDF with Langchain's PyMuPDF loader using lazy loading"""
    loader = PyMuPDFLoader(file_path)
    
    # Use lazy_load to process documents
    documents = []
    for doc in loader.lazy_load():
        documents.append(doc)
    
    return documents

async def split_documents(documents: List[Document], 
                         chunk_size: int = 1000,
                         chunk_overlap: int = 100) -> List[Document]:
    """Split documents into smaller chunks"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    return text_splitter.split_documents(documents)

def format_response(documents: List[Document]) -> dict:
    """Format documents into API response"""
    return {
        "pages": [
            {
                "page_number": doc.metadata.get("page", 0) + 1,
                "text": doc.page_content,
                "metadata": {
                    "source": doc.metadata.get("source"),
                    "format": doc.metadata.get("format", "pdf"),
                    "total_pages": doc.metadata.get("total_pages")
                }
            }
            for doc in documents
        ],
        "metadata": {
            "total_pages": len(documents),
            "processing_status": "success"
        }
    }

async def save_upload_file(file: UploadFile) -> str:
    """Save uploaded file to temporary location and return path"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file.flush()
        return tmp_file.name

@app.post("/process-pdf/")
async def process_pdf(file: UploadFile):
    """Process PDF file and return extracted text with metadata"""
    try:
        tmp_path = await save_upload_file(file)
        
        # Process PDF
        documents = await process_pdf_with_langchain(tmp_path)
        
        # Split into chunks if needed
        split_docs = await split_documents(documents)
        
        # Format response
        response = format_response(split_docs)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
