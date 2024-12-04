from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import io
from datetime import datetime
from utils.pdf_processor import PDFProcessor

app = FastAPI(title="PDF Processor API")

@app.post("/process-pdf/")
async def process_pdf_endpoint(file: UploadFile = File(...)):
    try:
        # Read file into memory
        contents = await file.read()
        pdf_stream = io.BytesIO(contents)
        
        # Process the PDF directly from memory
        processor = PDFProcessor(pdf_stream)
        chunks = processor.process()
        
        # Return results
        return JSONResponse(content={
            "status": "success",
            "chunks": chunks,
            "total_pages": len(chunks),
            "filename": file.filename
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root():
    return {"message": "PDF Processor API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
