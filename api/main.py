from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import shutil
import os
from typing import List, Dict
import uvicorn
from datetime import datetime
from utils.pdf_processor import PDFProcessor
import platform
from pathlib import Path

app = FastAPI(title="PDF Processor API")

# Create upload directory if it doesn't exist
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/process-pdf/")
async def process_pdf_endpoint(file: UploadFile = File(...)):
    try:
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Process the PDF
        processor = PDFProcessor(file_path)
        output_dir = os.path.join(OUTPUT_DIR, timestamp)
        os.makedirs(output_dir, exist_ok=True)
        
        chunks = processor.process(output_dir=output_dir)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        # Return results
        return JSONResponse(content={
            "status": "success",
            "chunks": chunks,
            "total_chunks": len(chunks),
            "output_directory": output_dir
        })
        
    except Exception as e:
        # Clean up in case of error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root():
    return {"message": "PDF Processor API is running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
