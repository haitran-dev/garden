1. Tạo python virtual environment
```bash
# Tạo virtual environment
python3 -m venv .venv

# Kích hoạt virtual environment
source .venv/bin/activate

# Cập nhật pip và cài đặt các gói cần thiết
pip install --upgrade pip

pip install langchain langchain-community fastapi uvicorn pymupdf
```

2. Tạo tệp requirements.txt ghi lại các package đã dùng
```
pip freeze > requirements.txt
```

3. Update VS Code interpreter
- Press Cmd+Shift+P (Mac)
- Type "Python: Select Interpreter"
- Choose the interpreter path = `which python` 

4. Create simple endpoint with fastAPI
```python
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
```

5. Run server
```bash
fastapi dev main.py
```
