from fastapi import FastAPI, UploadFile, HTTPException
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List
import tempfile
import logging
from langchain_community.embeddings import HuggingFaceEmbeddings
from fastapi.responses import StreamingResponse
import json
import asyncio
from langchain_google_genai import GoogleGenerativeAIEmbeddings

app = FastAPI()

# Thêm cấu hình logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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


async def save_upload_file(file: UploadFile) -> str:
    """Save uploaded file to temporary location and return path"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file.flush()
        return tmp_file.name

async def process_with_status(split_docs: List[Document]):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key="AIzaSyBS99uBPiBM5MJardfZGAgIt1W5Tc5hPtM"
    )
    total = len(split_docs)
    
    async def generate():
        for i, doc in enumerate(split_docs, 1): 
            embedding = embeddings.embed_query(doc.page_content)
            yield json.dumps({
                "status": f"Processing chunk {i}/{total}",
                "progress": round((i/total) * 100, 2),
                "embedding": embedding
            }) + "\n"
            await asyncio.sleep(0)
    
    return StreamingResponse(generate(), media_type="application/x-ndjson")

@app.post("/process-pdf/")
async def process_pdf(file: UploadFile):
    """Process PDF file and return extracted text with metadata"""
    try:
        tmp_path = await save_upload_file(file)
        
        # Process PDF
        documents = await process_pdf_with_langchain(tmp_path)
        
        # Split into chunks if needed
        chunks = await split_documents(documents)
        return await process_with_status(chunks)

    except Exception as e:
        logger.error(f"Error processing {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
