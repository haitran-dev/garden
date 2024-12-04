from fastapi import FastAPI, UploadFile, File, HTTPException
import io
from services.pdf_processor import PDFProcessor

app = FastAPI(title="PDF Processor API")

@app.post("/process-pdf/")
async def process_pdf_endpoint(file: UploadFile = File(...)):
    try:
        # Read file into memory
        contents = await file.read()
        pdf_stream = io.BytesIO(contents)
        
        # Process the PDF directly from memory
        processor = PDFProcessor(pdf_stream)
        result = processor.process_pdf()
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root():
    return {"message": "PDF Processor API is running"}