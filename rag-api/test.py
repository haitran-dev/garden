from langchain_community.document_loaders import PyMuPDFLoader
import fitz  # This is to verify PyMuPDF is accessible
import langchain_community.document_loaders as loaders
   

def test_imports():
    print("PyMuPDF (fitz) version:", fitz.__version__)
    print(dir(loaders))
    print("Import successful!")

if __name__ == "__main__":
    test_imports() 