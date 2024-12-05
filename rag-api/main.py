from fastapi import FastAPI, UploadFile, HTTPException, Query
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List, Optional
import tempfile
import logging
from langchain_community.embeddings import HuggingFaceEmbeddings
from fastapi.responses import StreamingResponse
import json
import asyncio
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
import os

app = FastAPI()

# Load environment variables
load_dotenv()

class VectorStore:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    
    def get_db(self, collection_name: str) -> Chroma:
        return Chroma(
            collection_name=collection_name,
            persist_directory="./chroma_db",
            embedding_function=self.embeddings
        )

# Khởi tạo global instance
vector_store = VectorStore()

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

async def process_with_status(split_docs: List[Document], collection_name: str):
    total = len(split_docs)
    processed_docs = []
    
    # Sử dụng global vector_store
    vectordb = vector_store.get_db(collection_name)  # Hoặc truyền collection_name vào function
    
    async def generate():
        for i, doc in enumerate(split_docs, 1):
            try:
                processed_docs.append(doc)
                
                if len(processed_docs) >= 10 or i == total:
                    vectordb.add_documents(processed_docs)
                    vectordb.persist()
                    processed_docs.clear()
                
                yield json.dumps({
                    "status": f"Processed and stored chunk {i}/{total}",
                    "progress": round((i/total) * 100, 2)
                }) + "\n"
                
            except Exception as e:
                yield json.dumps({
                    "error": f"Error at chunk {i}: {str(e)}"
                }) + "\n"
            
            await asyncio.sleep(0)
    
    return StreamingResponse(generate(), media_type="application/x-ndjson")

@app.post("/load-pdf/")
async def load_pdf(
    file: UploadFile,
):
    """Process PDF file and return extracted text with metadata"""
    try:
        tmp_path = await save_upload_file(file)
        
        # Process PDF
        documents = await process_pdf_with_langchain(tmp_path)
        
        # Split into chunks
        chunks = await split_documents(documents)
        
        # Process và lưu vào collection được chỉ định
        return chunks
    except Exception as e:
        logger.error(f"Error processing {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-pdf/")
async def process_pdf(
    file: UploadFile,
    collection_name: str = Query(..., description="Name of the collection to store embeddings")
):
    """Process PDF file and return extracted text with metadata"""
    try:
        tmp_path = await save_upload_file(file)
        
        # Process PDF
        documents = await process_pdf_with_langchain(tmp_path)
        
        # Split into chunks
        chunks = await split_documents(documents)
        
        # Process và lưu vào collection được chỉ định
        return await process_with_status(chunks, collection_name)

    except Exception as e:
        logger.error(f"Error processing {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Sử dụng trong endpoints
@app.post("/search-chunks")
async def search_chunks(
    query: str,
    collection_name: str,
):
    try:
        vectordb = vector_store.get_db(collection_name)
        
        # Tạo retriever từ vectordb
        retriever = vectordb.as_retriever(
            search_type="similarity"
        )
        
        # Lấy relevant documents
        docs = retriever.invoke(query)
        
        return {
            "query": query,
            "collection": collection_name,
            "chunks": [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in docs
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
