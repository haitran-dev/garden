from typing import List, Dict, Union
from pydantic import BaseModel, Field
from PyPDF2 import PdfReader
import io

class TextChunk(BaseModel):
    """A chunk of text from the PDF, ready for LLM processing"""
    content: str = Field(..., description="The text content")
    page_number: int = Field(..., description="Source page number")
    chunk_number: int = Field(..., description="Chunk sequence number")
    metadata: Dict = Field(default_factory=dict, description="Additional chunk metadata")

class ProcessedDocument(BaseModel):
    """Processed PDF document with chunks ready for LLM"""
    chunks: List[TextChunk] = Field(..., description="List of text chunks")
    total_pages: int = Field(..., description="Total number of pages")
    total_chunks: int = Field(..., description="Total number of chunks")
    metadata: Dict = Field(default_factory=dict, description="Document metadata")

class PDFProcessor:
    def __init__(self, source: Union[str, io.BytesIO], chunk_size: int = 1000):
        self.chunk_size = chunk_size
        self.source = source

    def process_pdf(self) -> ProcessedDocument:
        # Open PDF
        reader = PdfReader(self.source)
        chunks = []
        chunk_number = 0

        # Process each page
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text()
            
            # Create chunks from page text
            page_chunks = self._create_chunks(text, self.chunk_size)
            
            # Create TextChunk objects
            for chunk in page_chunks:
                chunks.append(TextChunk(
                    content=chunk,
                    page_number=page_num + 1,
                    chunk_number=chunk_number,
                    metadata={
                        "source_page": page_num + 1,
                        "length": len(chunk)
                    }
                ))
                chunk_number += 1

        return ProcessedDocument(
            chunks=chunks,
            total_pages=len(reader.pages),
            total_chunks=len(chunks),
            metadata=reader.metadata if hasattr(reader, 'metadata') else {}
        )

    def _create_chunks(self, text: str, chunk_size: int) -> List[str]:
        chunks = []
        current_chunk = []
        current_size = 0
        
        # Split by sentences to preserve context
        sentences = text.split('.')
        
        for sentence in sentences:
            sentence = sentence.strip() + '.'
            sentence_size = len(sentence)
            
            if current_size + sentence_size > chunk_size and current_chunk:
                # Save current chunk
                chunks.append(''.join(current_chunk))
                current_chunk = []
                current_size = 0
            
            current_chunk.append(sentence)
            current_size += sentence_size
        
        # Add any remaining text
        if current_chunk:
            chunks.append(''.join(current_chunk))
        
        return chunks
